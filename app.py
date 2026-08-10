import os
import sys

# Ensure project root is in Python path for Streamlit & Pyright resolution
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from src.graph import graph, AgentState
from foundation.schemas.project_brief import ConstructionCostBreakdown

st.set_page_config(page_title="Construction AI Copilot", layout="wide")
st.title("🏗️ Construction AI Copilot - Nền tảng Dự toán Thông minh")
st.caption("Powered by LangGraph Multi-Agent & Deterministic TCVN Math Engine")

# Initialize State
if "state" not in st.session_state:
    st.session_state.state = {
        "messages": [],
        "project_brief": {},
        "cost_breakdown": {},
        "status": "INIT"
    }

# 1. Chat Input
user_input = st.chat_input("Nhập yêu cầu (VD: Xây nhà 3 tầng 80m2 tại Hà Nội, gói trung cấp)")

if user_input:
    st.session_state.state["messages"].append({"role": "user", "content": user_input})
    
    # Chạy Planner để lấy ProjectBrief
    st.session_state.state = graph.invoke(st.session_state.state)
    st.rerun()

# 2. Render HITL Gate (Cổng xác nhận)
if st.session_state.state.get("status") == "WAITING_HITL":
    st.warning("⚠️ **HITL GATE**: Kiến trúc sư AI đã phác thảo quy mô. Vui lòng xác nhận hoặc chỉnh sửa trước khi hệ thống bóc tách khối lượng.")
    
    brief = st.session_state.state["project_brief"]
    
    with st.form("hitl_form"):
        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("Diện tích đất (m²)", value=float(brief.get('land_area_m2', 100)))
            floors = st.number_input("Số tầng", value=int(brief.get('num_floors', 3)))
        with col2:
            quality = st.selectbox("Gói chất lượng", ["budget", "medium", "premium"], index=["budget", "medium", "premium"].index(brief.get('quality_tier', 'medium')))
            
        submitted = st.form_submit_button("✅ Chốt quy mô & Chạy Math Engine")
        
        if submitted:
            # Update state với dữ liệu user đã sửa
            st.session_state.state["project_brief"]["land_area_m2"] = area
            st.session_state.state["project_brief"]["num_floors"] = floors
            st.session_state.state["project_brief"]["quality_tier"] = quality
            
            # Chạy tiếp Math Engine Node
            # (Trong thực tế dùng LangGraph Command(resume=...), ở đây ta gọi trực tiếp node để demo nhanh)
            from src.graph import math_engine_node
            st.session_state.state = math_engine_node(st.session_state.state)
            st.rerun()

# 3. Render Final Report
if st.session_state.state.get("status") == "COMPLETED":
    st.success("✅ **Đã hoàn thành Khái toán Sơ bộ (AI Concept Estimator)**")
    
    cost_dict = st.session_state.state["cost_breakdown"]
    cost = ConstructionCostBreakdown(**cost_dict)
    
    # Hiển thị Dashboard
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng Dự Toán", f"{int(cost.total_cost_vnd):,} VNĐ", delta="Đã gồm 5% dự phòng")
    col2.metric("Chi phí Hoàn Thiện", f"{int(cost.finishing_vnd):,} VNĐ")
    col3.metric("Chi phí Nhân Công", f"{int(cost.labor_vnd):,} VNĐ")
    
    with st.expander("📊 Xem chi tiết Bóc tách khối lượng (BOQ) & Cảnh báo Rủi ro"):
        st.write(f"- Chi phí Móng: {int(cost.foundation_vnd):,} VNĐ")
        st.write(f"- Chi phí Phần Thô: {int(cost.structure_rough_vnd):,} VNĐ")
        st.write(f"- Chi phí Pháp lý: {int(cost.permits_legal_vnd):,} VNĐ")
        st.info("💡 **Lưu ý chuyên gia:** Đây là khái toán sơ bộ dựa trên diện tích sàn sử dụng thực tế (không tính trùng lặp cho móng/mái). Để có BOQ chính xác từng viên gạch, vui lòng upload file BIM/IFC.")