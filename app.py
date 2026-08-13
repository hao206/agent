import os
import sys

# Ensure project root is in Python path for Streamlit & Pyright resolution
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from src.graph import graph, AgentState
from src.foundation.schemas.project_brief import ConstructionCostBreakdown

st.set_page_config(page_title="Construction AI Copilot", layout="wide")
st.title("🏗️ Construction AI Copilot - Nền tảng Dự toán Thông minh")
st.caption("Powered by Local Qwen2.5, LangGraph Multi-Agent & Deterministic TCVN Math Engine")

# Initialize State
if "state" not in st.session_state:
    st.session_state.state = {
        "messages": [],
        "project_brief": {},
        "cost_breakdown": {},
        "status": "INIT"
    }

# 1. Render Chat History
for msg in st.session_state.state.get("messages", []):
    role = getattr(msg, "type", "user")
    if role == "human" or (isinstance(msg, dict) and msg.get("role") == "user"):
        st.chat_message("user").write(msg.content if hasattr(msg, "content") else msg.get("content", ""))
    elif role == "ai" or (isinstance(msg, dict) and msg.get("role") == "assistant"):
        st.chat_message("assistant").write(msg.content if hasattr(msg, "content") else msg.get("content", ""))

# 2. Chat Input
user_input = st.chat_input("Nhập yêu cầu (VD: Xây nhà 3 tầng 80m2 tại Hà Nội, gói trung cấp, ngân sách 2 tỷ)")

if user_input:
    from langchain_core.messages import HumanMessage
    st.session_state.state.setdefault("messages", []).append(HumanMessage(content=user_input))
    
    # Run LangGraph Agent Workflow
    st.session_state.state = graph.invoke(st.session_state.state)
    st.rerun()

# 3. Render DECISION_BLOCKED Gate (QCVN / Budget Violation)
if st.session_state.state.get("status") == "DECISION_BLOCKED":
    st.error("🚨 **CẢNH BÁO QUY HOẠCH / RỦI RO (QCVN 01:2021/BXD)**")
    issues = st.session_state.state.get("reflection_issues", [])
    fixes = st.session_state.state.get("suggested_fixes", [])
    for issue in issues:
        st.write(f"- 🔴 {issue}")
    for fix in fixes:
        st.info(f"💡 Gợi ý khắc phục: {fix}")

    st.subheader("🛠️ Điều chỉnh quy mô công trình để khắc phục vi phạm:")
    brief = st.session_state.state.get("project_brief", {})
    with st.form("fix_blocked_form"):
        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("Diện tích đất (m²)", value=float(brief.get('land_area_m2') or 100))
            floors = st.number_input("Số tầng", value=int(brief.get('num_floors') or 3))
        with col2:
            quality = st.selectbox("Gói chất lượng", ["budget", "medium", "premium"], index=["budget", "medium", "premium"].index(brief.get('quality_tier') or 'medium'))
            
        submitted = st.form_submit_button("🔄 Cập nhật quy mô & Chạy lại Kiểm định Risk Auditor")
        if submitted:
            st.session_state.state["project_brief"]["land_area_m2"] = area
            st.session_state.state["project_brief"]["num_floors"] = floors
            st.session_state.state["project_brief"]["quality_tier"] = quality
            st.session_state.state["needs_revision"] = False
            st.session_state.state["status"] = "WAITING_HITL"
            st.session_state.state = graph.invoke(st.session_state.state)
            st.rerun()

# 4. Render HITL Gate (Cổng xác nhận quy mô)
if st.session_state.state.get("status") == "WAITING_HITL":
    st.warning("⚠️ **HITL GATE**: Kiến trúc sư AI đã phác thảo quy mô công trình. Vui lòng xác nhận hoặc chỉnh sửa trước khi hệ thống bóc tách khối lượng.")
    
    brief = st.session_state.state.get("project_brief", {})
    
    with st.form("hitl_form"):
        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("Diện tích đất (m²)", value=float(brief.get('land_area_m2') or 100))
            floors = st.number_input("Số tầng", value=int(brief.get('num_floors') or 3))
        with col2:
            quality_val = brief.get('quality_tier') or 'medium'
            quality_idx = ["budget", "medium", "premium"].index(quality_val) if quality_val in ["budget", "medium", "premium"] else 1
            quality = st.selectbox("Gói chất lượng", ["budget", "medium", "premium"], index=quality_idx)
            
        submitted = st.form_submit_button("✅ Chốt quy mô & Chạy TCVN Math Engine")
        
        if submitted:
            st.session_state.state["project_brief"]["land_area_m2"] = area
            st.session_state.state["project_brief"]["num_floors"] = floors
            st.session_state.state["project_brief"]["quality_tier"] = quality
            
            from src.graph import math_engine_node
            st.session_state.state = math_engine_node(st.session_state.state)
            st.rerun()

# 5. Render Final Report & Dashboard
if st.session_state.state.get("status") == "COMPLETED":
    st.success("✅ **Đã hoàn thành Khái toán Sơ bộ TCVN (AI Concept Estimator)**")
    
    cost_dict = st.session_state.state.get("cost_breakdown", {})
    cost = ConstructionCostBreakdown(**cost_dict)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng Dự Toán", f"{int(cost.total_cost_vnd):,} VNĐ", delta="Đã gồm 5% dự phòng")
    col2.metric("Chi phí Hoàn Thiện", f"{int(cost.finishing_vnd):,} VNĐ")
    col3.metric("Chi phí Nhân Công", f"{int(cost.labor_vnd):,} VNĐ")
    
    with st.expander("📊 Xem chi tiết Bóc tách khối lượng (BOQ) & Cảnh báo Rủi ro"):
        st.write(f"- Chi phí Móng: {int(cost.foundation_vnd):,} VNĐ")
        st.write(f"- Chi phí Phần Thô: {int(cost.structure_rough_vnd):,} VNĐ")
        st.write(f"- Chi phí Giấy phép / Pháp lý: {int(cost.permits_legal_vnd):,} VNĐ")
        st.write(f"- Chi phí Dự phòng (5%): {int(cost.contingency_vnd):,} VNĐ")
        st.info("💡 **Lưu ý chuyên gia:** Đây là khái toán sơ bộ dựa trên diện tích sàn sử dụng thực tế (không tính trùng lặp cho móng/mái). Để có BOQ chính xác từng viên gạch, vui lòng upload file BIM/IFC.")