# Agent & Node Responsibilities — Construction AI Copilot

Detailed breakdown of current node responsibilities and planned extensions within the research prototype.

---

## Current Implemented Nodes

### 1. Planner Node (`planner`)
- **File**: [planner.py](file:///c:/Users/haoph/Downloads/construction-ai-foundation/src/foundation/agents/planner.py)
- **Role**: Natural Language Parameter Extractor.
- **Responsibility**: Converts Vietnamese user messages into structured Pydantic `ProjectBrief` objects (`location`, `land_area_m2`, `num_floors`, `quality_tier`, `foundation_type`, `roof_type`, `budget_vnd`).
- **Behavior**: Asks clarifying follow-up questions if mandatory parameters (`location`, `land_area_m2`, `num_floors`) are missing.

### 2. Risk & QA Auditor Node (`risk_auditor`)
- **File**: [risk_auditor.py](file:///c:/Users/haoph/Downloads/construction-ai-foundation/src/foundation/agents/risk_auditor.py)
- **Role**: Preliminary Risk & Assumption Auditor.
- **Responsibility**: Evaluates building parameters against basic budget thresholds and preliminary QCVN 01:2021/BXD height/density rules.
- **Behavior**: If severe issues are detected, marks state as `DECISION_BLOCKED` to require human review.

### 3. Math Engine Node (`math_engine`)
- **File**: [math_engine.py](file:///c:/Users/haoph/Downloads/construction-ai-foundation/src/math_engine.py)
- **Role**: Deterministic Estimation Engine.
- **Responsibility**: Computes Gross Floor Area (GFA), preliminary concrete/steel/brick takeoff quantities, and detailed cost breakdowns using explicit testable Python arithmetic.

---

## Planned Extensions (Future Work)

The following agent responsibilities represent planned future enhancements:

- **Material Price Agent (`material_agent`)**: Fetching real-time market material price quotes from external supplier APIs.
- **Labor Rate Agent (`labor_agent`)**: Fetching regional labor wage data for trade workers.
- **Seasonality & Curing Agent (`curing_agent`)**: Analyzing local weather forecasts to predict concrete curing delays.
- **Supervisor Node (`supervisor`)**: Managing dynamic parallel dispatch of specialist agents.
