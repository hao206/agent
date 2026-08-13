"""
Engine Tính toán Chi phí & Bóc tách Khối lượng — Refactored Baseline Engine (TCVN 5574/2737).
"""
from typing import Literal
from pydantic import BaseModel, Field
from src.foundation.schemas.project_brief import ConstructionCostBreakdown

# Import core deterministic math logic from src.math_engine
from src.math_engine import (
    FOUNDATION_COEFFICIENTS,
    ROOF_COEFFICIENTS,
    QUALITY_TIER_PRICES,
    BillOfQuantitiesSummary,
    calculate_gross_floor_area,
    estimate_concrete_volume,
    estimate_steel_tonnage,
    estimate_brick_count,
    calculate_construction_cost_breakdown,
)

__all__ = [
    "FOUNDATION_COEFFICIENTS",
    "ROOF_COEFFICIENTS",
    "QUALITY_TIER_PRICES",
    "BillOfQuantitiesSummary",
    "calculate_gross_floor_area",
    "estimate_concrete_volume",
    "estimate_steel_tonnage",
    "estimate_brick_count",
    "calculate_construction_cost_breakdown",
]
