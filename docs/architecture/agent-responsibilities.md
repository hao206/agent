# Agent Responsibilities — Construction AI Copilot

Detailed breakdown of agent nodes, roles, inputs, and outputs within the LangGraph multi-agent architecture.

---

## 1. Classify Intent Node (`classify_intent`)
- **Role**: Intent Classifier
- **Responsibility**: Inspects user messages and recent chat history to route incoming requests into standard execution paths.
- **Route Options**:
  - `construction`: Project estimation, material pricing, zoning queries, curing schedules.
  - `follow_up`: Comparative or clarifying questions about existing estimates.
  - `chitchat`: Casual conversation or greeting.
  - `out_of_scope`: Non-construction related requests (refusal policy triggered).

---

## 2. Concept Architect Agent (`planner`)
- **Role**: Plan Drafter & Parameter Extractor
- **Responsibility**: Uses structured output LLM to extract project variables into a typed `ProjectBrief` (location, land area, number of floors, budget, foundation, quality tier).
- **Behavior**: If critical required fields (`location`, `land_area_m2`, `num_floors`, `budget_vnd`) are missing, generates a clarifying Vietnamese follow-up question instead of proceeding.

---

## 3. Human-in-the-Loop Confirmation Gate (`human_confirm`)
- **Role**: Execution Gatekeeper
- **Responsibility**: Pauses execution state using LangGraph `interrupt_before`. Displays extracted parameter draft to user for explicit confirmation or parameter modification before invoking calculation engines.

---

## 4. Specialist Domain Agents (Parallel Map Phase)
Dispatched concurrently via LangGraph `Send` API to collect market data and domain constraints:
- **Material Price Agent (`material_agent`)**: Queries current local market prices for steel, cement, sand, brick, and concrete.
- **Labor Rate Agent (`labor_agent`)**: Fetches regional construction worker daily rates (rough crews, finishing crews, MEP).
- **Seasonality & Curing Agent (`curing_agent`)**: Evaluates regional weather forecasts and concrete curing requirements.
- **Zoning & Legal Agent (`zoning_agent`)**: Queries QCVN 01:2021/BXD rules (building density, max height, front/rear setbacks).

---

## 5. Cost Reducer Node (`cost_reducer`)
- **Role**: State Aggregator & Mathematical Calculator
- **Responsibility**: Collects parallel outputs from specialist agents, applies user price overrides, and invokes the deterministic math engine (`calculate_construction_cost_breakdown`) to produce `BillOfQuantitiesSummary`.

---

## 6. Risk Auditor Agent (`reflect`)
- **Role**: Reflection & Quality Assurance Auditor
- **Responsibility**: Audits total project costs against client budget, checks building density against legal limits, and detects curing risks. Triggers a revision cycle if critical issues are detected (capped at 2 max revisions).

---

## 7. Decision Engine (`decision`)
- **Role**: Option Evaluator & Ranker
- **Responsibility**: Ranks construction options (`budget`, `balanced`, `premium`), calculates feasibility scores, and formats decision evidence.

---

## 8. Response Agent (`respond`)
- **Role**: Report Generator
- **Responsibility**: Synthesizes the final client report in professional Vietnamese Markdown based **strictly** on the verified `DecisionOutput` and `ProjectBrief`.
