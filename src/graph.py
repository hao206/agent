"""
LangGraph Multi-Agent Architecture for Construction AI Copilot.
Kết nối Planner Node (Qwen2.5 Local), Risk Auditor Node (QA & HITL Gate) và Deterministic TCVN Math Engine Node.
"""
import operator
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import AIMessage

from src.foundation.schemas.project_brief import ProjectBrief
from src.math_engine import calculate_construction_cost_breakdown
from src.foundation.agents.planner import planner_node
from src.foundation.agents.risk_auditor import risk_auditor_node, route_after_reflection


# 1. State Definition
class AgentState(TypedDict, total=False):
    messages: Annotated[list, operator.add]
    project_brief: dict
    cost_breakdown: dict
    boq_summary: dict
    status: str
    plan: dict
    plan_draft: dict
    revision_count: int
    needs_revision: bool
    reflection_issues: list
    suggested_fixes: list
    risks: list
    current_step: str


# 2. Math Engine Node
def math_engine_node(state: AgentState) -> dict:
    """Node: Tính toán Deterministic (TCVN Math Engine)"""
    brief_dict = state.get("project_brief", {})
    
    boq_summary = calculate_construction_cost_breakdown(
        land_area_m2=float(brief_dict.get("land_area_m2") or 100),
        num_floors=int(brief_dict.get("num_floors") or 3),
        foundation_type=brief_dict.get("foundation_type") or "strip",
        roof_type=brief_dict.get("roof_type") or "flat_concrete",
        quality_tier=brief_dict.get("quality_tier") or "medium",
    )
    
    cost_dict = boq_summary.cost_breakdown.model_dump()
    
    return {
        "cost_breakdown": cost_dict,
        "boq_summary": boq_summary.model_dump(),
        "status": "COMPLETED",
        "current_step": "math_engine",
        "messages": [AIMessage(content=f"Đã hoàn thành bóc tách BOQ & Khái toán sơ bộ TCVN: {int(cost_dict.get('total_cost_vnd', 0)):,} VNĐ.")],
    }


# 3. Build Multi-Agent Graph Workflow
graph_builder = StateGraph(AgentState)

graph_builder.add_node("planner", planner_node)
graph_builder.add_node("risk_auditor", risk_auditor_node)
graph_builder.add_node("math_engine", math_engine_node)

graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "risk_auditor")

graph_builder.add_conditional_edges(
    "risk_auditor",
    route_after_reflection,
    {
        "planner": "planner",
        "math_engine": "math_engine",
    }
)

graph_builder.add_edge("math_engine", END)

graph = graph_builder.compile()