"""
BoardRoomAI — Track B Dynamic Launch Scoring Regression Test Suite.
Verifies all 10 core requirements:
1. Different budgets produce different capital feasibility when other factors differ.
2. Unrealistic timelines reduce launch readiness.
3. Severe unresolved risks reduce risk mitigation.
4. Weak opportunities do not automatically receive 100%.
5. Different proposals produce different overall scores.
6. Scores remain within 0-100 range.
7. Scores are 100% deterministic and reproducible.
8. No random scoring is used.
9. Missing analysis does not produce 100%.
10. UI and PDF use the same canonical scores.
"""

import sys
import os
import unittest
import io
import pypdf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.track_b_scoring_engine import calculate_launch_scores, parse_budget_numeric, parse_timeline_months
from services.track_b_orchestrator import run_track_b_session, calculate_track_b_consensus
from services.report_generator import generate_pdf_report


class TestTrackBDynamicScoring(unittest.TestCase):

    def test_01_different_budgets_produce_different_capital_feasibility(self):
        """Verify that scaling the budget for the same venture dynamically changes capital feasibility."""
        idea = "Autonomous AI Drone Delivery Fleet"
        market = "India"
        timeline = "12 Months"

        score_low = calculate_launch_scores(idea, market, budget=10_000, timeline=timeline)
        score_mid = calculate_launch_scores(idea, market, budget=150_000, timeline=timeline)
        score_high = calculate_launch_scores(idea, market, budget=1_000_000, timeline=timeline)

        cap_low = score_low["capital_feasibility_score"]
        cap_mid = score_mid["capital_feasibility_score"]
        cap_high = score_high["capital_feasibility_score"]

        self.assertLess(cap_low, cap_mid, f"Low budget ({cap_low}) must be less than mid budget ({cap_mid})")
        self.assertLess(cap_mid, cap_high, f"Mid budget ({cap_mid}) must be less than high budget ({cap_high})")
        self.assertNotEqual(cap_low, 100)

    def test_02_unrealistic_timeline_reduces_launch_readiness(self):
        """Verify that a short/unrealistic timeline produces lower launch readiness."""
        idea = "Autonomous Passenger Air Taxi Network"
        market = "India"
        budget = 500_000

        score_3m = calculate_launch_scores(idea, market, budget, timeline="3 Months")
        score_12m = calculate_launch_scores(idea, market, budget, timeline="12 Months")
        score_36m = calculate_launch_scores(idea, market, budget, timeline="36 Months")

        rdy_3m = score_3m["launch_readiness_score"]
        rdy_12m = score_12m["launch_readiness_score"]
        rdy_36m = score_36m["launch_readiness_score"]

        self.assertLess(rdy_3m, rdy_12m, f"3m readiness ({rdy_3m}) must be lower than 12m ({rdy_12m})")
        self.assertLess(rdy_12m, rdy_36m, f"12m readiness ({rdy_12m}) must be lower than 36m ({rdy_36m})")
        self.assertLess(rdy_3m, 20, f"3m for air taxi must be critically low, got {rdy_3m}")

    def test_03_severe_unresolved_risks_reduce_risk_mitigation(self):
        """Verify that presence of high severity risks and critical blockers lowers risk mitigation."""
        idea = "AI Drone Delivery Service"
        market = "India"

        # Baseline with no severe blockers
        clean_scores = calculate_launch_scores(idea, market, 500_000, "12 Months", risk_matrix=[])

        # With multiple high risks and critical blocker
        risky_matrix = [
            {"level": "HIGH", "category": "CAPITAL RISK"},
            {"level": "HIGH", "category": "REGULATORY RISK"},
            {"level": "HIGH", "category": "OPERATIONAL RISK"}
        ]
        crit_blockers = [
            {"severity": "CRITICAL", "title": "Civil Aviation Airspace Prohibition"}
        ]
        risky_scores = calculate_launch_scores(
            idea, market, 500_000, "12 Months",
            risk_matrix=risky_matrix,
            critical_blockers=crit_blockers
        )

        self.assertGreater(clean_scores["risk_mitigation_score"], risky_scores["risk_mitigation_score"])
        self.assertLess(risky_scores["risk_mitigation_score"], 60)

    def test_04_weak_opportunities_do_not_receive_100(self):
        """Verify that weak or unviable opportunities do not automatically receive 100%."""
        mock_reports = {
            "MARKET_VALIDATOR": {"recommendation": "NO", "confidence": 90, "data_verified": True},
            "COMPETITIVE_SCOUT": {"recommendation": "NO", "confidence": 85, "data_verified": True}
        }
        scores = calculate_launch_scores(
            venture_idea="Unrealistic Commodity Device",
            target_market="India",
            budget=50_000,
            timeline="6 Months",
            specialist_reports=mock_reports
        )
        self.assertLess(scores["opportunity_score"], 40)
        self.assertNotEqual(scores["opportunity_score"], 100)

    def test_05_different_proposals_produce_different_overall_scores(self):
        """Verify that the 4 distinct user proposals produce meaningfully distinct scores."""
        cases = [
            ("Drone India", "AI-powered autonomous drone delivery service for urban last-mile deliveries.", "India", 100000, "6 Months"),
            ("Cloud UK", "AI-powered cloud accounting and financial forecasting platform for small businesses.", "United Kingdom", 400000, "12 Months"),
            ("Air Taxi India", "Build a nationwide autonomous passenger air taxi network.", "India", 10000, "3 Months"),
            ("Logistics SG", "AI-powered logistics optimization SaaS for commercial logistics companies.", "Singapore", 750000, "18 Months")
        ]
        scores_list = []
        for name, idea, country, budget, timeline in cases:
            s = calculate_launch_scores(idea, country, budget, timeline)
            scores_list.append((name, s))

        # Check all overall scores are not identical
        overall_values = [s["overall_launch_score"] for _, s in scores_list]
        self.assertGreater(len(set(overall_values)), 1, "Overall scores must not all be identical!")

        # Check Test A and Test C have low overall score compared to Test B and Test D
        drone_ovr = scores_list[0][1]["overall_launch_score"]
        cloud_ovr = scores_list[1][1]["overall_launch_score"]
        air_taxi_ovr = scores_list[2][1]["overall_launch_score"]
        logistics_ovr = scores_list[3][1]["overall_launch_score"]

        self.assertLess(drone_ovr, cloud_ovr)
        self.assertLess(air_taxi_ovr, cloud_ovr)
        self.assertLess(cloud_ovr, logistics_ovr)

    def test_06_scores_remain_within_0_100_range(self):
        """Verify all calculated scores stay strictly between 0 and 100."""
        extreme_budgets = [1, 10, 50_000, 1_000_000, 100_000_000]
        extreme_timelines = ["1 Day", "1 Month", "6 Months", "5 Years", "10 Years"]

        for b in extreme_budgets:
            for t in extreme_timelines:
                s = calculate_launch_scores("Generic Venture", "India", b, t)
                for k in ["opportunity_score", "risk_mitigation_score", "launch_readiness_score", "capital_feasibility_score", "overall_launch_score"]:
                    val = s[k]
                    self.assertTrue(0 <= val <= 100, f"{k} value {val} out of 0-100 range for budget={b}, timeline={t}")

    def test_07_scores_are_deterministic(self):
        """Verify that repeated evaluation of identical inputs produces identical scores without drift."""
        idea = "Precision Agriculture Sensor Network"
        market = "Australia"
        budget = 350000
        timeline = "12 Months"

        first_run = calculate_launch_scores(idea, market, budget, timeline)
        for _ in range(5):
            repeated_run = calculate_launch_scores(idea, market, budget, timeline)
            self.assertEqual(first_run["opportunity_score"], repeated_run["opportunity_score"])
            self.assertEqual(first_run["risk_mitigation_score"], repeated_run["risk_mitigation_score"])
            self.assertEqual(first_run["launch_readiness_score"], repeated_run["launch_readiness_score"])
            self.assertEqual(first_run["capital_feasibility_score"], repeated_run["capital_feasibility_score"])
            self.assertEqual(first_run["overall_launch_score"], repeated_run["overall_launch_score"])

    def test_08_missing_analysis_does_not_produce_100(self):
        """Verify missing or unverified analysis does not silently default to 100%."""
        empty_reports = {}
        s = calculate_launch_scores("Unknown Venture", "Unlisted Market", 100000, "6 Months", specialist_reports=empty_reports)
        self.assertNotEqual(s["opportunity_score"], 100)
        self.assertNotEqual(s["capital_feasibility_score"], 100)
        self.assertNotEqual(s["launch_readiness_score"], 100)
        self.assertNotEqual(s["overall_launch_score"], 100)

    def test_09_extreme_negative_cases_cannot_produce_100(self):
        """Assert extreme negative cases (Passenger Air Taxi with $10k) cannot produce 100% across KPIs."""
        s = calculate_launch_scores(
            venture_idea="Build a nationwide autonomous passenger air taxi network.",
            target_market="India",
            budget=10000,
            timeline="3 Months"
        )
        self.assertLess(s["capital_feasibility_score"], 15)
        self.assertLess(s["launch_readiness_score"], 15)
        self.assertLess(s["overall_launch_score"], 30)

        # Assert not 100%
        self.assertFalse(
            s["capital_feasibility_score"] == 100 and s["launch_readiness_score"] == 100 and s["overall_launch_score"] == 100,
            "Extreme negative proposal must never produce 100% across metrics"
        )

    def test_10_canonical_scores_used_identically_in_consensus_and_pdf(self):
        """Verify that UI consensus and PDF generation receive the exact same canonical score values."""
        res = run_track_b_session(
            business_idea="AI-powered cloud accounting and financial forecasting platform for small businesses.",
            target_market="United Kingdom",
            capital_budget=400000,
            timeline="12 Months",
            strategic_question="Should we launch an AI cloud accounting platform in the UK?"
        )
        cm = res["consensus_metrics"]
        self.assertEqual(res["opportunity_score"], cm["opportunity_score"])
        self.assertEqual(res["capital_feasibility_score"], cm["capital_feasibility_score"])
        self.assertEqual(res["launch_readiness_score"], cm["launch_readiness_score"])
        self.assertEqual(res["risk_mitigation_score"], cm["risk_mitigation_score"])

        # Compile PDF and ensure no crash
        pdf_bytes = generate_pdf_report(res)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        self.assertGreater(len(reader.pages), 0)


if __name__ == "__main__":
    unittest.main()
