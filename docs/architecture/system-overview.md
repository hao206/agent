# Architecture Overview — Construction AI Copilot (Student Prototype)

## Overview

**Construction AI Copilot** is an educational research prototype exploring workflow orchestration using **LangGraph**, **FastAPI**, and **Pydantic V2**.

The application isolates probabilistic LLM reasoning (parameter extraction and natural language understanding) from deterministic computation (arithmetic cost & volume takeoff) and rule-based screening.

```mermaid
graph TD
    subgraph Frontend Layer
        UI[Streamlit Web App - app.py]
    end

    subgraph API Layer
        API[FastAPI Router - main.py]
    end

    subgraph Multi-Agent Graph Layer - src/graph.py
        Planner[Planner Node - Local Qwen2.5 / LLM]
        Auditor[Risk Auditor Node - Rule Screening]
        Engine[Deterministic Estimation Engine]
    end

    UI --> API
    UI <--> Multi-Agent Graph Layer
    API <--> Multi-Agent Graph Layer
```

---

## Current Architecture Components

### 1. Planner Node (`src/foundation/agents/planner.py`)
- **Role**: Natural language parameter extractor.
- **Implementation**: Uses Local Qwen2.5 via `ChatOllama` (`src/foundation/llm_factory.py`) with `PydanticOutputParser` to populate the `ProjectBrief` schema.
- **Dynamic Dispatch**: Determines required execution steps based on building type (`residential`, `commercial`, `industrial`) and scale (`num_floors > 5`).

### 2. Risk & QA Auditor Node (`src/foundation/agents/risk_auditor.py`)
- **Role**: Preliminary rule-based risk screening.
- **Implementation**: Audits extracted parameters against basic QCVN 01:2021/BXD height/density heuristics and budget thresholds.
- **HITL Routing**: If critical issues are flagged, state updates to `DECISION_BLOCKED`, requiring human user confirmation or parameter correction on the UI.

### 3. Deterministic Math Engine (`src/math_engine.py`)
- **Role**: Arithmetical takeoff and preliminary cost computation.
- **Implementation**: Standard testable Python code implementing GFA formulas, preliminary material volume estimates, and cost breakdown arithmetic.

---

## Key Architectural Principles

1. **Deterministic Computation First**: All numbers ($m^2$ GFA, $m^3$ concrete, steel tons, brick counts, cost breakdowns) are calculated using explicit Python code rather than LLM inference.
2. **Explicit State Transitions**: LangGraph `StateGraph` models processing nodes (`planner`, `risk_auditor`, `math_engine`) and explicit conditional routing (`route_after_reflection`).
3. **Human-in-the-Loop Confirmation (HITL)**: Workflow pauses at `WAITING_HITL` or `DECISION_BLOCKED` states so the user can verify parameters before final cost computation.

---

## Experimental & Planned Extensions (Future Work)

The following components represent conceptual design ideas for future extension:
- **Material Price Agent**: Querying live market material price feeds.
- **Labor Rate Agent**: Querying regional subcontractor labor rates.
- **Weather & Curing Agent**: Integrating real-time weather forecasts for concrete curing scheduling.
- **Supervisor Dispatcher**: Dynamic multi-agent supervisor dispatching parallel specialist agents.
