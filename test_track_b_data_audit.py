"""
test_track_b_data_audit.py
Comprehensive Data-Grounding, Metric & Decision Audit Test Suite for Track B
Tests 1 to 9 as specified in STEP 5 of BoardRoomAI.
"""

import json
import unittest
from unittest.mock import patch, MagicMock

import config
import services.data_service as ds
from services.track_b_orchestrator import (
    run_track_b_session,
    calculate_track_b_consensus,
    TRACK_B_AGENTS
)
from services.boardroom_orchestrator import run_boardroom_session, CORE_AGENTS
from agents.market_validator_agent import validate_market
from agents.competitive_scout_agent import scout_competition
from agents.regulatory_navigator_agent import navigate_regulations
from agents.launch_operations_agent import evaluate_launch_operations
from agents.venture_risk_agent import assess_venture_risk
from agents.capital_strategist_agent import strategize_capital, parse_currency_value, format_budget
from agents.founder_ceo_agent import decide_founder_ceo


def create_mock_completion(content_str):
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = content_str
    return mock_resp


class TestTrackBDataAudit(unittest.TestCase):

    def setUp(self):
        self.specialist_mock_json = json.dumps({
            "analysis": "Empirical startup ecosystem and infrastructure data verified. Conditions support entry.",
            "recommendation": "YES",
            "confidence": 85,
            "dialogue": "Data benchmarks indicate positive environment.",
            "mind_change_threshold": "If licensing costs exceed 25% of launch budget."
        })
        
        self.ceo_mock_json = json.dumps({
            "analysis": "Synthesized 6 specialist reports. Market demand and regulatory alignment support strategic launch.",
            "recommendation": "LAUNCH",
            "confidence": 88,
            "dialogue": "We have alignment across the venture board.",
            "validation_roadmap": [
                "1. Conduct 25 customer discovery interviews to address Market Validator demand validation.",
                "2. Submit formal incorporation and licensing paperwork to address Regulatory Navigator requirements.",
                "3. Deploy pilot MVP with tight burn rate controls to address Capital Strategist budget benchmarks.",
                "4. Secure local supplier MOUs to address Launch Operations supply chain logistics."
            ]
        })

    # =========================================================================
    # TEST 1: Valid Country + Valid Business Idea (Real Data Retrieved)
    # =========================================================================
    def test_01_valid_country_real_data(self):
        print("\n--- TEST 1: Valid Country (Australia) Real Data Retrieval ---")
        
        def llm_side_effect(*args, **kwargs):
            messages = kwargs.get("messages", [])
            content = str(messages)
            if "FOUNDER_CEO" in content or "Founder CEO" in content:
                return create_mock_completion(self.ceo_mock_json)
            return create_mock_completion(self.specialist_mock_json)

        with patch('time.sleep', return_value=None):
            with patch.object(config.client.chat.completions, 'create', side_effect=llm_side_effect):
                result = run_track_b_session(
                    business_idea="Autonomous AI Precision Agriculture Drone Platform",
                    target_market="Australia",
                    capital_budget=500000,
                    timeline="12 months",
                    strategic_question="Should we launch an AI drone agriculture platform in Australia?"
                )
                
                self.assertEqual(result["mode"], "launch")
                self.assertTrue(result["data_verified"], "Australia must have data_verified=True")
                self.assertIn(result["final_recommendation"], ["LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"])
                self.assertEqual(len(result["specialist_reports"]), 7)
                
                # Check individual specialist data verification
                for agent_id, rep in result["specialist_reports"].items():
                    self.assertTrue(rep["data_verified"], f"Agent {agent_id} data_verified must be True for Australia")
                    self.assertIn(rep["recommendation"], ["YES", "NO", "MAYBE", "LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"])

    # =========================================================================
    # TEST 2: Unknown Country (No Fabricated Metrics)
    # =========================================================================
    def test_02_unknown_country_no_fabrication(self):
        print("\n--- TEST 2: Unknown Country (Atlantis) Data Flagging ---")
        
        def llm_side_effect(*args, **kwargs):
            return create_mock_completion(self.specialist_mock_json)

        with patch('time.sleep', return_value=None):
            with patch.object(config.client.chat.completions, 'create', side_effect=llm_side_effect):
                result = run_track_b_session(
                    business_idea="Subsea Sensor Grid",
                    target_market="Atlantis",
                    capital_budget=250000,
                    timeline="6 months",
                    strategic_question="Should we deploy in Atlantis?"
                )
                
                self.assertFalse(result["data_verified"], "Atlantis must have data_verified=False")
                for agent_id in ["MARKET_VALIDATOR", "COMPETITIVE_SCOUT", "REGULATORY_NAVIGATOR", "LAUNCH_OPERATIONS", "VENTURE_RISK", "CAPITAL_STRATEGIST"]:
                    rep = result["specialist_reports"][agent_id]
                    self.assertFalse(rep["data_verified"], f"{agent_id} must flag data_verified=False for unknown country")

    # =========================================================================
    # TEST 3: Missing Research Benchmark (Capital Strategist Does Not Invent X)
    # =========================================================================
    def test_03_missing_research_benchmark(self):
        print("\n--- TEST 3: Missing Research Benchmark Handling ---")
        
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(self.specialist_mock_json)) as mock_llm:
            rep = strategize_capital(
                business_idea="Quantum Encryption Hardware",
                target_market="Wakanda",
                capital_budget=1000000,
                timeline="18 months",
                strategic_question="Is capital sizing adequate in Wakanda?"
            )
            
            self.assertFalse(rep["data_verified"], "Capital strategist must mark data_verified=False when benchmark missing")
            call_kwargs = mock_llm.call_args[1]
            prompt_sent = str(call_kwargs.get("messages", []))
            self.assertIn("No verified startup ecosystem funding benchmark found", prompt_sent)

    # =========================================================================
    # TEST 4: Proposed Budget > Benchmark (ABOVE)
    # =========================================================================
    def test_04_budget_above_benchmark(self):
        print("\n--- TEST 4: Proposed Budget > Benchmark (ABOVE) ---")
        # Australia avg startup funding is ~$7.63M. We test $20M USD budget (> 1.20 * 7.63M)
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(self.specialist_mock_json)) as mock_llm:
            rep = strategize_capital(
                business_idea="AI Agritech",
                target_market="Australia",
                capital_budget=20000000,
                timeline="12 months",
                strategic_question="Capital feasibility check?"
            )
            
            call_kwargs = mock_llm.call_args[1]
            prompt_sent = str(call_kwargs.get("messages", []))
            self.assertIn("is ABOVE the local startup funding benchmark", prompt_sent)
            self.assertTrue(rep["data_verified"])

    # =========================================================================
    # TEST 5: Proposed Budget < Benchmark (BELOW)
    # =========================================================================
    def test_05_budget_below_benchmark(self):
        print("\n--- TEST 5: Proposed Budget < Benchmark (BELOW) ---")
        # Australia avg startup funding is ~$7.63M. We test $500,000 USD budget (< 0.80 * 7.63M)
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(self.specialist_mock_json)) as mock_llm:
            rep = strategize_capital(
                business_idea="AI Agritech",
                target_market="Australia",
                capital_budget=500000,
                timeline="12 months",
                strategic_question="Capital feasibility check?"
            )
            
            call_kwargs = mock_llm.call_args[1]
            prompt_sent = str(call_kwargs.get("messages", []))
            self.assertIn("is BELOW the local startup funding benchmark", prompt_sent)
            self.assertTrue(rep["data_verified"])

    # =========================================================================
    # TEST 6: Proposed Budget ~ Benchmark (IN LINE WITH)
    # =========================================================================
    def test_06_budget_in_line_benchmark(self):
        print("\n--- TEST 6: Proposed Budget ~ Benchmark (IN LINE WITH) ---")
        # Australia avg startup funding is $7,634,195. We test $7,500,000 USD budget (within +-20%)
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(self.specialist_mock_json)) as mock_llm:
            rep = strategize_capital(
                business_idea="AI Agritech",
                target_market="Australia",
                capital_budget=7500000,
                timeline="12 months",
                strategic_question="Capital feasibility check?"
            )
            
            call_kwargs = mock_llm.call_args[1]
            prompt_sent = str(call_kwargs.get("messages", []))
            self.assertIn("is IN LINE WITH the local startup funding benchmark", prompt_sent)
            self.assertTrue(rep["data_verified"])

    # =========================================================================
    # TEST 7: Unsupported Financial Metric Detection
    # =========================================================================
    def test_07_no_unsupported_financial_metrics(self):
        print("\n--- TEST 7: Unsupported Financial Metric Audit ---")
        # Verify currency parser handles real units
        self.assertEqual(parse_currency_value("7.63 Million"), 7630000.0)
        self.assertEqual(parse_currency_value("$138,372"), 138372.0)
        self.assertEqual(parse_currency_value("1.57 Billion"), 1570000000.0)
        self.assertIsNone(parse_currency_value("N/A"))
        
        # Verify budget formatting does not produce $500,000M
        self.assertEqual(format_budget(500000), "$500,000 USD")
        self.assertEqual(format_budget(1500000), "$1.50 Million USD")
        
        # Verify Capital Strategist role description in orchestrator
        cap_agent = next(a for a in TRACK_B_AGENTS if a["id"] == "CAPITAL_STRATEGIST")
        self.assertNotIn("yield", cap_agent["role"].lower())
        self.assertNotIn("npv", cap_agent["role"].lower())
        self.assertNotIn("roi", cap_agent["role"].lower())

    # =========================================================================
    # TEST 8: Founder CEO Validation Roadmap Traceability
    # =========================================================================
    def test_08_founder_ceo_roadmap_traceability(self):
        print("\n--- TEST 8: Founder CEO Validation Roadmap Traceability ---")
        specialist_reports = {
            "MARKET_VALIDATOR": {"recommendation": "YES", "confidence": 80, "analysis": "Demand exists but churn risk is unmeasured.", "data_verified": True},
            "COMPETITIVE_SCOUT": {"recommendation": "MAYBE", "confidence": 75, "analysis": "Incumbents dominate enterprise segment.", "data_verified": True},
            "REGULATORY_NAVIGATOR": {"recommendation": "YES", "confidence": 90, "analysis": "Registration takes 2 days.", "data_verified": True},
            "LAUNCH_OPERATIONS": {"recommendation": "YES", "confidence": 85, "analysis": "High LPI logistics score.", "data_verified": True},
            "VENTURE_RISK": {"recommendation": "YES", "confidence": 85, "analysis": "Stable macroeconomic climate.", "data_verified": True},
            "CAPITAL_STRATEGIST": {"recommendation": "MAYBE", "confidence": 70, "analysis": "Budget is below average startup funding.", "data_verified": True}
        }
        
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(self.ceo_mock_json)):
            res = decide_founder_ceo(
                business_idea="Precision Agritech AI",
                target_market="Australia",
                capital_budget=500000,
                timeline="12 months",
                strategic_question="Launch decision?",
                specialist_reports=specialist_reports
            )
            
            self.assertIn(res["recommendation"], ["LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"])
            self.assertIsInstance(res["validation_roadmap"], list)
            self.assertTrue(3 <= len(res["validation_roadmap"]) <= 5)
            
            # Check specialist references in roadmap
            roadmap_text = " ".join(res["validation_roadmap"])
            has_specialist_reference = any(
                specialist in roadmap_text for specialist in 
                ["Market", "Validator", "Regulatory", "Navigator", "Capital", "Strategist", "Operations", "Scout", "Risk"]
            )
            self.assertTrue(has_specialist_reference, "Validation roadmap items must cite named specialist concerns")

    # =========================================================================
    # TEST 9: Track A Regression Suite
    # =========================================================================
    def test_09_track_a_regression(self):
        print("\n--- TEST 9: Track A Regression (Corporate Expansion Protection) ---")
        
        csuite_mock_json = json.dumps({
            "analysis": "Corporate market expansion metrics validated. High ROI and operational synergy.",
            "recommendation": "GO",
            "confidence": 88,
            "dialogue": "Expansion is strategically aligned with global objectives.",
            "mind_change_threshold": "If corporate tax exceeds 35%."
        })
        
        ceo_track_a_mock = json.dumps({
            "analysis": "Unanimous board approval. Expansion into target territory is fully greenlit.",
            "recommendation": "GO",
            "confidence": 92,
            "dialogue": "We proceed immediately with expansion.",
            "validation_roadmap": [
                "1. Establish local subsidiary.",
                "2. Finalize distributor contracts."
            ]
        })
        
        def track_a_side_effect(*args, **kwargs):
            messages = kwargs.get("messages", [])
            content = str(messages)
            if "CEO" in content and "FOUNDER" not in content:
                return create_mock_completion(ceo_track_a_mock)
            return create_mock_completion(csuite_mock_json)
            
        with patch('time.sleep', return_value=None):
            with patch.object(config.client.chat.completions, 'create', side_effect=track_a_side_effect):
                result_a = run_boardroom_session(
                    company="Tesla",
                    market="Australia",
                    budget=50.0,
                    timeline="12 months",
                    question="Should Tesla expand Supercharger network in Australia?"
                )
                
                self.assertIn(result_a["ceo_decision"], ["GO", "NO-GO", "CONDITIONAL GO", "DELAY ENTRY"])
                self.assertEqual(len(result_a["board_reports"]), 7)  # 6 C-Suite agents + 1 CEO report
                self.assertEqual(len(CORE_AGENTS), 6)
                self.assertIn("consensus_metrics", result_a)
                print("Track A executed successfully with intact C-Suite agents, consensus metrics, and decision schema.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
