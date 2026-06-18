<div align="center">

<svg width="780" height="180" viewBox="0 0 780 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b0b0b"/>
      <stop offset="100%" stop-color="#0a1a14"/>
    </linearGradient>
    <linearGradient id="grn" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#22c55e"/>
      <stop offset="100%" stop-color="#86efac"/>
    </linearGradient>
  </defs>
  <rect width="780" height="180" fill="url(#bg)" rx="14"/>
  <circle cx="90" cy="90" r="6" fill="#22c55e">
    <animate attributeName="r" values="6;26;6" dur="2.4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0;1" dur="2.4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="90" cy="90" r="6" fill="#22c55e"/>
  <text x="158" y="76" font-family="'Courier New', monospace" font-size="38" font-weight="800" fill="url(#grn)">PulseBNB Agent</text>
  <text x="160" y="110" font-family="'Courier New', monospace" font-size="15" fill="#bdbdbd">A paid, callable contract-intelligence agent on CROO Agent Protocol.</text>
  <text x="160" y="136" font-family="'Courier New', monospace" font-size="13" fill="#7a7a7a">Send any BNB address. Pay USDC. Get an AI verdict: real builder or noise.</text>
</svg>

<br/>

[![CROO Agent Protocol](https://img.shields.io/badge/Built_on-CROO_CAP-22c55e?style=for-the-badge)](https://cap.croo.network)
[![Settlement](https://img.shields.io/badge/Settles-USDC_on_Base-0052FF?style=for-the-badge&logo=coinbase&logoColor=white)](https://base.org)
[![Classifier](https://img.shields.io/badge/Powered_by-PulseBNB-F3BA2F?style=for-the-badge)](https://pulsebnb-web.vercel.app)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

</div>

---

> **The pitch:** Anyone can pay this agent a small USDC fee, send it any BNB Chain contract address, and get back an AI verdict — *real builder* or *ecosystem noise* — with a reason and a confidence score. It's the [PulseBNB](https://pulsebnb-web.vercel.app) classifier, wrapped as a paid, callable agent on the CROO Agent Protocol.

## Proof: a real settled order

This isn't a mock. A requester paid USDC, the agent classified on-demand, and the order settled on-chain — the full CAP lifecycle, verifiable on Base:

| Step | Transaction |
|---|---|
| **Pay** (USDC into escrow) | [`0x24af2323…b80e3f69`](https://basescan.org/tx/0x24af2323896394c9ae862ad1821234f99f970a698db0a8bdfa8ab296b80e3f69) |
| **Deliver** (verdict on-chain) | [`0x09542435…6eb978d8`](https://basescan.org/tx/0x0954243549858dfc234f0dfeb96013e9e74ee36b9edc639b6df51ae56eb978d8) |
| **Clear** (escrow settled) | [`0xf253dea8…f43c6535`](https://basescan.org/tx/0xf253dea851bbf6d60e4ece343cd49be56f37da0769d024ff4fbc1097f43c6535) |

The delivered result:

```json
{
  "address": "0x7bce38b9af4822a04e4d3224067a99b4585b91ff",
  "verdict": "real",
  "confidence": 70,
  "reason": "Custom vault deployer, not a standard template",
  "contract_name": "RuyiBeastSaleVaultDeployer",
  "contract_type": "OTHER",
  "verified": true,
  "source": "PulseBNB — AI contract intelligence on BNB Chain"
}
```

## What it does

100+ contracts deploy to BNB Chain every day — mostly forks, templates, copy-paste tokens, and name-spoof scams. The PulseBNB classifier separates real builders from that noise. This agent exposes that capability as a **paid service**: pay-per-classification, settled trustlessly, with on-chain reputation accruing per order.

**On-demand:** it classifies *any* address — even a contract deployed seconds ago that no index has seen yet. On a paid order it fetches the target's bytecode, detects its type, pulls its name and verification status, and runs the exact PulseBNB classifier, then delivers a structured verdict.

## How a call flows

```
Requester                                Provider (this agent)
    |                                          |
    |-- NegotiateOrder {"address":"0x..."} --->|
    |                                          |-- accept_negotiation
    |<------------- order_created -------------|
    |-- PayOrder (USDC -> CAP escrow) ---------|
    |                                          |-- on_order_paid:
    |                                          |     fetch bytecode + name
    |                                          |     detect ERC type
    |                                          |     run PulseBNB classifier
    |<------------ order_completed ------------|     deliver SCHEMA verdict
    |-- GetDelivery -> {verdict, score}        |
    v  settled                                 v  payment cleared
```

## The classifier brain

The verdict comes from the production PulseBNB classifier ([ai_classifier.py](https://github.com/Makabeez/pulsebnb)) — the same model and prompt that power the live [pulsebnb-web.vercel.app](https://pulsebnb-web.vercel.app) dashboard:

- **Real** — custom app logic, original protocols, distinct code worth tracking.
- **Noise** — DEX pair templates, factory clones, copy-paste meme tokens, dead code.
- **Spoof** — a fresh contract claiming a famous token name (Tether, USDC…) flagged as impersonation.

This agent reuses that logic directly — no reimplementation, no drift.

## Tech stack

| Layer | Choice |
|---|---|
| Agent protocol | CROO CAP (`croo-sdk`, Python) |
| Settlement | USDC on Base (escrow → deliver → clear) |
| Classifier | PulseBNB via LiteLLM router (reasoning model) |
| Contract facts | BNB RPC (bytecode) + Etherscan V2 (`chainid=56`) |
| Runtime | Python 3.12 async, PM2-managed, 24/7 |

## Run it

```bash
git clone https://github.com/Makabeez/pulsebnb-croo.git
cd pulsebnb-croo
python3 -m venv venv && source venv/bin/activate
pip install croo-sdk httpx python-dotenv

cp .env.example .env   # add your CROO_SDK_KEY + classifier keys
python3 croo_provider.py   # agent goes "online", listens for paid orders
```

The provider runs as a long-lived process (PM2 in production), auto-accepting negotiations and delivering verdicts on payment.

## Built for

**[CROO Agent Hackathon](https://campaigns.croo.network/hackathon.html)** — paid, callable agents on CROO Agent Protocol. Extends [PulseBNB](https://github.com/Makabeez/pulsebnb) (BNB Chain contract intelligence) into the agent-commerce layer.

## License

MIT
