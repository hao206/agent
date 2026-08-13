"""
ConceptArchitect Agent (Planner Module) — Dynamic Dispatch & Local Qwen2.5 Integration.
Tự động phân tích quy mô công trình và điều phối danh sách agent cần chạy theo loại hình công trình.
"""
import json
import logging
from datetime import datetime
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.foundation.llm_factory import get_local_qwen
from src.foundation.schemas.project_brief import ProjectBrief
from src.foundation.prompts.concept_extractor import (
    PLANNER_SYSTEM_PROMPT,
    build_missing_fields_question,
)

logger = logging.getLogger(__name__)


def get_dynamic_steps(brief: ProjectBrief) -> list[str]:
    """
    Tự động xác định danh sách các Agent thực thi (Dynamic Dispatch) 
    dựa vào loại hình (residential, commercial, industrial) và quy mô công trình.
    """
    if brief.steps and len(brief.steps) > 0:
        return brief.steps

    steps = ["material_agent", "labor_agent"]

    if brief.construction_type in ["residential", "commercial"]:
        steps.extend(["zoning_agent", "curing_agent"])
    elif brief.construction_type == "industrial":
        steps.extend(["fire_safety_agent", "structural_load_agent"])

    if brief.num_floors and brief.num_floors > 5:
        steps.append("elevator_mep_agent")

    return list(dict.fromkeys(steps))


def planner_node(state: dict) -> dict:
    """
    Planner Node sử dụng Local Qwen2.5 / LLM Factory để trích xuất ProjectBrief.
    """
    messages = state.get("messages", [])
    user_message = messages[-1].content if messages else ""

    # Lấy draft cũ nếu có
    draft = state.get("plan_draft")
    previous_brief: ProjectBrief | None = None
    if draft:
        try:
            previous_brief = ProjectBrief.model_validate(draft)
        except Exception:
            pass

    # Gọi LLM Qwen2.5 để extract thông số
    llm = get_local_qwen()
    parser = PydanticOutputParser(pydantic_object=ProjectBrief)

    formatted_sys = PLANNER_SYSTEM_PROMPT.format(
        current_date=datetime.now().strftime("%Y-%m-%d")
    )
    
    # Ép prompt ngắn gọn dạng Rule-Based + JSON Schema Instructions
    instruction_msg = SystemMessage(
        content=f"{formatted_sys}\n\nHãy trả về JSON tuân thủ schema:\n{parser.get_format_instructions()}"
    )

    extracted_brief: ProjectBrief | None = None
    try:
        response = llm.invoke([instruction_msg, HumanMessage(content=user_message)])
        raw_text = response.content if hasattr(response, "content") else str(response)
        
        # Thử parse qua PydanticOutputParser hoặc json.loads
        try:
            extracted_brief = parser.parse(raw_text)
        except Exception:
            # Fallback parse JSON thủ công nếu Qwen trả về JSON bọc trong markdown code block
            clean_json = raw_text.strip()
            if clean_json.startswith("```"):
                clean_json = clean_json.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            dict_data = json.loads(clean_json)
            extracted_brief = ProjectBrief.model_validate(dict_data)
    except Exception as e:
        logger.warning(f"[PLANNER] Error extracting brief via Qwen2.5: {e}. Fallback to heuristic parser.")

    if not extracted_brief:
        extracted_brief = ProjectBrief(goal=user_message)

    # Merge với previous_brief nếu có
    if previous_brief:
        p_dump = previous_brief.model_dump()
        b_dump = extracted_brief.model_dump()
        for k, v in b_dump.items():
            if v in (None, "", [], {}) and p_dump.get(k) is not None:
                setattr(extracted_brief, k, p_dump[k])

    # Gán Dynamic Steps
    extracted_brief.steps = get_dynamic_steps(extracted_brief)

    # Kiểm tra thiếu thông tin bắt buộc
    missing = extracted_brief.missing_required_fields()
    if missing:
        question = build_missing_fields_question(extracted_brief.model_dump(mode="json"), missing)
        return {
            "messages": [AIMessage(content=question)],
            "plan": None,
            "plan_draft": extracted_brief.model_dump(mode="json"),
            "status": "WAITING_INPUT",
            "current_step": "planner",
        }

    graph_plan = {
        "steps": extracted_brief.steps,
        "constraints": extracted_brief.model_dump(mode="json"),
        "goal": extracted_brief.goal or f"Quy hoạch & dự toán công trình tại {extracted_brief.location}",
    }

    return {
        "project_brief": extracted_brief.model_dump(mode="json"),
        "plan": graph_plan,
        "plan_draft": None,
        "status": "WAITING_HITL",
        "current_step_index": 0,
        "current_step": "planner",
        "messages": [AIMessage(content=f"Đã phác thảo quy mô công trình tại {extracted_brief.location or 'chưa rõ'}. Chờ xác nhận HITL Gate.")],
    }
