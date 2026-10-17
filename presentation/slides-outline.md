# CrossPay — Competition Presentation Outline

**WeBank International AI Finance Challenge — Topic C**  
**Duration:** 10 minutes  

---

## Slide 1: Title
- **CrossPay** — AI Financial Assistant for International Students
- WeBank International Track | Topic C: Cross-border & Student Finance
- Team & University Affiliation

## Slide 2: The Problem (1 min)
- 3 student personas: Bangladesh, Pakistan, Nigeria → studying in China
- Pain points: 3-5% FX markups, hidden remittance fees, no credit history, multi-currency budget chaos
- Stat: International students overpay ~$300-500/year on FX alone

## Slide 3: Our Solution (1 min)
- CrossPay: conversational AI agent built on Gemini 3.8 Flash
- Key principle: LLM for intent understanding, deterministic Python for all calculations
- Three-tier security model (Read / Write-confirmed / Regulated)

## Slide 4: Architecture (1.5 min)
- Show architecture diagram from `docs/architecture.md`
- Highlight: Tool call loop, confirmation gate, audit logger
- Stack: Streamlit + Gemini 3.8 Flash + SQLite + Python 3.14

## Slide 5: Live Demo Walkthrough (3 min)
1. "What's the BDT to CNY rate today?" → FX tool call
2. "Compare remittance options for $300" → Provider comparison table
3. "Schedule my tuition payment" → Preview + Confirm flow
4. "How do I build credit in China?" → Credit profile + tips
5. "Transfer $15,000 to Iran" → AML flag + sanctions block

## Slide 6: Security Design (1 min)
- 3-tier permission model table
- Confirmation gate enforcement at Python layer (not LLM prompt)
- AML + sanctions + PII masking — all deterministic, not LLM-judged
- Audit log evidence

## Slide 7: Innovation Highlights (30 sec)
- No-LLM-arithmetic guarantee via function-calling architecture
- Multi-currency support: BDT, PKR, NGN → CNY
- Credit-building advisor tailored to international students (no SSN)
- Stateful multi-turn context via `previous_interaction_id`

## Slide 8: Technical Implementation (30 sec)
- 144 automated tests across 13 test suites (100% passing)
- 24 deterministic tools across FX, remittance, budget, credit, compliance, analytics & anti-fraud
- TDD throughout: tests written before implementation
- Full execution audit trail (Deliverable 06) and 10-page Master Operational Manual

## Slide 9: Roadmap
- Live FX API integration (Wise/TransferWise API)
- Cross-session AML aggregation
- WeBank account integration for real transfers
- Mobile app via Flutter

## Slide 10: Conclusion
- CrossPay solves a real problem for millions of international students
- Security-first design: every financial action is deterministic, audited, and confirmed
- Built by international students, for international students
- GitHub: [repo link]
