"""
PulseBNB CROO requester — fires one real paid call at the provider service.

Negotiates an order, pays USDC, receives the classification verdict.
This is the end-to-end proof: a settled order on CROO CAP.
"""

import asyncio
import json
import logging
import os

from croo import (
    AgentClient,
    Config,
    EventType,
    DeliverableType,
    NegotiateOrderRequest,
    Event,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("pulsebnb-requester")

# The contract to classify in this test (a real indexed builder).
TARGET_CONTRACT = os.environ.get(
    "TEST_CONTRACT", "0x7bce38b9af4822a04e4d3224067a99b4585b91ff"
)


async def main() -> None:
    client = AgentClient(
        Config(
            base_url=os.environ["CROO_API_URL"],
            ws_url=os.environ["CROO_WS_URL"],
            rpc_url=os.environ.get("BASE_RPC_URL", ""),
        ),
        os.environ["CROO_SDK_KEY"],  # the TESTER's key
    )

    stream = await client.connect_websocket()
    done = asyncio.Event()

    # Pay as soon as the order is created
    def on_order_created(e: Event) -> None:
        async def _handle() -> None:
            log.info("Order %s created, paying USDC...", e.order_id)
            try:
                result = await client.pay_order(e.order_id)
                log.info("PAID. tx_hash: %s", result.tx_hash)
            except Exception as err:
                log.error("pay error: %s", err)
                done.set()
        asyncio.create_task(_handle())

    stream.on(EventType.ORDER_CREATED, on_order_created)

    # Read the delivered verdict when the order completes
    def on_order_completed(e: Event) -> None:
        async def _handle() -> None:
            log.info("Order %s COMPLETED. Fetching delivery...", e.order_id)
            try:
                delivery = await client.get_delivery(e.order_id)
                if delivery.deliverable_type == DeliverableType.SCHEMA:
                    verdict = json.loads(delivery.deliverable_schema)
                    print("\n========== CLASSIFICATION RESULT ==========")
                    print(json.dumps(verdict, indent=2))
                    print("===========================================\n")
                else:
                    print("Delivery (text):", delivery.deliverable_text)
            except Exception as err:
                log.error("get delivery error: %s", err)
            done.set()
        asyncio.create_task(_handle())

    stream.on(EventType.ORDER_COMPLETED, on_order_completed)

    def on_negotiation_rejected(e: Event) -> None:
        log.error("Negotiation rejected: %s", e.reason)
        done.set()
    stream.on(EventType.NEGOTIATION_REJECTED, on_negotiation_rejected)

    # Start the negotiation against the provider service
    log.info("Negotiating order for contract %s...", TARGET_CONTRACT)
    neg = await client.negotiate_order(NegotiateOrderRequest(
        service_id=os.environ["CROO_TARGET_SERVICE_ID"],
        requirements=json.dumps({"address": TARGET_CONTRACT}),
    ))
    log.info("Negotiation started: %s", neg.negotiation_id)

    # Wait for completion (with a timeout safety net)
    try:
        await asyncio.wait_for(done.wait(), timeout=120)
    except asyncio.TimeoutError:
        log.error("Timed out waiting for order completion (120s).")

    await stream.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())