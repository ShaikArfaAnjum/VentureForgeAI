"""
test_step_6_hardening.py
Verification suite for STEP 6: Master Hardening of Track B & Protection of Track A.
Tests A through H as defined in Step 6 specifications.
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
from agents.capital_strategist_agent import strategize_capital, parse_currency_value, format_budget
from agents.founder_ceo_agent import decide_founder_ceo


def create_mock_completion(content_str):
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = content_str
    return mock_resp


class TestStep6Hardening(unittest.TestCase):

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
    # TEST A: Valid Country (All Required Datasets Available)
    # =========================================================================
    def test_A_valid_country(self):
        print("\n--- TEST A: Valid Country (Australia) Full Verification ---")
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
                self.assertTrue(result["data_verified"])
                self.assertTrue(result["data_verified_overall"])
                self.assertEqual(result["status"], "success")
                self.assertIn(result["final_recommendation"], ["LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"])
                self.assertEqual(len(result["specialist_reports"]), 7)
                for agent_id in ["MARKET_VALIDATOR", "COMPETITIVE_SCOUT", "REGULATORY_NAVIGATOR", "LAUNCH_OPERATIONS", "VENTURE_RISK", "CAPITAL_STRATEGIST"]:
                    rep = result["specialist_reports"][agent_id]
                    self.assertTrue(rep["data_verified"])
                    self.assertEqual(rep.get("status"), "success")

    # =========================================================================
    # TEST B: Unknown Country ("Atlantis")
    # =========================================================================
    def test_B_unknown_country(self):
        print("\n--- TEST B: Unknown Country (Atlantis) No Fabrication ---")
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
                
                self.assertFalse(result["data_verified"])
                self.assertFalse(result["data_verified_overall"])
                self.assertEqual(result["status"], "data_unavailable")
                for agent_id in ["MARKET_VALIDATOR", "COMPETITIVE_SCOUT", "REGULATORY_NAVIGATOR", "LAUNCH_OPERATIONS", "VENTURE_RISK", "CAPITAL_STRATEGIST"]:
                    rep = result["specialist_reports"][agent_id]
                    self.assertFalse(rep["data_verified"], f"{agent_id} data_verified must be False")
                    self.assertEqual(rep.get("status"), "data_unavailable")

    # =========================================================================
    # TEST C: Missing Research Benchmark
    # =========================================================================
    def test_C_missing_research_benchmark(self):
        print("\n--- TEST C: Missing Research Benchmark ---")
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(self.specialist_mock_json)) as mock_llm:
            rep = strategize_capital(
                business_idea="Quantum Encryption Hardware",
                target_market="Wakanda",
                capital_budget=1000000,
                timeline="18 months",
                strategic_question="Is capital sizing adequate in Wakanda?"
            )
            
            self.assertFalse(rep["data_verified"])
            call_kwargs = mock_llm.call_args[1]
            prompt_sent = str(call_kwargs.get("messages", []))
            self.assertIn("No verified startup ecosystem funding benchmark found", prompt_sent)

    # =========================================================================
    # TEST D: LLM / Tool Execution Failure (Clear Agent Error State)
    # =========================================================================
    def test_D_execution_failure_state(self):
        print("\n--- TEST D: Execution Failure State Tracking ---")
        
        failing_mock = MagicMock(side_effect=RuntimeError("Groq Connection Timeout (504)"))
        
        with patch('time.sleep', return_value=None):
            with patch.dict(TRACK_B_AGENTS[1], {"function": failing_mock}):
                with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(self.specialist_mock_json)):
                    result = run_track_b_session(
                        business_idea="AgriDrone",
                        target_market="Australia",
                        capital_budget=500000,
                        timeline="12 months",
                        strategic_question="Viability check?"
                    )
                    
                    cs_report = result["specialist_reports"]["COMPETITIVE_SCOUT"]
                    self.assertEqual(cs_report["status"], "error")
                    self.assertIn("504", cs_report["error_message"])
                    self.assertEqual(cs_report["confidence"], 0)
                    self.assertFalse(cs_report["data_verified"])
                    self.assertEqual(result["status"], "error")

    # =========================================================================
    # TEST E: Malformed Specialist Response
    # =========================================================================
    def test_E_malformed_specialist_response(self):
        print("\n--- TEST E: Malformed Response Error Handling ---")
        # Return invalid unparseable string from LLM
        malformed_mock = create_mock_completion("THIS IS NOT JSON AT ALL {{{ broken syntax")
        
        with patch('time.sleep', return_value=None):
            with patch.object(config.client.chat.completions, 'create', return_value=malformed_mock):
                rep = config.call_groq_api(
                    prompt="test",
                    system_prompt="test",
                    agent_role="MARKET_VALIDATOR",
                    company="Idea",
                    market="Australia",
                    budget=500000,
                    timeline="12m",
                    question="Q"
                )
                
                self.assertIn("[PARSING ERROR]", rep["analysis"])
                self.assertEqual(rep["confidence"], 0)

    # =========================================================================
    # TEST F: Track A Regression
    # =========================================================================
    def test_F_track_a_regression(self):
        print("\n--- TEST F: Track A Regression ---")
        csuite_mock_json = json.dumps({
            "analysis": "Expansion into target market is supported by positive ROI and operations synergy.",
            "recommendation": "GO",
            "confidence": 88,
            "dialogue": "Expansion is strategically sound.",
            "mind_change_threshold": "If corporate tax exceeds 35%."
        })
        
        ceo_track_a_mock = json.dumps({
            "analysis": "Consensus reached. Corporate expansion approved.",
            "recommendation": "GO",
            "confidence": 90,
            "dialogue": "We proceed with expansion.",
            "validation_roadmap": [
                "1. Establish local subsidiary."
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
                    question="Should Tesla expand Superchargers in Australia?"
                )
                
                self.assertIn(result_a["ceo_decision"], ["GO", "NO-GO", "CONDITIONAL GO", "DELAY ENTRY"])
                self.assertEqual(len(result_a["board_reports"]), 7)
                self.assertEqual(len(CORE_AGENTS), 6)
                self.assertIn("consensus_metrics", result_a)

    # =========================================================================
    # TEST G: Track B Successful Execution
    # =========================================================================
    def test_G_track_b_successful_execution(self):
        print("\n--- TEST G: Track B Successful Execution ---")
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
                    strategic_question="Should we launch?"
                )
                
                self.assertEqual(result["final_recommendation"], "LAUNCH")
                self.assertEqual(result["ceo_confidence"], 88)
                self.assertTrue(3 <= len(result["validation_roadmap"]) <= 5)
                self.assertEqual(len(result["transcript"]), 7)

    # =========================================================================
    # TEST H: Track B With One Unavailable Specialist
    # =========================================================================
    def test_H_one_unavailable_specialist(self):
        print("\n--- TEST H: Track B With One Unavailable Specialist ---")
        
        orig_get_data = ds.get_data
        def mocked_get_data(data_type, **kwargs):
            if data_type == "Risk Data":
                return {"status": "unavailable", "source": "None", "data": {}}
            return orig_get_data(data_type, **kwargs)

        with patch('time.sleep', return_value=None):
            with patch('services.data_service.get_data', side_effect=mocked_get_data):
                with patch('agents.venture_risk_agent.get_data', side_effect=mocked_get_data):
                    with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(self.specialist_mock_json)):
                        result = run_track_b_session(
                            business_idea="AgriDrone",
                            target_market="Australia",
                            capital_budget=500000,
                            timeline="12 months",
                            strategic_question="Viability check?"
                        )
                        
                        # Venture Risk must be data_verified=False
                        vr_report = result["specialist_reports"]["VENTURE_RISK"]
                        self.assertFalse(vr_report["data_verified"])
                        
                        # Overall data_verified must be False
                        self.assertFalse(result["data_verified"])
                        self.assertFalse(result["data_verified_overall"])
                        self.assertEqual(result["status"], "data_unavailable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
