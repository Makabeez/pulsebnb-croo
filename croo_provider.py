"""
PulseBNB CROO Agent — paid, callable contract-intelligence agent on CROO CAP.

Wraps the existing PulseBNB AI classifier as a CROO Agent Protocol service.
A requester pays USDC, sends ANY BNB contract address, and receives a structured
verdict: real builder vs noise, with a reason and a 0-100 confidence score.

On-demand: classifies any address live (even brand-new deploys not yet indexed),
reusing the exact PulseBNB classifier brain (ai_classifier.classify_with_ai).
"""

import asyncio
import json
import logging
import os
import signal
import sys

import httpx

# Reuse the REAL PulseBNB classifier (same prompt/model the dashboard uses).
sys.path.insert(0, os.environ.get("PULSEBNB_DIR", "/home/vps/pulsebnb"))
from ai_classifier import classify_with_ai  # noqa: E402

from croo import (  # noqa: E402
    AgentClient,
    Config,
    EventType,
    DeliverableType,
    DeliverOrderRequest,
    Event,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
log = logging.getLogger("pulsebnb-croo")

ETHERSCAN_KEY = os.environ.get("ETHERSCAN_API_KEY", "")
BSC_RPC = os.environ.get("BSC_RPC_URL", "https://bsc-dataseed.binance.org")

# ERC interface selectors for lightweight type detection from bytecode.
ERC20_SELECTORS = {"a9059cbb", "70a08231", "18160ddd", "dd62ed3e", "095ea7b3"}
ERC721_SELECTORS = {"6352211e", "42842e0e", "b88d4fde"}
ERC1155_SELECTORS = {"f242432a", "2eb2c2d6", "4e1273f4"}


def _extract_address(requirements: str) -> str | None:
    """Pull a BNB contract address from the caller's requirements string."""
    if not requirements:
        return None
    requirements = requirements.strip()
    try:
        obj = json.loads(requirements)
        if isinstance(obj, dict):
            addr = obj.get("address") or obj.get("contract") or obj.get("target")
            if addr:
                requirements = str(addr).strip()
    except (json.JSONDecodeError, TypeError):
        pass
    if requirements.startswith("0x") and len(requirements) == 42:
        return requirements
    return None


def _detect_type(bytecode_hex: str) -> str:
    """Rough ERC type detection from runtime bytecode function selectors."""
    code = bytecode_hex.lower()
    has = lambda sels: sum(1 for s in sels if s in code) >= 2  # noqa: E731
    if has(ERC1155_SELECTORS):
        return "ERC1155"
    if has(ERC721_SELECTORS):
        return "ERC721"
    if has(ERC20_SELECTORS):
        return "ERC20"
    return "OTHER"


async def _fetch_contract_facts(address: str) -> dict | None:
    """Gather {contract_type, verified, contract_name} for any BNB address.

    Returns None if the address has no contract code (an EOA).
    """
    async with httpx.AsyncClient(timeout=20.0) as http:
        # 1. runtime bytecode via RPC -> type detection + contract existence
        rpc_resp = await http.post(
            BSC_RPC,
            json={
                "jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                "params": [address, "latest"],
            },
        )
        code = rpc_resp.json().get("result", "0x")
        if not code or code == "0x":
            return None  # not a contract
        contract_type = _detect_type(code)

        # 2. name + verification via Etherscan V2 (chainid=56)
        name, verified = None, False
        if ETHERSCAN_KEY:
            try:
                es = await http.get(
                    "https://api.etherscan.io/v2/api",
                    params={
                        "chainid": "56", "module": "contract",
                        "action": "getsourcecode", "address": address,
                        "apikey": ETHERSCAN_KEY,
                    },
                )
                result = es.json().get("result", [{}])
                if result and isinstance(result, list):
                    entry = result[0]
                    nm = (entry.get("ContractName") or "").strip()
                    name = nm or None
                    verified = bool((entry.get("SourceCode") or "").strip())
            except Exception as e:
                log.warning("etherscan lookup failed for %s: %s", address[:10], e)

    return {
        "address": address,
        "contract_type": contract_type,
        "verified": verified,
        "contract_name": name,
    }


async def classify_address(address: str) -> dict:
    """On-demand classify ANY BNB contract address using the real classifier."""
    facts = await _fetch_contract_facts(address)
    if facts is None:
        return {
            "address": address,
            "verdict": "not_a_contract",
            "confidence": 0,
            "reason": "Address has no contract code (likely a wallet/EOA).",
            "source": "PulseBNB — AI contract intelligence on BNB Chain",
        }

    # classify_with_ai is sync (shared httpx.Client) -> run in a thread
    label, reason, score = await asyncio.to_thread(classify_with_ai, facts)

    if label is None:
        return {
            "address": address,
            "verdict": "unavailable",
            "confidence": 0,
            "reason": "Classifier temporarily unavailable, please retry.",
            "contract_name": facts.get("contract_name"),
            "source": "PulseBNB — AI contract intelligence on BNB Chain",
        }

    return {
        "address": address,
        "verdict": label,                       # real | noise
        "confidence": score,                    # 0-100
        "reason": reason,
        "contract_name": facts.get("contract_name"),
        "contract_type": facts.get("contract_type"),
        "verified": facts.get("verified"),
        "source": "PulseBNB — AI contract intelligence on BNB Chain",
    }


async def main() -> None:
    client = AgentClient(
        Config(
            base_url=os.environ["CROO_API_URL"],
            ws_url=os.environ["CROO_WS_URL"],
            rpc_url=os.environ.get("BASE_RPC_URL", ""),
        ),
        os.environ["CROO_SDK_KEY"],
    )

    stream = await client.connect_websocket()
    log.info("PulseBNB CROO agent online. Listening for negotiations...")

    def on_negotiation_created(e: Event) -> None:
        async def _handle() -> None:
            log.info("Negotiation %s received, accepting...", e.negotiation_id)
            try:
                result = await client.accept_negotiation(e.negotiation_id)
                log.info("Order created: %s", result.order.order_id)
            except Exception as err:
                log.error("accept error: %s", err)
        asyncio.create_task(_handle())

    stream.on(EventType.NEGOTIATION_CREATED, on_negotiation_created)

    def on_order_paid(e: Event) -> None:
        async def _handle() -> None:
            log.info("Order %s paid. Classifying...", e.order_id)
            try:
                order = await client.get_order(e.order_id)
                negotiation = await client.get_negotiation(order.negotiation_id)
                address = _extract_address(negotiation.requirements)

                if not address:
                    verdict = {
                        "error": "no valid BNB address in requirements",
                        "expected": '{"address": "0x...40hex"}',
                    }
                else:
                    verdict = await classify_address(address)

                await client.deliver_order(
                    e.order_id,
                    DeliverOrderRequest(
                        deliverable_type=DeliverableType.SCHEMA,
                        deliverable_schema=json.dumps(verdict),
                    ),
                )
                log.info("Order %s delivered: %s",
                         e.order_id, verdict.get("verdict", verdict))
            except Exception as err:
                log.error("deliver error: %s", err)
        asyncio.create_task(_handle())

    stream.on(EventType.ORDER_PAID, on_order_paid)

    def on_order_completed(e: Event) -> None:
        log.info("Order %s completed and settled.", e.order_id)

    stream.on(EventType.ORDER_COMPLETED, on_order_completed)

    stop = asyncio.Event()
    loop = asyncio.get_event_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, stop.set)
        loop.add_signal_handler(signal.SIGTERM, stop.set)
    except NotImplementedError:
        pass
    await stop.wait()

    await stream.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())