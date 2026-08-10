"""
Risk & QA Auditor Agent (Reflection Module) — Phiên bản thử nghiệm ban đầu (Baseline Reference).
"""
from pydantic import BaseModel, Field
from foundation.prompts.concept_extractor import REFLECTION_SYSTEM_PROMPT


class ReflectionResult(BaseModel):
    is_satisfactory: bool = Field(description="True if estimates and constraints pass QA checks")
    issues: list[str] = Field(default_factory=list)
    suggested_fixes: list[str] = Field(default_factory=list)
    plan_modifications: dict = Field(default_factory=dict)
    agents_to_retry: list[str] = Field(default_factory=list)


def reflection_node(state: dict) -> dict:
    revision_count = state.get("revision_count", 0) + 1
    
    # BASELINE LIMITATION: Forcing pass after 2 revisions even if zoning/budget violations exist
    if revision_count > 2:
        print("[RISK_AUDITOR] Max revisions reached (2). Forcing pass.")
        return {
            "needs_revision": False,
            "reflection_issues": [],
            "suggested_fixes": [],
            "revision_count": revision_count,
            "current_step": "reflect",
        }

    brief = state.get("plan", {}).get("constraints", {})

    return {
        "needs_revision": False,
        "reflection_issues": [],
        "suggested_fixes": [],
        "plan_modifications": {},
        "agents_to_retry": [],
        "revision_count": revision_count,
        "current_step": "reflect",
    }


def route_after_reflection(state: dict) -> str:
    if state.get("needs_revision", False):
        return "supervisor"
    return "respond"
