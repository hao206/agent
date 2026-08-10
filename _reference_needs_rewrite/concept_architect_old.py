"""
Legacy ConceptArchitect Agent (Planner) — Extracted for reference, needs rewrite.
"""
from datetime import datetime
from langchain_core.messages import AIMessage

from foundation.prompts.concept_extractor import (
    PLANNER_SYSTEM_PROMPT,
    build_missing_fields_question,
)
from foundation.schemas.project_brief import ProjectBrief


def _default_steps(plan: ProjectBrief) -> list[str]:
    if plan.steps:
        return plan.steps
    return ["material_agent", "labor_agent", "curing_agent", "zoning_agent"]


def planner_node(state: dict) -> dict:
    user_message = state["messages"][-1].content
    recent_messages = state["messages"][-6:]

    # Retrieve existing brief draft if present
    draft = state.get("plan_draft")
    previous_brief = None
    if draft:
        try:
            previous_brief = ProjectBrief.model_validate(draft)
        except Exception:
            pass

    # Dummy/Reference extraction logic placeholder
    brief = ProjectBrief(goal=user_message)

    if previous_brief:
        # Merge previous fields if current extraction is None
        p_dump = previous_brief.model_dump()
        b_dump = brief.model_dump()
        for k, v in b_dump.items():
            if v in (None, "", [], {}) and p_dump.get(k) is not None:
                setattr(brief, k, p_dump[k])

    brief.steps = _default_steps(brief)
    missing = brief.missing_required_fields()

    if missing:
        question = build_missing_fields_question(brief.model_dump(mode="json"), missing)
        print(f"[CONCEPT_ARCHITECT] Missing required fields → asking user: {missing}")
        return {
            "messages": [AIMessage(content=question)],
            "plan": None,
            "plan_draft": brief.model_dump(mode="json"),
            "current_step": "planner",
        }

    graph_plan = {
        "steps": brief.steps,
        "constraints": brief.model_dump(mode="json"),
        "goal": brief.goal,
    }

    return {
        "plan": graph_plan,
        "plan_draft": None,
        "current_step_index": 0,
        "current_step": "planner",
    }
