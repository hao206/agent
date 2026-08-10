# Parallel Agent Dispatcher Pattern (Map-Reduce via LangGraph Send API)

## Overview

In construction project evaluation, querying domain agents sequentially (Material -> Labor -> Seasonality -> Zoning) introduces additive latency (~12-15 seconds total). 

By leveraging LangGraph's dynamic `Send` API, the graph maps specialist agents in parallel and reduces all results into a single deterministic math step (`cost_reducer`), cutting overall latency down to ~3 seconds.

```mermaid
graph TD
    Planner[Planner Agent] --> Confirm{HITL Confirmation}
    Confirm -->|Approved| Dispatcher[Parallel Dispatcher]
    
    subgraph Map Phase (Parallel)
        Dispatcher -->|Send API| Material[Material Agent]
        Dispatcher -->|Send API| Labor[Labor Agent]
        Dispatcher -->|Send API| Curing[Curing Agent]
        Dispatcher -->|Send API| Zoning[Zoning Agent]
    end
    
    subgraph Reduce Phase
        Material --> Reducer[Cost Reducer Node]
        Labor --> Reducer
        Curing --> Reducer
        Zoning --> Reducer
    end
    
    Reducer --> Reflect[Risk Auditor]
```

---

## Pattern Implementation Code (Reference)

```python
from typing import List
from langgraph.graph import StateGraph, END
from langgraph.types import Send
from foundation.schemas import AgentState

# ── 1. Parallel Dispatcher (Map Phase) ────────────────
def parallel_dispatcher_node(state: dict) -> List[Send]:
    """Dispatches specialist domain agents concurrently via LangGraph Send API."""
    print("[PARALLEL_DISPATCHER] Launching specialist agents in parallel.")
    return [
        Send("material_agent", state),
        Send("labor_agent", state),
        Send("curing_agent", state),
        Send("zoning_agent", state),
    ]

# ── 2. Cost Reducer (Reduce Phase) ────────────────────
def cost_reducer_node(state: dict) -> dict:
    """Aggregates parallel outputs and invokes deterministic BOQ math engine."""
    plan = state.get("plan", {})
    constraints = plan.get("constraints", {})
    
    # Run deterministic calculation engine
    boq_summary = calculate_construction_cost_breakdown(...)
    
    return {
        "boq_output": boq_summary.model_dump(mode="json"),
        "completed_agents": ["material_agent", "labor_agent", "curing_agent", "zoning_agent"],
        "current_step": "cost_reducer",
    }

# ── 3. Graph Routing Setup ────────────────────────────
graph = StateGraph(AgentState)
graph.add_node("human_confirm", human_confirm_node)
graph.add_node("material_agent", material_agent_node)
graph.add_node("labor_agent", labor_agent_node)
graph.add_node("curing_agent", curing_agent_node)
graph.add_node("zoning_agent", zoning_agent_node)
graph.add_node("cost_reducer", cost_reducer_node)

# Map edge from confirmation gate to parallel agents
graph.add_conditional_edges("human_confirm", parallel_dispatcher_node, [
    "material_agent", "labor_agent", "curing_agent", "zoning_agent"
])

# Reduce edges from parallel agents into cost_reducer
graph.add_edge("material_agent", "cost_reducer")
graph.add_edge("labor_agent", "cost_reducer")
graph.add_edge("curing_agent", "cost_reducer")
graph.add_edge("zoning_agent", "cost_reducer")
```

---

## Best Practices & Key Takeaways

1. **State Isolation**: Each parallel agent receives a snapshot of `state` via `Send("agent_name", state)`.
2. **Immutable Append**: Agent outputs should update distinct keys in `AgentState` or append to typed lists to avoid state overwrites during parallel reduction.
3. **Deterministic Reduction**: Reducer nodes must rely on pure standard Python code for aggregation to ensure consistent execution.
