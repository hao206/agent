"""
Unit tests for Preliminary Risk & Assumption Auditor Node.
"""
import unittest
from src.foundation.schemas.project_brief import ProjectBrief
from src.foundation.agents.risk_auditor import risk_auditor_node, check_zoning_violations


class TestRiskAuditor(unittest.TestCase):

    def test_normal_case_passes_screening(self):
        brief = ProjectBrief(
            location="Hà Nội",
            land_area_m2=100.0,
            num_floors=3,
            budget_vnd=3_000_000_000.0,
        )
        state = {
            "project_brief": brief.model_dump(),
            "cost_breakdown": {"total_cost_vnd": 2_700_000_000.0},
            "revision_count": 0,
        }
        res = risk_auditor_node(state)
        self.assertFalse(res["needs_revision"])
        self.assertEqual(res["status"], "PASSED_QA")

    def test_zoning_heuristic_warning(self):
        # 45m2 land plot with 8 floors triggers preliminary zoning warning
        brief = ProjectBrief(
            location="Hà Nội",
            land_area_m2=45.0,
            num_floors=8,
        )
        risks = check_zoning_violations(brief)
        self.assertGreater(len(risks), 0)
        self.assertEqual(risks[0].severity, "high")
        self.assertIn("Preliminary Warning", risks[0].message)

    def test_budget_overrun_warning(self):
        brief = ProjectBrief(
            location="Đà Nẵng",
            land_area_m2=100.0,
            num_floors=3,
            budget_vnd=2_000_000_000.0,  # 2.0B budget
        )
        state = {
            "project_brief": brief.model_dump(),
            "cost_breakdown": {"total_cost_vnd": 2_750_000_000.0}, # 2.75B estimate > 2.0B budget
            "revision_count": 0,
        }
        res = risk_auditor_node(state)
        self.assertGreater(len(res["risks"]), 0)
        budget_risk = [r for r in res["risks"] if r["type"] == "budget_overrun"]
        self.assertGreater(len(budget_risk), 0)


if __name__ == "__main__":
    unittest.main()
