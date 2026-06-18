<div align="center">



<svg width="780" height="180" viewBox="0 0 780 180" xmlns="http://www.w3.org/2000/svg">

&#x20; <defs>

&#x20;   <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">

&#x20;     <stop offset="0%" stop-color="#0b0b0b"/>

&#x20;     <stop offset="100%" stop-color="#0a1a14"/>

&#x20;   </linearGradient>

&#x20;   <linearGradient id="grn" x1="0%" y1="0%" x2="100%" y2="0%">

&#x20;     <stop offset="0%" stop-color="#22c55e"/>

&#x20;     <stop offset="100%" stop-color="#86efac"/>

&#x20;   </linearGradient>

&#x20; </defs>

&#x20; <rect width="780" height="180" fill="url(#bg)" rx="14"/>



&#x20; <!-- pulse node -->

&#x20; <circle cx="90" cy="90" r="6" fill="#22c55e">

&#x20;   <animate attributeName="r" values="6;26;6" dur="2.4s" repeatCount="indefinite"/>

&#x20;   <animate attributeName="opacity" values="1;0;1" dur="2.4s" repeatCount="indefinite"/>

&#x20; </circle>

&#x20; <circle cx="90" cy="90" r="6" fill="#22c55e"/>



&#x20; <text x="158" y="76" font-family="'Courier New', monospace" font-size="40" font-weight="800" fill="url(#grn)">

&#x20;   PulseBNB Agent

&#x20; </text>

&#x20; <text x="160" y="110" font-family="'Courier New', monospace" font-size="15" fill="#bdbdbd">

&#x20;   A paid, callable contract-intelligence agent on CROO Agent Protocol.

&#x20; </text>

&#x20; <text x="160" y="136" font-family="'Courier New', monospace" font-size="13" fill="#7a7a7a">

&#x20;   Send any BNB address. Pay USDC. Get an AI verdict: real builder or noise.

&#x20; </text>

</svg>



<br/>



\[!\[CROO Agent Protocol](https://img.shields.io/badge/Built\_on-CROO\_CAP-22c55e?style=for-the-badge)](https://cap.croo.network)

\[!\[Settlement](https://img.shields.io/badge/Settles-USDC\_on\_Base-0052FF?style=for-the-badge\&logo=coinbase\&logoColor=white)](https://base.org)

\[!\[Classifier](https://img.shields.io/badge/Powered\_by-PulseBNB-F3BA2F?style=for-the-badge)](https://pulsebnb-web.vercel.app)

\[!\[License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)



</div>



\---



> \*\*The pitch:\*\* Anyone can pay this agent a small USDC fee, send it any BNB Chain contract address, and get back an AI verdict — \*real builder\* or \*ecosystem noise\* — with a reason and a confidence score. It's the \[PulseBNB](https://pulsebnb-web.vercel.app) classifier, wrapped as a paid, callable agent on the CROO Agent Protocol.



\## Proof: a real settled order



This isn't a mock. A requester paid USDC, the agent classified on-demand, and the order settled on-chain — the full CAP lifecycle, verifiable on Base:



| Step | Transaction |

|---|---|

| \*\*Pay\*\* (USDC into escrow) | \[`0x24af2323…b80e3f69`](https://basescan.org/tx/0x24af2323896394c9ae862ad1821234f99f970a698db0a8bdfa8ab296b80e3f69) |

| \*\*Deliver\*\* (verdict on-chain) | \[`0x09542435…6eb978d8`](https://basescan.org/tx/0x0954243549858dfc234f0dfeb96013e9e74ee36b9edc639b6df51ae56eb978d8) |

| \*\*Clear\*\* (escrow settled) | \[`0xf253dea8…f43c6535`](https://basescan.org/tx/0xf253dea851bbf6d60e4ece343cd49be56f37da0769d024ff4fbc1097f43c6535) |



The delivered result:



```json

{

&#x20; "address": "0x7bce38b9af4822a04e4d3224067a99b4585b91ff",

&#x20; "verdict": "real",

&#x20; "confidence": 70,

&#x20; "reason": "Custom vault deployer, not a standard template",

&#x20; "contract\_name": "RuyiBeastSaleVaultDeployer",

&#x20; "contract\_type": "OTHER",

&#x20; "verified": true,

&#x20; "source": "PulseBNB — AI contract intelligence on BNB Chain"

}

```



\## What it does



100+ contracts deploy to BNB Chain every day — mostly forks, templates, copy-paste tokens, and name-spoof scams. The PulseBNB classifier separates real builders from that noise. This agent exposes that capability as a \*\*paid service\*\*: pay-per-classification, settled trustlessly, with on-chain reputation accruing per order.



\*\*On-demand\*\*: it classifies \*any\* address — even a contract deployed seconds ago that no index has seen yet. On a paid order it fetches the target's bytecode, detects its type, pulls its name + verification status, and runs the exact PulseBNB classifier, then delivers a structured verdict.



\## How a call flows



```

Requester                                Provider (this agent)

&#x20;   │                                          │

&#x20;   ├─ NegotiateOrder {"address":"0x..."} ────►│

&#x20;   │                                          ├─ accept\_negotiation

&#x20;   │◄────────────── order\_created ────────────┤

&#x20;   ├─ PayOrder (USDC → CAP escrow) ───────────┤

&#x20;   │                                          ├─ on\_order\_paid:

&#x20;   │                                          │    fetch bytecode + name

&#x20;   │                                          │    detect ERC type

&#x20;   │                                          │    run PulseBNB classifier

&#x20;   │◄───────────── order\_completed ───────────┤    deliver SCHEMA verdict

&#x20;   ├─ GetDelivery → {verdict, score, reason}  │

&#x20;   ▼ settled ✓                                ▼ payment cleared ✓

```



\## The classifier brain



The verdict comes from the production PulseBNB classifier (\[ai\_classifier.py](https://github.com/Makabeez/pulsebnb)) — the same model and prompt that power the live \[pulsebnb-web.vercel.app](https://pulsebnb-web.vercel.app) dashboard:



\- \*\*Real\*\* — custom app logic, original protocols, distinct code worth tracking.

\- \*\*Noise\*\* — DEX pair templates, factory clones, copy-paste meme tokens, dead code.

\- \*\*Spoof\*\* — a fresh contract claiming a famous token name (Tether, USDC…) flagged as impersonation.



This agent reuses that logic directly — no reimplementation, no drift.



\## Tech stack



| Layer | Choice |

|---|---|

| Agent protocol | CROO CAP (`croo-sdk`, Python) |

| Settlement | USDC on Base (escrow → deliver → clear) |

| Classifier | PulseBNB via LiteLLM router (reasoning model) |

| Contract facts | BNB RPC (bytecode) + Etherscan V2 (`chainid=56`) |

| Runtime | Python 3.12 async, PM2-managed, 24/7 |



\## Run it



```bash

git clone https://github.com/Makabeez/pulsebnb-croo.git

cd pulsebnb-croo

python3 -m venv venv \&\& source venv/bin/activate

pip install croo-sdk httpx python-dotenv



cp .env.example .env   # add your CROO\_SDK\_KEY + classifier keys

python3 croo\_provider.py   # agent goes "online", listens for paid orders

```



The provider runs as a long-lived process (PM2 in production), auto-accepting negotiations and delivering verdicts on payment.



\## Built for



\*\*\[CROO Agent Hackathon](https://campaigns.croo.network/hackathon.html)\*\* — paid, callable agents on CROO Agent Protocol. Extends \[PulseBNB](https://github.com/Makabeez/pulsebnb) (BNB Chain contract intelligence) into the agent-commerce layer.



\## License



MIT

