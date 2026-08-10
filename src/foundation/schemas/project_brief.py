"""
Consolidated Construction Domain Schemas & Pydantic Models.
Refactored from domain.py and api/schemas/ for production-ready validation.
"""
from __future__ import annotations

from datetime import date as Date
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ── Analytics & System Types ───────────────────────
DataMode = Literal["live", "fixture", "missing"]
CoverageStatus = Literal["draft_only", "verified", "estimated", "unsupported"]
DecisionStatus = Literal["recommended", "needs_revision", "insufficient_data"]
DecisionConfidence = Literal["high", "medium", "low", "insufficient"]


class ProviderRecord(BaseModel):
    """Base record tracking metadata for provider data items."""
    provider: str = "local_market"
    retrieved_at: datetime = Field(default_factory=utc_now)
    data_mode: DataMode = "live"
    assumptions: list[str] = Field(default_factory=list)


class ProjectBrief(BaseModel):
    """Construction Project Brief (Hồ sơ yêu cầu & quy mô công trình xây dựng)."""
    location: str | None = None
    land_area_m2: float | None = Field(default=None, ge=1)
    width_m: float | None = Field(default=None, ge=0)
    length_m: float | None = Field(default=None, ge=0)
    num_floors: int | None = Field(default=None, ge=1, le=50)
    soil_type: Literal["good", "medium", "weak", "unknown"] = "medium"
    foundation_type: Literal["single", "strip", "mat", "pile"] = "strip"
    roof_type: Literal["flat_concrete", "corrugated_iron", "tile_roof"] = "flat_concrete"
    structure_type: Literal["reinforced_concrete", "steel_frame"] = "reinforced_concrete"
    quality_tier: Literal["budget", "medium", "premium"] = "medium"
    budget_vnd: float | None = Field(default=None, ge=0)
    currency: str = "VND"
    start_date: Date | None = None
    construction_type: Literal["residential", "commercial", "industrial"] = "residential"
    functional_requirements: list[str] = Field(default_factory=list)
    priority: Literal["cheapest", "balanced", "high_quality"] = "balanced"
    constraints: dict[str, Any] = Field(default_factory=dict)
    steps: list[str] = Field(default_factory=list)
    goal: str = ""
    version: int = 1

    @model_validator(mode="after")
    def derive_land_area(self) -> "ProjectBrief":
        if self.land_area_m2 is None and self.width_m and self.length_m:
            self.land_area_m2 = round(self.width_m * self.length_m, 2)
        return self

    def missing_required_fields(self) -> list[str]:
        missing: list[str] = []
        if not self.location:
            missing.append("location")
        if not self.land_area_m2:
            missing.append("land_area_m2")
        if not self.num_floors:
            missing.append("num_floors")
        if not self.budget_vnd:
            missing.append("budget_vnd")
        return missing


class BOQItem(BaseModel):
    """Bill of Quantities Item (Hạng mục bóc tách khối lượng & đơn giá)."""
    work_code: str
    work_name: str
    unit: str  # m3, ton, m2, piece, kg, bag, lot
    quantity: float = Field(ge=0)
    unit_price_vnd: float = Field(ge=0)

    @property
    def total_vnd(self) -> float:
        return round(self.quantity * self.unit_price_vnd, 2)


class MaterialPrice(ProviderRecord):
    """Construction Material Market Price (Đơn giá vật liệu xây dựng)."""
    material_id: str
    name: str
    category: Literal["steel", "cement", "sand", "brick", "concrete", "finishing", "general"] = "general"
    unit: str = "kg"
    unit_price_vnd: float = Field(ge=0)
    supplier: str = "Đại lý vật liệu địa phương"
    region: str = "Toàn quốc"
    valid_from: Date | None = None
    valid_to: Date | None = None


class LaborRate(ProviderRecord):
    """Construction Worker / Subcontractor Labor Rate (Đơn giá nhân công thi công)."""
    worker_type: str  # Thợ thô, Thợ hoàn thiện, Thợ điện nước, Giám sát
    daily_rate_vnd: float = Field(ge=0)
    region: str = "Toàn quốc"
    effective_date: Date | None = None


