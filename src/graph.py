import operator
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from foundation.schemas.project_brief import ProjectBrief
# pyrefly: ignore [missing-import]
from src.math_engine import calculate_construction_cost_breakdown
import json

# 1. Define State
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    project_brief: dict
    cost_breakdown: dict
    status: str

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key.startswith("your_") or api_key == "sk-...":
    api_key = "dummy-api-key-for-init"

llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)

# 2. Nodes
def planner_node(state: AgentState) -> dict:
    """Agent 1: Trích xuất thông số từ câu nói của người dùng"""
    sys_prompt = """Bạn là Concept Architect. Hãy trích xuất JSON từ yêu cầu của user với các key: 
    location, land_area_m2, num_floors, foundation_type, roof_type, quality_tier.
    Chỉ trả về JSON, không markdown."""
    
    response = llm.invoke([SystemMessage(content=sys_prompt)] + state["messages"])
    
    # Giả lập parse JSON (Thực tế nên dùng Pydantic with_structured_output)
    try:
        brief_dict = json.loads(response.content)
    except:
        brief_dict = {"land_area_m2": 100, "num_floors": 3, "quality_tier": "medium"} # Fallback
        
    return {
        "project_brief": brief_dict, 
        "status": "WAITING_HITL",
        "messages": [AIMessage(content=f"Đã phác thảo: {brief_dict}")]
    }

def math_engine_node(state: AgentState) -> dict:
    """Agent 2: Tính toán Deterministic (Không dùng LLM)"""
    brief = state["project_brief"]
    
    # Gọi Math Engine chuẩn TCVN
    cost = calculate_construction_cost_breakdown(
        land_area_m2=float(brief.get("land_area_m2", 100)),
        num_floors=int(brief.get("num_floors", 3)),
        foundation_type=brief.get("foundation_type", "strip"),
        roof_type=brief.get("roof_type", "flat_concrete"),
        quality_tier=brief.get("quality_tier", "medium")
    )
    
    return {
        "cost_breakdown": cost.model_dump(),
        "status": "COMPLETED",
        "messages": [AIMessage(content="Đã tính toán xong BOQ & Chi phí.")]
    }

# 3. Build Graph
graph_builder = StateGraph(AgentState)
graph_builder.add_node("planner", planner_node)
graph_builder.add_node("math_engine", math_engine_node)

graph_builder.add_edge(START, "planner")
# Luồng sẽ dừng ở Planner để chờ HITL từ Streamlit, sau đó mới nhảy sang math_engine
graph_builder.add_edge("math_engine", END)

graph = graph_builder.compile()