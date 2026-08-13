"""
Unit tests for Pydantic V2 ProjectBrief and ConstructionCostBreakdown schemas.
"""
import unittest
from pydantic import ValidationError
from src.foundation.schemas.project_brief import ProjectBrief, ConstructionCostBreakdown, BOQItem


class TestSchemas(unittest.TestCase):

    def test_valid_project_brief(self):
        brief = ProjectBrief(
            location="Hà Nội",
            land_area_m2=100.0,
            num_floors=3,
            budget_vnd=2_000_000_000.0,
        )
        self.assertEqual(brief.location, "Hà Nội")
        self.assertEqual(brief.land_area_m2, 100.0)
        self.assertEqual(brief.num_floors, 3)
        self.assertEqual(len(brief.missing_required_fields()), 0)

    def test_derive_land_area_from_dimensions(self):
        brief = ProjectBrief(
            width_m=5.0,
            length_m=20.0,
            num_floors=3,
            location="Đà Nẵng",
            budget_vnd=1_500_000_000.0,
        )
        self.assertEqual(brief.land_area_m2, 100.0)

    def test_missing_required_fields(self):
        brief = ProjectBrief(location="TP.HCM")
        missing = brief.missing_required_fields()
        self.assertIn("land_area_m2", missing)
        self.assertIn("num_floors", missing)
        self.assertIn("budget_vnd", missing)

    def test_invalid_negative_land_area(self):
        with self.assertRaises(ValidationError):
            ProjectBrief(land_area_m2=-50.0)

    def test_computed_field_serialization(self):
        cost = ConstructionCostBreakdown(
            foundation_vnd=100_000_000.0,
            structure_rough_vnd=500_000_000.0,
            finishing_vnd=300_000_000.0,
            labor_vnd=200_000_000.0,
            permits_legal_vnd=15_000_000.0,
            contingency_vnd=55_000_000.0,
        )
        self.assertEqual(cost.total_cost_vnd, 1_170_000_000.0)
        dump = cost.model_dump()
        self.assertIn("total_cost_vnd", dump)
        self.assertEqual(dump["total_cost_vnd"], 1_170_000_000.0)

    def test_assumed_parameters_tracking(self):
        brief = ProjectBrief(location="Hà Nội", land_area_m2=100.0, num_floors=3)
        assumptions = brief.get_assumed_parameters()
        self.assertIn("foundation_type", assumptions)
        self.assertIn("assumed demo default", assumptions["foundation_type"])


if __name__ == "__main__":
    unittest.main()
