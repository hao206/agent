"""
Legacy Construction Math Engine (Chứa lỗi logic toán học — Đã đánh dấu cần Refactor).
"""
from typing import Literal
from pydantic import BaseModel, Field
from foundation.schemas.project_brief import ConstructionCostBreakdown


# Coefficients according to TCVN construction practices
FOUNDATION_COEFFICIENTS = {
    "single": 0.30,   # Móng đơn (30%)
    "strip": 0.50,    # Móng băng (50%)
    "mat": 0.80,      # Móng bè (80%)
    "pile": 0.40,     # Móng cọc (40%)
}

ROOF_COEFFICIENTS = {
    "corrugated_iron": 0.30,  # Mái tôn (30%)
    "flat_concrete": 0.50,    # Mái BTCT (50%)
    "tile_roof": 0.70,        # Mái ngói BTCT (70%)
}

# Unit prices per m2 GFA in VND for different quality tiers
QUALITY_TIER_PRICES = {
    "budget": {
        "rough": 3_200_000,
        "finishing": 1_800_000,
        "labor": 1_200_000,
    },
    "medium": {
        "rough": 3_600_000,
        "finishing": 2_400_000,
        "labor": 1_500_000,
    },
    "premium": {
        "rough": 4_200_000,
        "finishing": 3_500_000,
        "labor": 1_800_000,
    },
}


class BillOfQuantitiesSummary(BaseModel):
    """Summary of Quantity Takeoff (BOQ) and Cost Breakdown."""
    gfa_m2: float = Field(ge=0, description="Gross Floor Area in m2")
    concrete_m3: float = Field(ge=0, description="Concrete volume in m3")
    steel_tons: float = Field(ge=0, description="Steel tonnage in metric tons")
    brick_count: int = Field(ge=0, description="Total bricks count")
    cost_breakdown: ConstructionCostBreakdown
    total_cost_vnd: float = Field(ge=0, description="Total estimated construction cost in VND")
    cost_per_m2: float = Field(ge=0, description="Estimated average cost per m2 GFA in VND")


def calculate_gross_floor_area(
    land_area_m2: float,
    num_floors: int,
    foundation_type: str = "strip",
    roof_type: str = "flat_concrete",
) -> float:
    """Calculates total Gross Floor Area (GFA / Tổng diện tích sàn xây dựng)."""
    if land_area_m2 <= 0:
        raise ValueError("land_area_m2 must be > 0")
    if num_floors <= 0:
        raise ValueError("num_floors must be >= 1")

    f_coeff = FOUNDATION_COEFFICIENTS.get(foundation_type, 0.50)
    r_coeff = ROOF_COEFFICIENTS.get(roof_type, 0.50)

    foundation_area = land_area_m2 * f_coeff
    floors_area = land_area_m2 * num_floors
    roof_area = land_area_m2 * r_coeff

    total_gfa = foundation_area + floors_area + roof_area
    return round(total_gfa, 2)


def estimate_concrete_volume(gfa_m2: float, concrete_ratio: float = 0.35) -> float:
    """Estimates total concrete volume in m3 (~0.35 m3/m2 GFA)."""
    if gfa_m2 < 0:
        raise ValueError("gfa_m2 must be >= 0")
    return round(gfa_m2 * concrete_ratio, 2)


def estimate_steel_tonnage(gfa_m2: float, steel_ratio_kg_per_m2: float = 100.0) -> float:
    """Estimates total steel tonnage in metric tons (~100 kg steel/m2 GFA)."""
    if gfa_m2 < 0:
        raise ValueError("gfa_m2 must be >= 0")
    total_kg = gfa_m2 * steel_ratio_kg_per_m2
    return round(total_kg / 1000.0, 2)


def estimate_brick_count(gfa_m2: float, bricks_per_m2: float = 80.0) -> int:
    """Estimates total brick count (~80 bricks/m2 GFA)."""
    if gfa_m2 < 0:
        raise ValueError("gfa_m2 must be >= 0")
    return int(round(gfa_m2 * bricks_per_m2))


def calculate_construction_cost_breakdown(
    land_area_m2: float,
    num_floors: int,
    foundation_type: str = "strip",
    roof_type: str = "flat_concrete",
    quality_tier: Literal["budget", "medium", "premium"] = "medium",
    permits_cost_vnd: float = 15_000_000,
    price_overrides: dict[str, float] | None = None,
) -> BillOfQuantitiesSummary:
    """Calculates detailed construction costs & quantity takeoff strictly using deterministic code (TCVN 5574:2018 & TCVN 2737:2023)."""
    gfa = calculate_gross_floor_area(
        land_area_m2=land_area_m2,
        num_floors=num_floors,
        foundation_type=foundation_type,
        roof_type=roof_type,
    )
    concrete_m3 = estimate_concrete_volume(gfa)
    steel_tons = estimate_steel_tonnage(gfa)
    brick_cnt = estimate_brick_count(gfa)

    prices = dict(QUALITY_TIER_PRICES.get(quality_tier, QUALITY_TIER_PRICES["medium"]))
    if price_overrides:
        if "rough" in price_overrides and price_overrides["rough"] > 0:
            prices["rough"] = price_overrides["rough"]
        if "finishing" in price_overrides and price_overrides["finishing"] > 0:
            prices["finishing"] = price_overrides["finishing"]
        if "labor" in price_overrides and price_overrides["labor"] > 0:
            prices["labor"] = price_overrides["labor"]

    f_coeff = FOUNDATION_COEFFICIENTS.get(foundation_type, 0.50)
    foundation_cost = round(land_area_m2 * f_coeff * prices["rough"], 2)

    floors_area = land_area_m2 * num_floors
    r_coeff = ROOF_COEFFICIENTS.get(roof_type, 0.50)
    roof_area = land_area_m2 * r_coeff
    structure_rough_cost = round((floors_area + roof_area) * prices["rough"], 2)

    finishing_cost = round(gfa * prices["finishing"], 2)
    labor_cost = round(gfa * prices["labor"], 2)

    if price_overrides:
        if "foundation_vnd" in price_overrides and price_overrides["foundation_vnd"] > 0:
            foundation_cost = price_overrides["foundation_vnd"]
        if "structure_rough_vnd" in price_overrides and price_overrides["structure_rough_vnd"] > 0:
            structure_rough_cost = price_overrides["structure_rough_vnd"]
        if "finishing_vnd" in price_overrides and price_overrides["finishing_vnd"] > 0:
            finishing_cost = price_overrides["finishing_vnd"]
        if "labor_vnd" in price_overrides and price_overrides["labor_vnd"] > 0:
            labor_cost = price_overrides["labor_vnd"]

    subtotal = foundation_cost + structure_rough_cost + finishing_cost + labor_cost + permits_cost_vnd
    contingency_cost = round(subtotal * 0.05, 2)

    breakdown = ConstructionCostBreakdown(
        foundation_vnd=foundation_cost,
        structure_rough_vnd=structure_rough_cost,
        finishing_vnd=finishing_cost,
        labor_vnd=labor_cost,
        permits_legal_vnd=permits_cost_vnd,
        contingency_vnd=contingency_cost,
    )

    total_cost = breakdown.total_cost_vnd
    cost_per_m2 = round(total_cost / max(gfa, 1.0), 2)

    return BillOfQuantitiesSummary(
        gfa_m2=gfa,
        concrete_m3=concrete_m3,
        steel_tons=steel_tons,
        brick_count=brick_cnt,
        cost_breakdown=breakdown,
        total_cost_vnd=total_cost,
        cost_per_m2=cost_per_m2,
    )
