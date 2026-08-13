"""
Golden Master Pattern Test Example — Construction Cost Estimation (Refactored TCVN Baseline).
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.foundation.schemas.project_brief import ConstructionCostBreakdown, ProjectBrief
from src.math_engine import calculate_construction_cost_breakdown


class TestGoldenConstructionCosts(unittest.TestCase):

    def test_golden_townhouse_cost(self):
        """Golden Case 1: Townhouse 100m2, 3 floors, strip foundation, flat roof -> 400m2 GFA"""
        boq = calculate_construction_cost_breakdown(
            land_area_m2=100.0,
            num_floors=3,
            foundation_type="strip",
            roof_type="flat_concrete",
            quality_tier="medium",
        )
        self.assertEqual(boq.gfa_m2, 400.0)
        self.assertEqual(boq.concrete_m3, 140.0)
        self.assertEqual(boq.steel_tons, 40.0)
        self.assertEqual(boq.brick_count, 32000)

        # Medium quality: rough=3.6M, finishing=2.4M, labor=1.5M
        # Foundation cost = 100 * 0.5 * 3,600,000 = 180,000,000 VND
        self.assertEqual(boq.cost_breakdown.foundation_vnd, 180_000_000.0)
        
        # Finishing cost = 300m2 usable area * 2,400,000 = 720,000,000 VND (Refactored TCVN formula)
        self.assertEqual(boq.cost_breakdown.finishing_vnd, 720_000_000.0)

        # Contingency 5% = 2,610,000,000 * 0.05 = 130,500,000 VND
        self.assertEqual(boq.cost_breakdown.contingency_vnd, 130_500_000.0)
        
        # Total cost check
        self.assertEqual(boq.total_cost_vnd, 2_755_500_000.0)
        self.assertEqual(boq.total_cost_vnd, boq.cost_breakdown.total_cost_vnd)

    def test_golden_villa_cost(self):
        """Golden Case 2: Villa 200m2, 2 floors, pile foundation, tile roof -> 620m2 GFA"""
        boq = calculate_construction_cost_breakdown(
            land_area_m2=200.0,
            num_floors=2,
            foundation_type="pile",
            roof_type="tile_roof",
            quality_tier="premium",
        )
        self.assertEqual(boq.gfa_m2, 620.0)
        self.assertGreater(boq.cost_breakdown.foundation_vnd, 0)
        self.assertGreater(boq.total_cost_vnd, 2_000_000_000)

    def test_project_brief_schema_validation(self):
        """Schema validation test: deriving land area from width & length."""
        brief = ProjectBrief(width_m=5.0, length_m=20.0, num_floors=3, budget_vnd=2_000_000_000, location="Hà Nội")
        self.assertEqual(brief.land_area_m2, 100.0)
        self.assertEqual(len(brief.missing_required_fields()), 0)


if __name__ == "__main__":
    unittest.main()
