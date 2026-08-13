import os
import sys

# Ensure project root is in Python path for Streamlit resolution
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from langchain_core.messages import HumanMessage
from src.graph import graph
from src.foundation.schemas.project_brief import ConstructionCostBreakdown, ProjectBrief

st.set_page_config(
    page_title="Construction AI Copilot — Student Prototype",
    page_icon="🏗️",
    layout="wide",
)

# Sidebar
with st.sidebar:
    st.markdown("### 🎓 Construction AI Copilot")
    st.markdown("**Role**: Student AI Engineering Prototype")
    st.markdown("**Architecture**: LangGraph + Qwen2.5 + Deterministic Math Engine")
    st.markdown("---")
    if st.button("🔄 Reset Demo Session", use_container_width=True):
        st.session_state.state = {
            "messages": [],
            "project_brief": {},
            "cost_breakdown": {},
            "boq_summary": {},
            "status": "INIT",
        }
        st.rerun()

# Header Section
st.title("🏗️ Construction AI Copilot")
st.caption("🎓 **Student Prototype for AI-Assisted Construction Estimation** — Computer Science Research Project")

st.markdown("---")

# Initialize Session State
if "state" not in st.session_state:
    st.session_state.state = {
        "messages": [],
        "project_brief": {},
        "cost_breakdown": {},
        "boq_summary": {},
        "status": "INIT",
    }

# Render Chat History
for msg in st.session_state.state.get("messages", []):
    role = getattr(msg, "type", "user")
    if role == "human" or (isinstance(msg, dict) and msg.get("role") == "user"):
        st.chat_message("user").write(msg.content if hasattr(msg, "content") else msg.get("content", ""))
    elif role == "ai" or (isinstance(msg, dict) and msg.get("role") == "assistant"):
        st.chat_message("assistant").write(msg.content if hasattr(msg, "content") else msg.get("content", ""))

# Input Section
user_input = st.chat_input("Enter project request (e.g. Townhouse 3 floors 100m2 in Hanoi, medium quality, 2.8B VND budget)")

if user_input:
    st.session_state.state.setdefault("messages", []).append(HumanMessage(content=user_input))
    with st.spinner("Processing request via LangGraph workflow..."):
        st.session_state.state = graph.invoke(st.session_state.state)
    st.rerun()

# 1. Processing Status Indicator Pipeline
status = st.session_state.state.get("status", "INIT")

if status != "INIT":
    st.subheader("⚙️ Prototype Execution Pipeline")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    if status in ["WAITING_HITL", "DECISION_BLOCKED", "COMPLETED"]:
        col_s1.success("✓ 1. Parameter Extraction (LLM Planner)")
    else:
        col_s1.info("⏳ 1. Parameter Extraction")

    if status in ["WAITING_HITL", "DECISION_BLOCKED", "COMPLETED"]:
        col_s2.success("✓ 2. Preliminary Risk Screening (Auditor)")
    else:
        col_s2.info("⏳ 2. Preliminary Risk Screening")

    if status == "COMPLETED":
        col_s3.success("✓ 3. Cost & Volume Takeoff (Math Engine)")
    else:
        col_s3.info("⏳ 3. Cost & Volume Takeoff")

st.markdown("---")

# 2. DECISION_BLOCKED State (Rule-based Warning)
if status == "DECISION_BLOCKED":
    st.error("🚨 **PRELIMINARY RISK SCREENING WARNING**")
    issues = st.session_state.state.get("reflection_issues", [])
    fixes = st.session_state.state.get("suggested_fixes", [])
    for issue in issues:
        st.write(f"- 🔴 {issue}")
    for fix in fixes:
        st.info(f"💡 Recommendation: {fix}")

    st.subheader("🛠️ Adjust Parameters for Review:")
    brief = st.session_state.state.get("project_brief", {})
    with st.form("fix_blocked_form"):
        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("Land Area (m²)", value=float(brief.get('land_area_m2') or 100))
            floors = st.number_input("Number of Floors", value=int(brief.get('num_floors') or 3))
        with col2:
            quality = st.selectbox("Quality Tier", ["budget", "medium", "premium"], index=["budget", "medium", "premium"].index(brief.get('quality_tier') or 'medium'))
            
        submitted = st.form_submit_button("🔄 Update & Re-run Screening")
        if submitted:
            st.session_state.state["project_brief"]["land_area_m2"] = area
            st.session_state.state["project_brief"]["num_floors"] = floors
            st.session_state.state["project_brief"]["quality_tier"] = quality
            st.session_state.state["needs_revision"] = False
            st.session_state.state["status"] = "WAITING_HITL"
            st.session_state.state = graph.invoke(st.session_state.state)
            st.rerun()

