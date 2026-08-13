"""
Preliminary Risk & Assumption Auditor Node — Construction AI Copilot.

This module performs preliminary rule-based screening on extracted parameters (e.g. checking plot size
against basic floor thresholds and budget constraints).

Disclaimer:
    This auditor is a simplified rule-based screening component for demonstration purposes.
    It does NOT constitute official legal compliance verification or certified building code auditing.
"""
import logging
from pydantic import BaseModel, Field
from src.foundation.schemas.project_brief import ProjectBrief, Risk

logger = logging.getLogger(__name__)


class ReflectionResult(BaseModel):
    is_satisfactory: bool = Field(description="True if estimates and parameters pass preliminary screening")
    issues: list[str] = Field(default_factory=list)
    suggested_fixes: list[str] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)


def check_zoning_violations(brief: ProjectBrief) -> list[Risk]:
    """
    Performs preliminary rule-based screening for building density and height heuristics.
    """
    risks: list[Risk] = []
    
    if brief.land_area_m2 and brief.num_floors:
        if brief.land_area_m2 <= 50 and brief.num_floors > 6:
            risks.append(
                Risk(
                    type="zoning_violation",
                    severity="high",
                    message=f"Preliminary Warning: Plot size ({brief.land_area_m2}m²) with {brief.num_floors} floors triggers maximum height screening heuristic (QCVN 01:2021 reference).",
                    recommendation="Requires professional verification: Consider reducing floor count to 5-6 floors or consulting official local zoning guidelines.",
                )
            )
        elif brief.land_area_m2 > 100 and brief.num_floors > 10:
            risks.append(
                Risk(
                    type="zoning_violation",
                    severity="high",
                    message=f"Potential Issue: Building scale ({brief.num_floors} floors on {brief.land_area_m2}m² plot) exceeds basic residential demo heuristics.",
                    recommendation="Requires professional verification: Project scale requires formal engineering design and local planning approval.",
                )
            )
            
    return risks


def risk_auditor_node(state: dict) -> dict:
    """
    Preliminary Risk & Assumption Auditor Node.
    Audits extracted project parameters against preliminary budget and density screening rules.
    """
    revision_count = state.get("revision_count", 0) + 1
    brief_data = state.get("project_brief", {})
    
    try:
        brief = ProjectBrief.model_validate(brief_data)
    except Exception:
        brief = ProjectBrief()

    # Rule-based screening checks
    zoning_risks = check_zoning_violations(brief)
    
    budget_risks: list[Risk] = []
    cost_breakdown = state.get("cost_breakdown", {})
    total_cost = cost_breakdown.get("total_cost_vnd", 0)
    if brief.budget_vnd and total_cost > brief.budget_vnd * 1.15:
        budget_risks.append(
            Risk(
                type="budget_overrun",
                severity="medium",
                message=f"Preliminary Warning: Estimated total cost ({total_cost:,.0f} VNĐ) exceeds planned budget ({brief.budget_vnd:,.0f} VNĐ) by more than 15%.",
                recommendation="Consider adjusting finishing tier from Premium to Medium or reducing floor count.",
            )
        )

    all_risks = zoning_risks + budget_risks
    critical_violations = [r for r in all_risks if r.severity == "high"]

    if critical_violations:
        logger.info(f"[RISK_AUDITOR] Preliminary rule triggered for revision {revision_count}.")
        return {
            "needs_revision": True,
            "status": "DECISION_BLOCKED",
            "reflection_issues": [r.message for r in critical_violations],
            "suggested_fixes": [r.recommendation or "" for r in critical_violations if r.recommendation],
            "risks": [r.model_dump() for r in all_risks],
            "revision_count": revision_count,
            "current_step": "reflect",
        }

    return {
        "needs_revision": False,
        "status": "PASSED_QA",
        "reflection_issues": [r.message for r in all_risks],
        "suggested_fixes": [r.recommendation or "" for r in all_risks if r.recommendation],
        "risks": [r.model_dump() for r in all_risks],
        "revision_count": revision_count,
        "current_step": "reflect",
    }


def route_after_reflection(state: dict) -> str:
    if state.get("needs_revision", False):
        return "planner"
    return "math_engine"
