import json
import time
import unittest
from unittest.mock import patch, MagicMock

import services.data_service as ds
import config
from services.track_b_orchestrator import (
    run_track_b_session,
    calculate_track_b_consensus,
    run_strategic_session,
    TRACK_B_AGENTS
)
from services.boardroom_orchestrator import run_boardroom_session, CORE_AGENTS

def create_mock_completion(content_str):
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = content_str
    return mock_resp

def run_tests():
    print("==================================================")
    print("RUNNING TRACK B ORCHESTRATOR TESTS (TESTS 1 - 6)")
    print("==================================================")

    # ----------------------------------------------------
    # TEST 1: Valid Launch (Australia)
    # ----------------------------------------------------
    print("\n--- TEST 1: Valid Launch Simulation (Australia) ---")
    specialist_mock_json = json.dumps({
        "analysis": "Verified market conditions and ecosystem metrics in Australia indicate high strategic viability.",
        "recommendation": "YES",
        "confidence": 85,
        "dialogue": "Conditions are ripe for launch.",
        "mind_change_threshold": "If regulatory approval timeline exceeds 180 days."
    })
    
    ceo_mock_json = json.dumps({
        "analysis": "Synthesized unanimous specialist support. Market momentum and regulatory ease indicate high venture viability.",
        "recommendation": "LAUNCH",
        "confidence": 90,
        "dialogue": "All board specialists approve. Let us proceed to launch.",
        "validation_roadmap": [
            "1. Run 20 customer discovery interviews to address initial adoption concerns.",
            "2. Pilot with 3 commercial partners to validate Launch Operations logistics.",
            "3. Obtain formal tax and registration clearance to address Regulatory Navigator guidelines."
        ]
    })
    
    def llm_side_effect(*args, **kwargs):
        messages = kwargs.get("messages", [])
        content = messages[-1]["content"] if messages else ""
        if "Founder CEO" in content or "FOUNDER_CEO" in str(args) or "Founder CEO" in str(messages):
            return create_mock_completion(ceo_mock_json)
        return create_mock_completion(specialist_mock_json)
        
    with patch('time.sleep', return_value=None):
        with patch.object(config.client.chat.completions, 'create', side_effect=llm_side_effect):
            events = []
            def test_callback(agent_id, status, dialogue, consensus):
                events.append((agent_id, status))
                
            result = run_track_b_session(
                business_idea="AI Precision Agriculture Platform",
                target_market="Australia",
                capital_budget=1.5,
                timeline="12 months",
                strategic_question="Should we launch an AI agritech platform in Australia?",
                progress_callback=test_callback
            )
            
            print(f"Final Decision: {result['final_recommendation']}")
            print(f"CEO Confidence: {result['ceo_confidence']}%")
            print(f"Validation Roadmap Items: {len(result['validation_roadmap'])}")
            print(f"Data Verified Status: {result['data_verified']}")
            print(f"Number of specialist reports: {len(result['specialist_reports'])}")
            
            assert result['mode'] == "launch", "Test 1 Failed: mode must be 'launch'"
            assert result['final_recommendation'] in ["LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"], "Test 1 Failed: Invalid CEO decision"
            assert len(result['validation_roadmap']) >= 3, "Test 1 Failed: Validation roadmap must have at least 3 items"
            assert len(result['specialist_reports']) == 7, "Test 1 Failed: Must contain 6 specialists + 1 Founder CEO report"
            assert result['data_verified'] == True, "Test 1 Failed: Australia data should be verified"
            assert len(events) > 0, "Test 1 Failed: Progress callback was not triggered"

        # ----------------------------------------------------
        # TEST 2: Track B Unknown Country (Atlantis)
        # ----------------------------------------------------
        print("\n--- TEST 2: Unknown Country (Atlantis) ---")
        with patch.object(config.client.chat.completions, 'create', side_effect=llm_side_effect):
            result_un = run_track_b_session(
                business_idea="Subsea IoT Sensors",
                target_market="Atlantis",
                capital_budget=0.5,
                timeline="6 months",
                strategic_question="Should we deploy IoT sensors in Atlantis?"
            )
            print(f"Atlantis overall data_verified: {result_un['data_verified']}")
            assert result_un['data_verified'] == False, "Test 2 Failed: Atlantis data_verified must be False"
            mv_report = result_un['specialist_reports']['MARKET_VALIDATOR']
            assert mv_report['data_verified'] == False, "Test 2 Failed: Market Validator data_verified must be False for Atlantis"

        # ----------------------------------------------------
        # TEST 3: Capital Benchmark Missing
        # ----------------------------------------------------
        print("\n--- TEST 3: Capital Benchmark Missing ---")
        with patch.object(config.client.chat.completions, 'create', side_effect=llm_side_effect):
            result_bench = run_track_b_session(
                business_idea="FinTech Gateway",
                target_market="NonExistentMarket",
                capital_budget=0.8,
                timeline="12 months",
                strategic_question="Should we launch?"
            )
            cap_report = result_bench['specialist_reports']['CAPITAL_STRATEGIST']
            print(f"Capital Strategist on missing benchmark: data_verified={cap_report['data_verified']}")
            assert cap_report['data_verified'] == False, "Test 3 Failed: Capital benchmark must not be marked verified for missing market"

        # ----------------------------------------------------
        # TEST 4: Specialist Partial Failure Preservation
        # ----------------------------------------------------
        print("\n--- TEST 4: Specialist Failure Preservation ---")
        orig_fn = TRACK_B_AGENTS[1]["function"]
        try:
            TRACK_B_AGENTS[1]["function"] = MagicMock(side_effect=Exception("Database lock error"))
            with patch.object(config.client.chat.completions, 'create', side_effect=llm_side_effect):
                result_partial = run_track_b_session(
                    business_idea="AI Logistics Hub",
                    target_market="Australia",
                    capital_budget=2.0,
                    timeline="18 months",
                    strategic_question="Can we establish logistics in Australia?"
                )
                cs_failed_report = result_partial['specialist_reports']['COMPETITIVE_SCOUT']
                print(f"Failed specialist report: rec={cs_failed_report['recommendation']}, conf={cs_failed_report['confidence']}, analysis={cs_failed_report['analysis']}")
                assert cs_failed_report['confidence'] == 0, "Test 4 Failed: Failed specialist confidence must be 0"
                assert cs_failed_report['data_verified'] == False, "Test 4 Failed: Failed specialist data_verified must be False"
                assert len(result_partial['specialist_reports']) == 7, "Test 4 Failed: All reports must still be present"
                assert "EXECUTION ERROR" in cs_failed_report['analysis'], "Test 4 Failed: Explicit execution error must be documented"
        finally:
            TRACK_B_AGENTS[1]["function"] = orig_fn

        # ----------------------------------------------------
        # TEST 5: Founder CEO Failure Handling
        # ----------------------------------------------------
        print("\n--- TEST 5: Founder CEO Failure Handling ---")
        with patch('services.track_b_orchestrator.decide_founder_ceo', side_effect=Exception("LLM synthesis timeout")):
            with patch.object(config.client.chat.completions, 'create', side_effect=llm_side_effect):
                result_ceo_fail = run_track_b_session(
                    business_idea="Robotics Automation",
                    target_market="Australia",
                    capital_budget=1.0,
                    timeline="12 months",
                    strategic_question="Should we launch robotics in Australia?"
                )
                print(f"CEO Failure result: rec={result_ceo_fail['final_recommendation']}, conf={result_ceo_fail['ceo_confidence']}")
                assert result_ceo_fail['final_recommendation'] == "VALIDATE FIRST", "Test 5 Failed: CEO failure must default to VALIDATE FIRST"
                assert result_ceo_fail['ceo_confidence'] == 0, "Test 5 Failed: CEO confidence must be 0 on failure"
                assert len(result_ceo_fail['validation_roadmap']) >= 2, "Test 5 Failed: Fallback roadmap must be present"

        # ----------------------------------------------------
        # TEST 6: Track A Regression & Dispatcher Verification
        # ----------------------------------------------------
        print("\n--- TEST 6: Track A Regression & Dispatcher Test ---")
        assert callable(run_boardroom_session), "Test 6 Failed: Track A run_boardroom_session must be callable"
        assert len(CORE_AGENTS) == 6, "Test 6 Failed: Track A CORE_AGENTS must contain 6 agents"
        
        # Test unified dispatcher for Track A
        track_a_mock_json = json.dumps({
            "analysis": "Expansion into Australia shows high corporate strategic alignment.",
            "recommendation": "YES",
            "confidence": 88,
            "dialogue": "Corporate expansion is viable."
        })
        track_a_ceo_json = json.dumps({
            "analysis": "Unanimous board consensus to enter Australia.",
            "recommendation": "ENTER MARKET",
            "confidence": 92,
            "dialogue": "Proceed with international expansion."
        })
        def track_a_side_effect(*args, **kwargs):
            messages = kwargs.get("messages", [])
            content = messages[-1]["content"] if messages else ""
            if "CEO" in content or "CEO" in str(args):
                return create_mock_completion(track_a_ceo_json)
            return create_mock_completion(track_a_mock_json)
            
        with patch.object(config.client.chat.completions, 'create', side_effect=track_a_side_effect):
            disp_a = run_strategic_session(
                mode="expansion",
                company="EnterpriseCorp",
                market="Australia",
                budget=5.0,
                timeline="12 months",
                question="Should we expand into Australia?"
            )
            print(f"Dispatcher Track A result: decision={disp_a['ceo_decision']}, conf={disp_a['ceo_confidence']}")
            assert disp_a['ceo_decision'] == "ENTER MARKET", "Test 6 Failed: Track A expansion must return ENTER MARKET"
            assert len(disp_a['board_reports']) == 7, "Test 6 Failed: Track A must have 6 core agents + CEO"

    print("\n==================================================")
    print("ALL ORCHESTRATOR TESTS PASSED SUCCESSFULLY (TESTS 1 - 6)!")
    print("==================================================")

if __name__ == '__main__':
    run_tests()