# 3. WAITING_HITL Confirmation Gate State
if status == "WAITING_HITL":
    st.warning("⚠️ **HUMAN CONFIRMATION GATE**: Please review extracted project parameters before running calculation routines.")
    
    brief_dict = st.session_state.state.get("project_brief", {})
    try:
        brief_obj = ProjectBrief.model_validate(brief_dict)
        assumed = brief_obj.get_assumed_parameters()
    except Exception:
        assumed = {}

    st.markdown("#### Extracted Parameters & Demo Defaults")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Location", brief_dict.get('location') or "Not specified")
    c2.metric("Land Area", f"{brief_dict.get('land_area_m2', 100)} m²")
    c3.metric("Floors", f"{brief_dict.get('num_floors', 3)}")
    budget_val = brief_dict.get('budget_vnd')
    c4.metric("Planned Budget", f"{int(budget_val):,} VNĐ" if budget_val else "Unspecified")

    with st.form("hitl_form"):
        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("Land Area (m²)", value=float(brief_dict.get('land_area_m2') or 100))
            floors = st.number_input("Number of Floors", value=int(brief_dict.get('num_floors') or 3))
        with col2:
            quality_val = brief_dict.get('quality_tier') or 'medium'
            quality_idx = ["budget", "medium", "premium"].index(quality_val) if quality_val in ["budget", "medium", "premium"] else 1
            quality = st.selectbox("Quality Tier", ["budget", "medium", "premium"], index=quality_idx)
            
        submitted = st.form_submit_button("✅ Confirm Parameters & Compute BOQ")
        
        if submitted:
            st.session_state.state["project_brief"]["land_area_m2"] = area
            st.session_state.state["project_brief"]["num_floors"] = floors
            st.session_state.state["project_brief"]["quality_tier"] = quality
            
            from src.graph import math_engine_node
            st.session_state.state = math_engine_node(st.session_state.state)
            st.rerun()

# 4. COMPLETED Results & Dashboard
if status == "COMPLETED":
    st.success("✅ **Preliminary Estimation Complete**")
    
    cost_dict = st.session_state.state.get("cost_breakdown", {})
    cost = ConstructionCostBreakdown(**cost_dict)
    boq_summary = st.session_state.state.get("boq_summary", {})
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Estimated Cost", f"{int(cost.total_cost_vnd):,} VNĐ", help="Includes 5% contingency buffer")
    col2.metric("Estimated GFA", f"{boq_summary.get('gfa_m2', 0)} m²")
    col3.metric("Cost per m² GFA", f"{int(boq_summary.get('cost_per_m2', 0)):,} VNĐ/m²")
    
    with st.expander("📊 Detailed BOQ Takeoff & Cost Breakdown", expanded=True):
        st.markdown("#### Cost Components")
        st.write(f"- **Foundation Cost**: {int(cost.foundation_vnd):,} VNĐ")
        st.write(f"- **Structure Rough Cost**: {int(cost.structure_rough_vnd):,} VNĐ")
        st.write(f"- **Finishing Cost**: {int(cost.finishing_vnd):,} VNĐ *(Calculated strictly on usable floor area)*")
        st.write(f"- **Labor Cost**: {int(cost.labor_vnd):,} VNĐ")
        st.write(f"- **Permits / Fixed Baseline**: {int(cost.permits_legal_vnd):,} VNĐ")
        st.write(f"- **Contingency Buffer (5%)**: {int(cost.contingency_vnd):,} VNĐ")
        
        st.markdown("---")
        st.markdown("#### Preliminary Material Takeoff Estimates")
        st.write(f"- **Concrete Volume**: ~{boq_summary.get('concrete_m3', 0)} m³")
        st.write(f"- **Steel Tonnage**: ~{boq_summary.get('steel_tons', 0)} metric tons")
        st.write(f"- **Brick Count**: ~{boq_summary.get('brick_count', 0):,} bricks")

    with st.expander("📋 Applied Demo Assumptions & Risks"):
        st.markdown("#### Applied Demo Assumptions")
        for asm in boq_summary.get("assumptions_applied", []):
            st.write(f"- ℹ️ {asm}")
            
        risks = st.session_state.state.get("risks", [])
        if risks:
            st.markdown("#### Flagged Preliminary Warnings")
            for r in risks:
                st.write(f"- ⚠️ **[{r.get('type')}]**: {r.get('message')}")

# Footer Disclaimer
st.markdown("---")
st.caption(
    "⚠️ **Disclaimer**: This application is a student research prototype developed for educational and demonstration purposes. "
    "All estimations, material takeoff quantities, and risk alerts are preliminary demo approximations and MUST NOT be used "
    "for official construction contracting, structural engineering design, financial commitments, or regulatory compliance."
)