class ZoningConstraint(ProviderRecord):
    """Local Building Code & Zoning Rules (QCVN 01:2021/BXD)."""
    id: str
    name: str
    max_building_density_pct: float | None = Field(default=80.0, ge=0, le=100)
    max_height_m: float | None = Field(default=16.5, ge=0)
    max_floors: int | None = Field(default=4, ge=1)
    setback_front_m: float | None = Field(default=2.4, ge=0)
    setback_rear_m: float | None = Field(default=1.0, ge=0)
    regulation_code: str = "QCVN 01:2021/BXD"
    description: str = ""


class SeasonalityForecast(ProviderRecord):
    """Weather & Concrete Curing Impact Forecast."""
    date: Date
    location: str
    temperature_celsius: float | None = None
    rain_probability: float = Field(default=0, ge=0, le=1)
    curing_impact_days: int = Field(default=0, ge=0)
    summary: str = ""
    curing_recommendation: str = ""


class ConstructionPhase(BaseModel):
    """Construction Schedule Phase (Giai đoạn thi công & tiến độ)."""
    phase_name: str  # Móng & Ngầm, Khung & Thô, Hoàn thiện & MEP, Nghiệm thu
    duration_days: int = Field(ge=1)
    start_date: Date | None = None
    end_date: Date | None = None
    cost_vnd: float = Field(default=0, ge=0)
    boq_items: list[BOQItem] = Field(default_factory=list)


class ConstructionCostBreakdown(BaseModel):
    """Detailed Construction Takeoff Breakdown (Chi phí dự toán công trình)."""
    foundation_vnd: float = Field(default=0, ge=0)
    structure_rough_vnd: float = Field(default=0, ge=0)
    finishing_vnd: float = Field(default=0, ge=0)
    labor_vnd: float = Field(default=0, ge=0)
    permits_legal_vnd: float = Field(default=0, ge=0)
    contingency_vnd: float = Field(default=0, ge=0)

    @property
    def total_cost_vnd(self) -> float:
        return (
            self.foundation_vnd
            + self.structure_rough_vnd
            + self.finishing_vnd
            + self.labor_vnd
            + self.permits_legal_vnd
            + self.contingency_vnd
        )


class Risk(BaseModel):
    """Construction Project Risk Audit."""
    type: str  # budget_overrun, zoning_violation, curing_delay
    severity: Literal["low", "medium", "high"]
    message: str
    recommendation: str | None = None
    suggested_action: str | None = None


class DecisionEvidence(BaseModel):
    type: Literal["warning", "info", "success"]
    rule: str
    observed_value: str
    threshold: str | None = None
    recommendation: str | None = None


class RankedOption(BaseModel):
    id: Literal["budget", "balanced", "premium"]
    total_cost_vnd: float = 0
    cost_per_m2: float = 0
    gfa_m2: float = 0
    feasibility_score: float = 0
    cost_breakdown: ConstructionCostBreakdown = Field(default_factory=ConstructionCostBreakdown)
    reasons: list[str] = Field(default_factory=list)


class DecisionInput(BaseModel):
    project_brief: ProjectBrief
    material_prices: list[MaterialPrice] = Field(default_factory=list)
    labor_rates: list[LaborRate] = Field(default_factory=list)
    zoning_constraints: list[ZoningConstraint] = Field(default_factory=list)
    seasonality_forecasts: list[SeasonalityForecast] = Field(default_factory=list)
    phases: list[ConstructionPhase] = Field(default_factory=list)


class DecisionOutput(BaseModel):
    recommended_option: str | None = None
    budget_status: Literal["under_budget", "near_limit", "slightly_over", "over_budget", "unknown"]
    total_cost_vnd: float = Field(ge=0)
    cost_per_m2: float = Field(ge=0)
    budget_delta_vnd: float | None = None
    gfa_m2: float = Field(ge=0)
    concrete_m3: float = Field(default=0, ge=0)
    steel_tons: float = Field(default=0, ge=0)
    brick_count: int = Field(default=0, ge=0)
    cost_breakdown: ConstructionCostBreakdown
    options: list[RankedOption] = Field(default_factory=list)
    phases: list[ConstructionPhase] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    evidence: list[DecisionEvidence] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    why_recommended: list[str] = Field(default_factory=list)
    coverage_status: CoverageStatus = "draft_only"
    decision_status: DecisionStatus = "insufficient_data"
    confidence: DecisionConfidence = "insufficient"
