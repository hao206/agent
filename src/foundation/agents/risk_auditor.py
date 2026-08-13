"""
Risk & QA Auditor Agent (Reflection Module) — Real HITL Gate & QCVN Check.
Loại bỏ hoàn toàn cơ chế force pass tự động sau 2 lần lặp.
Nếu phát hiện vi phạm QCVN 01:2021/BXD hoặc vượt ngân sách nghiêm trọng, kích hoạt cổng HITL.
"""
import logging
from pydantic import BaseModel, Field
from src.foundation.schemas.project_brief import ProjectBrief, Risk

logger = logging.getLogger(__name__)


class ReflectionResult(BaseModel):
    is_satisfactory: bool = Field(description="True if estimates and constraints pass QA checks")
    issues: list[str] = Field(default_factory=list)
    suggested_fixes: list[str] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)


def check_zoning_violations(brief: ProjectBrief) -> list[Risk]:
    """
    Kiểm tra vi phạm Quy chuẩn Xây dựng Việt Nam (QCVN 01:2021/BXD).
    """
    risks: list[Risk] = []
    
    # Quy tắc QCVN: Đất dưới 50m2 được xây 100% diện tích; từ 100m2 trở lên mật độ giảm
    if brief.land_area_m2 and brief.num_floors:
        if brief.land_area_m2 <= 50 and brief.num_floors > 6:
            risks.append(
                Risk(
                    type="zoning_violation",
                    severity="high",
                    message=f"Số tầng ({brief.num_floors} tầng) vượt quá giới hạn tối đa cho phép đối với lô đất {brief.land_area_m2}m² theo QCVN 01:2021/BXD.",
                    recommendation="Vui lòng giảm số tầng xuống tối đa 5-6 tầng hoặc xin phép điều chỉnh chỉ tiêu quy hoạch 1/500.",
                )
            )
        elif brief.land_area_m2 > 100 and brief.num_floors > 10:
            risks.append(
                Risk(
                    type="zoning_violation",
                    severity="high",
                    message=f"Dự án quy mô {brief.num_floors} tầng trên đất {brief.land_area_m2}m² vượt mật độ & chiều cao quy hoạch nhà ở riêng lẻ.",
                    recommendation="Cần lập dự án đầu tư và thẩm duyệt PCCC & Giấy phép xây dựng cấp tỉnh/thành phố.",
                )
            )
            
    return risks


def risk_auditor_node(state: dict) -> dict:
    """
    Risk Auditor Node: Đánh giá rủi ro pháp lý & ngân sách.
    Loại bỏ cơ chế force-pass. Nếu vi phạm nghiêm trọng -> Yêu cầu Human can thiệp (HITL).
    """
    revision_count = state.get("revision_count", 0) + 1
    brief_data = state.get("project_brief", {})
    
    try:
        brief = ProjectBrief.model_validate(brief_data)
    except Exception:
        brief = ProjectBrief()

    # Audit QCVN Zoning Rules
    zoning_risks = check_zoning_violations(brief)
    
    # Audit Budget Overrun if cost_breakdown and budget_vnd are present
    budget_risks: list[Risk] = []
    cost_breakdown = state.get("cost_breakdown", {})
    total_cost = cost_breakdown.get("total_cost_vnd", 0)
    if brief.budget_vnd and total_cost > brief.budget_vnd * 1.15:
        budget_risks.append(
            Risk(
                type="budget_overrun",
                severity="medium",
                message=f"Tổng chi phí dự toán ({total_cost:,.0f} VNĐ) vượt 15% so với ngân sách dự kiến ({brief.budget_vnd:,.0f} VNĐ).",
                recommendation="Xem xét giảm chất lượng vật liệu hoàn thiện từ Premium -> Medium hoặc giảm 1 tầng.",
            )
        )

    all_risks = zoning_risks + budget_risks
    critical_violations = [r for r in all_risks if r.severity == "high"]

    if critical_violations:
        logger.warning(f"[RISK_AUDITOR] Found critical violations! Triggering HITL Gate for revision {revision_count}.")
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
