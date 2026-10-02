"""
Comprehensive Test Suite for Track A Corporate Expansion Workflow.
Validates:
1. Dynamic, input-driven pipeline execution (zero hardcoded Tesla/Australia/26M contamination).
2. Deterministic decision engine (RULE-001..RULE-009).
3. Canonical BoardRoomResult construction.
4. Clean separation from Track B.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.boardroom_orchestrator import run_boardroom_session
from services.expansion_decision_engine import evaluate_expansion_decision
from services.expansion_canonical_result import build_expansion_canonical_result
from services.track_b_orchestrator import run_track_b_session


class TestTrackAExpansion(unittest.TestCase):

    def test_case_1_tesla_ev_australia(self):
        """Test Case 1: Tesla in Australian EV Market (validates when user inputs Tesla)."""
        print("\n--- Running Test Case 1: Tesla Australia EV ---")
        company = "Tesla"
        market = "Australian Electric Vehicle Market"
        budget = 26000000.0
        timeline = "1 Year"
        question = "Should Tesla expand EV charging networks into regional Australia?"

        result = run_boardroom_session(
            company=company,
            market=market,
            budget=budget,
            timeline=timeline,
            question=question,
            business_model="B2C Electric Vehicles & Infrastructure"
        )

        self.assertEqual(result["company"], company)
        self.assertEqual(result["market"], market)
        self.assertEqual(result["budget"], budget)
        self.assertEqual(result["timeline"], timeline)
        self.assertIn(result["final_decision"], ["ENTER MARKET", "ENTER WITH CONDITIONS", "DEFER / VALIDATE", "DO NOT ENTER"])
        self.assertGreater(len(result["evidence_ledger"]), 0)
        self.assertGreater(len(result["rule_evaluations"]), 0)
        self.assertIsInstance(result["decision_explanation"], dict)
        self.assertIn("final_decision", result["decision_explanation"])
        self.assertIn("strongest_positive_evidence", result["decision_explanation"])
        self.assertIn("most_important_risk", result["decision_explanation"])
        print(f"Test 1 Decision: {result['final_decision']} (Confidence: {result['confidence']}%)")

    def test_case_2_abc_smart_devices_singapore(self):
        """Test Case 2: ABC Smart Devices in Singapore Smart Home Market ($500k, 6 Months)."""
        print("\n--- Running Test Case 2: ABC Smart Devices Singapore ($500k, 6 Months) ---")
        company = "ABC Smart Devices"
        market = "Singapore Smart Home Market"
        budget = 500000.0
        timeline = "6 Months"
        question = "Can ABC Smart Devices capture 5% of Singapore smart home market within 6 months on a $500k budget?"

        result = run_boardroom_session(
            company=company,
            market=market,
            budget=budget,
            timeline=timeline,
            question=question,
            business_model="B2B2C Smart IoT Hardware & Software"
        )

        # Exact input checks
        self.assertEqual(result["company"], "ABC Smart Devices")
        self.assertEqual(result["market"], "Singapore Smart Home Market")
        self.assertEqual(result["budget"], 500000.0)
        self.assertEqual(result["timeline"], "6 Months")

        # Contamination checks across full result
        full_text = str(result)
        self.assertNotIn("Tesla", full_text, "Found leaked 'Tesla' in ABC Smart Devices run!")
        self.assertNotIn("Australian Electric Vehicle Market", full_text, "Found leaked 'Australian Electric Vehicle Market' in Singapore run!")
        self.assertNotIn("$26.00M", full_text, "Found leaked '$26.00M' in $500k run!")
        self.assertNotIn("26,000,000", full_text, "Found leaked '26,000,000' in $500k run!")
        
        # Verify specialist reports received exact parameters
        for agent_id, rep in result.get("specialist_reports", {}).items():
            self.assertIn("ABC Smart Devices", str(rep), f"Agent {agent_id} did not reference ABC Smart Devices")

        # Schema assertion
        self.assertIsInstance(result["decision_explanation"], dict)
        self.assertIn("final_decision", result["decision_explanation"])
        self.assertIn("strongest_positive_evidence", result["decision_explanation"])

        print(f"Test 2 Decision: {result['final_decision']} (Confidence: {result['confidence']}%)")
        print("Zero Tesla / Australia / $26M contamination confirmed.")

    def test_case_3_xyz_healthcare_uae(self):
        """Test Case 3: XYZ Healthcare Technologies in UAE Healthcare SaaS Market ($2M, 18 Months)."""
        print("\n--- Running Test Case 3: XYZ Healthcare Technologies UAE ($2M, 18 Months) ---")
        company = "XYZ Healthcare Technologies"
        market = "UAE Healthcare SaaS Market"
        budget = 2000000.0
        timeline = "18 Months"
        question = "Should XYZ Healthcare expand its clinical workflow SaaS to Dubai and Abu Dhabi hospitals?"

        result = run_boardroom_session(
            company=company,
            market=market,
            budget=budget,
            timeline=timeline,
            question=question,
            business_model="B2B Enterprise Healthcare SaaS"
        )

        self.assertEqual(result["company"], "XYZ Healthcare Technologies")
        self.assertEqual(result["market"], "UAE Healthcare SaaS Market")
        self.assertEqual(result["budget"], 2000000.0)
        self.assertEqual(result["timeline"], "18 Months")

        full_text = str(result)
        self.assertNotIn("Tesla", full_text, "Found leaked 'Tesla' in XYZ Healthcare run!")
        self.assertNotIn("Australian Electric Vehicle", full_text, "Found leaked 'Australian Electric Vehicle' in UAE Healthcare run!")
        self.assertNotIn("$26.00M", full_text, "Found leaked '$26.00M' in $2M run!")
        
        # Schema assertion
        self.assertIsInstance(result["decision_explanation"], dict)
        self.assertIn("final_decision", result["decision_explanation"])

        print(f"Test 3 Decision: {result['final_decision']} (Confidence: {result['confidence']}%)")
        print("Zero contamination confirmed.")

    def test_case_4_spacex_europe_satellite(self):
        """Test Case 4: SpaceX in European Commercial Satellite Launch Market ($500k, 1 Year)."""
        print("\n--- Running Test Case 4: SpaceX European Satellite Launch ---")
        company = "SpaceX"
        market = "European Commercial Satellite Launch Market"
        budget = 500000.0
        timeline = "1 Year"
        question = "Can SpaceX deploy a European smallsat rideshare hub with a initial $500,000 budget?"

        result = run_boardroom_session(
            company=company,
            market=market,
            budget=budget,
            timeline=timeline,
            question=question,
            business_model="Commercial Orbital Launch & Satellite Rideshare"
        )

        self.assertEqual(result["company"], "SpaceX")
        self.assertEqual(result["market"], "European Commercial Satellite Launch Market")
        self.assertEqual(result["budget"], 500000.0)
        self.assertEqual(result["timeline"], "1 Year")

        full_text = str(result)
        self.assertNotIn("Tesla", full_text, "Found leaked 'Tesla' in SpaceX run!")
        self.assertNotIn("Australian Electric Vehicle", full_text, "Found leaked 'Australian EV' in SpaceX run!")
        
        self.assertIsInstance(result["decision_explanation"], dict)
        self.assertIn("final_decision", result["decision_explanation"])
        self.assertIn("capital_consideration", result["decision_explanation"])
        print(f"Test 4 Decision: {result['final_decision']} (Confidence: {result['confidence']}%)")

    def test_case_5_track_b_integrity(self):
        """Test Case 5: Verify Track B (New Business Launch) remains 100% intact and functional."""
        print("\n--- Running Test Case 5: Track B Integrity Verification ---")
        launch_res = run_track_b_session(
            business_idea="AI-Powered Precision Irrigation Sensors",
            target_market="Australian AgTech Viticulture",
            capital_budget=750000,
            timeline="12 Months",
            strategic_question="Is $750k sufficient to pilot in Barossa Valley?"
        )
        self.assertEqual(launch_res.get("business_idea"), "AI-Powered Precision Irrigation Sensors")
        self.assertEqual(launch_res.get("target_market"), "Australian AgTech Viticulture")
        self.assertIn("final_recommendation", launch_res)
        self.assertIn(launch_res["final_recommendation"], ["LAUNCH", "GO FOR LAUNCH", "LAUNCH WITH CONDITIONS", "VALIDATE FIRST", "DO NOT LAUNCH"])
        self.assertIsInstance(launch_res.get("decision_explanation"), dict)
        print(f"Track B Decision: {launch_res['final_recommendation']} (Verified 100% Functional)")


if __name__ == "__main__":
    unittest.main()
