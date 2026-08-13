"""
Unit tests for Deterministic Estimation Math Engine.
"""
import unittest
from src.math_engine import (
    calculate_gross_floor_area,
    estimate_concrete_volume,
    estimate_steel_tonnage,
    estimate_brick_count,
    calculate_construction_cost_breakdown,
)


class TestMathEngine(unittest.TestCase):

    def test_gfa_calculation(self):
        # 100m2 land, 3 floors, strip foundation (0.50), flat concrete roof (0.50)
        # GFA = 100*0.5 + 300 + 100*0.5 = 400.0 m2
        gfa = calculate_gross_floor_area(100.0, 3, "strip", "flat_concrete")
        self.assertEqual(gfa, 400.0)

    def test_gfa_invalid_inputs(self):
        with self.assertRaises(ValueError):
            calculate_gross_floor_area(0, 3)
        with self.assertRaises(ValueError):
            calculate_gross_floor_area(100, 0)

    def test_takeoff_estimates(self):
        gfa = 400.0
        self.assertEqual(estimate_concrete_volume(gfa), 140.0)   # 400 * 0.35
        self.assertEqual(estimate_steel_tonnage(gfa), 40.0)       # 400 * 100 / 1000
        self.assertEqual(estimate_brick_count(gfa), 32000)        # 400 * 80

    def test_cost_breakdown_tcvn_rules(self):
        boq = calculate_construction_cost_breakdown(
            land_area_m2=100.0,
            num_floors=3,
            foundation_type="strip",
            roof_type="flat_concrete",
            quality_tier="medium",
        )
        self.assertEqual(boq.gfa_m2, 400.0)
        
        # Medium prices: rough=3.6M, finishing=2.4M, labor=1.5M
        # Foundation = 50 * 3.6M = 180M
        self.assertEqual(boq.cost_breakdown.foundation_vnd, 180_000_000.0)
        # Finishing = 300 * 2.4M = 720M (strictly usable floor area)
        self.assertEqual(boq.cost_breakdown.finishing_vnd, 720_000_000.0)
        # Labor cost = (300 + 50) * 1.5M = 525M
        # Subtotal = 180M + 1260M + 720M + 525M = 2685M
        # Contingency 5% = 2685M * 0.05 = 134.25M
        self.assertEqual(boq.cost_breakdown.contingency_vnd, 134_250_000.0)
        self.assertEqual(boq.total_cost_vnd, 2_834_250_000.0)
        self.assertGreater(len(boq.assumptions_applied), 0)


if __name__ == "__main__":
    unittest.main()
