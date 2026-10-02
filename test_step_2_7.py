import json
import unittest
from unittest.mock import patch, MagicMock

import services.data_service as ds
import config

from agents.market_validator_agent import validate_market
from agents.competitive_scout_agent import scout_competition
from agents.regulatory_navigator_agent import navigate_regulations
from agents.launch_operations_agent import evaluate_launch_operations
from agents.venture_risk_agent import assess_venture_risk
from agents.capital_strategist_agent import strategize_capital
from agents.founder_ceo_agent import decide_founder_ceo

# Track A imports
from agents.researcher_agent import analyze_market
from agents.competitor_agent import analyze_competition
from agents.legal_agent import analyze_legal
from agents.operations_agent import analyze_operations
from agents.risk_agent import analyze_risk
from agents.cfo_agent import analyze_finance
from agents.ceo_agent import analyze_ceo
from services.boardroom_orchestrator import run_boardroom_session, CORE_AGENTS

def create_mock_completion(content_str):
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = content_str
    return mock_resp

def run_tests():
    print("==================================================")
    print("RUNNING STEP 2.7 TESTS (A - F)")
    print("==================================================")

    # ----------------------------------------------------
    # TEST A: Valid Country + Valid Business Idea (Australia)
    # ----------------------------------------------------
    print("\n--- TEST A: Valid Country & Business Idea (Australia) ---")
    valid_json = json.dumps({
        "analysis": "Real LLM evaluated successfully based on verified data.",
        "recommendation": "YES",
        "confidence": 85,
        "dialogue": "Let us launch.",
        "mind_change_threshold": "If CAC increases by 50%"
    })
    
    with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(valid_json)):
        # 1. Market Validator
        mv_res = validate_market("AI AgriTech", "Australia", 500000, "12 months", "Should we launch an agritech startup?")
        print(f"Market Validator: data_verified={mv_res['data_verified']}, rec={mv_res['recommendation']}, conf={mv_res['confidence']}")
        assert mv_res['data_verified'] == True, "Test A Failed: Market Validator data_verified should be True for Australia"
        
        # 2. Competitive Scout
        cs_res = scout_competition("AI AgriTech", "Australia", 500000, "12 months", "Should we launch an agritech startup?")
        print(f"Competitive Scout: data_verified={cs_res['data_verified']}, rec={cs_res['recommendation']}, conf={cs_res['confidence']}")
        assert cs_res['data_verified'] == True, "Test A Failed: Competitive Scout data_verified should be True for Australia"

        # 3. Regulatory Navigator
        reg_res = navigate_regulations("AI AgriTech", "Australia", 500000, "12 months", "Should we launch an agritech startup?")
        print(f"Regulatory Navigator: data_verified={reg_res['data_verified']}, rec={reg_res['recommendation']}, conf={reg_res['confidence']}")
        assert reg_res['data_verified'] == True, "Test A Failed: Regulatory Navigator data_verified should be True for Australia"

        # 4. Launch Operations
        ops_res = evaluate_launch_operations("AI AgriTech", "Australia", 500000, "12 months", "Should we launch an agritech startup?")
        print(f"Launch Operations: data_verified={ops_res['data_verified']}, rec={ops_res['recommendation']}, conf={ops_res['confidence']}")
        assert ops_res['data_verified'] == True, "Test A Failed: Launch Operations data_verified should be True for Australia"

        # 5. Venture Risk
        vr_res = assess_venture_risk("AI AgriTech", "Australia", 500000, "12 months", "Should we launch an agritech startup?")
        print(f"Venture Risk: data_verified={vr_res['data_verified']}, rec={vr_res['recommendation']}, conf={vr_res['confidence']}")
        assert vr_res['data_verified'] == True, "Test A Failed: Venture Risk data_verified should be True for Australia"

        # 6. Capital Strategist
        cap_res = strategize_capital("AI AgriTech", "Australia", 500000, "12 months", "Should we launch an agritech startup?")
        print(f"Capital Strategist: data_verified={cap_res['data_verified']}, rec={cap_res['recommendation']}, conf={cap_res['confidence']}")
        assert cap_res['data_verified'] == True, "Test A Failed: Capital Strategist data_verified should be True for Australia"

        # 7. Founder CEO
        ceo_json = json.dumps({
            "analysis": "Synthesis of all 6 specialist reports confirms viability for Australia.",
            "recommendation": "LAUNCH",
            "confidence": 88,
            "dialogue": "We have alignment to launch an MVP in Australia.",
            "validation_roadmap": [
                "1. Pilot with 5 local farms to address Launch Operations sensor deployment.",
                "2. Conduct 20 customer discovery interviews to address Market Validator CAC concerns.",
                "3. Secure legal advisory on data storage compliance to address Regulatory Navigator notes."
            ]
        })
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(ceo_json)):
            reports = {
                "MARKET_VALIDATOR": mv_res,
                "COMPETITIVE_SCOUT": cs_res,
                "REGULATORY_NAVIGATOR": reg_res,
                "LAUNCH_OPERATIONS": ops_res,
                "VENTURE_RISK": vr_res,
                "CAPITAL_STRATEGIST": cap_res
            }
            founder_res = decide_founder_ceo("AI AgriTech", "Australia", 500000, "12 months", "Should we launch an agritech startup?", reports)
            print(f"Founder CEO: rec={founder_res['recommendation']}, conf={founder_res['confidence']}, roadmap count={len(founder_res['validation_roadmap'])}")
            assert founder_res['recommendation'] == "LAUNCH"
            assert len(founder_res['validation_roadmap']) >= 3
            assert founder_res['data_verified'] == True

    # ----------------------------------------------------
    # TEST B: Unknown/Unavailable Country (Atlantis)
    # ----------------------------------------------------
    print("\n--- TEST B: Unknown Country (Atlantis) ---")
    with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(valid_json)):
        mv_un = validate_market("AI FinTech", "Atlantis", 250000, "6 months", "Underwater payments")
        print(f"Market Validator (Atlantis): data_verified={mv_un['data_verified']}")
        assert mv_un['data_verified'] == False, "Test B Failed: Market Validator data_verified should be False for Atlantis"
        
        cap_un = strategize_capital("AI FinTech", "Atlantis", 250000, "6 months", "Payment gateway")
        print(f"Capital Strategist (Atlantis): data_verified={cap_un['data_verified']}")
        assert cap_un['data_verified'] == False, "Test B Failed: Capital Strategist data_verified should be False for Atlantis"

        ops_un = evaluate_launch_operations("AI FinTech", "Atlantis", 250000, "6 months", "Payment gateway")
        print(f"Launch Operations (Atlantis): data_verified={ops_un['data_verified']}")
        assert ops_un['data_verified'] == False, "Test B Failed: Launch Operations data_verified should be False for Atlantis"

    # ----------------------------------------------------
    # TEST C: Missing Startup Funding Benchmark
    # ----------------------------------------------------
    print("\n--- TEST C: Missing Startup Funding Benchmark ---")
    with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(valid_json)):
        cap_missing = strategize_capital("AI FinTech", "NonExistentCountry", 300000, "12 months", "App")
        print(f"Capital Strategist (NonExistentCountry): data_verified={cap_missing['data_verified']}")
        assert cap_missing['data_verified'] == False, "Test C Failed: Capital benchmark should not be verified for missing country"

    # ----------------------------------------------------
    # TEST D: Malformed LLM Output Handling
    # ----------------------------------------------------
    print("\n--- TEST D: Malformed LLM Output Handling ---")
    malformed_raw = "This is not JSON at all! Just raw rambling text with no schema structure..."
    with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(malformed_raw)):
        # Specialist test
        parsed_specialist = config.call_groq_api(
            "system prompt", "user prompt", agent_role="MARKET_VALIDATOR",
            company="StartupX", market="Australia", budget=100000, timeline=6, question="test",
            grounding_data={"status": "success"}
        )
        print(f"Specialist on malformed output: rec={parsed_specialist.get('recommendation')}, conf={parsed_specialist.get('confidence')}, data_verified={parsed_specialist.get('data_verified')}")
        assert parsed_specialist['confidence'] == 0, "Test D Failed: confidence should be 0 on malformed LLM output"
        assert parsed_specialist['recommendation'] == "MAYBE", "Test D Failed: specialist recommendation should be MAYBE on malformed output"
        assert "parsing error" in parsed_specialist['analysis'].lower() or "malformed" in parsed_specialist['analysis'].lower(), "Test D Failed: analysis should explicitly mention parsing issue"

        # Founder CEO test
        parsed_ceo = config.call_groq_api(
            "system prompt", "user prompt", agent_role="FOUNDER_CEO",
            company="StartupX", market="Australia", budget=100000, timeline=6, question="test",
            grounding_data={"status": "success"}
        )
        print(f"Founder CEO on malformed output: rec={parsed_ceo.get('recommendation')}, conf={parsed_ceo.get('confidence')}, roadmap={parsed_ceo.get('validation_roadmap')}")
        assert parsed_ceo['confidence'] == 0, "Test D Failed: Founder CEO confidence should be 0 on malformed output"
        assert parsed_ceo['recommendation'] == "VALIDATE FIRST", "Test D Failed: Founder CEO recommendation should be VALIDATE FIRST on malformed output"
        assert len(parsed_ceo['validation_roadmap']) >= 2, "Test D Failed: Founder CEO should have default validation roadmap on malformed output"

    # ----------------------------------------------------
    # TEST E: All LLM Attempts Fail (Network / Quota)
    # ----------------------------------------------------
    print("\n--- TEST E: All LLM Attempts Fail ---")
    with patch.object(config.client.chat.completions, 'create', side_effect=Exception("API connection timeout")):
        fail_specialist = config.call_groq_api(
            "system prompt", "user prompt", agent_role="MARKET_VALIDATOR",
            company="StartupX", market="Australia", budget=100000, timeline=6, question="test",
            grounding_data={"status": "success"}
        )
        print(f"Specialist on all-model failure: rec={fail_specialist.get('recommendation')}, conf={fail_specialist.get('confidence')}, analysis={fail_specialist.get('analysis')[:80]}...")
        assert fail_specialist['confidence'] == 0, "Test E Failed: confidence should be 0 on all LLM attempts fail"
        assert fail_specialist['recommendation'] == "MAYBE", "Test E Failed: recommendation should be MAYBE on all LLM fail"
        assert "[api failure]" in fail_specialist['analysis'].lower(), "Test E Failed: analysis should state LLM API failure"

        fail_ceo = config.call_groq_api(
            "system prompt", "user prompt", agent_role="FOUNDER_CEO",
            company="StartupX", market="Australia", budget=100000, timeline=6, question="test",
            grounding_data={"status": "success"}
        )
        print(f"Founder CEO on all-model failure: rec={fail_ceo.get('recommendation')}, conf={fail_ceo.get('confidence')}")
        assert fail_ceo['confidence'] == 0, "Test E Failed: Founder CEO confidence should be 0"
        assert fail_ceo['recommendation'] == "VALIDATE FIRST", "Test E Failed: Founder CEO rec should be VALIDATE FIRST"
        assert "[api failure]" in fail_ceo['analysis'].lower(), "Test E Failed: Founder CEO analysis should state API failure"

    # ----------------------------------------------------
    # TEST F: Track A Integrity Test
    # ----------------------------------------------------
    print("\n--- TEST F: Track A Integrity & Import Test ---")
    assert callable(run_boardroom_session), "Test F Failed: run_boardroom_session should be callable"
    assert len(CORE_AGENTS) == 6, "Test F Failed: CORE_AGENTS should have 6 Track A agents"
    print(f"Track A Orchestrator & Agents Integrity verified: {len(CORE_AGENTS)} core agents loaded.")

    # Test Track A mock execution if mock mode enabled or mocked LLM
    with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion('{"analysis": "Track A expansion verified.", "recommendation": "YES", "confidence": 90, "dialogue": "Expansion viable.", "mind_change_threshold": "10% tariff"}')):
        t1 = analyze_market("TechCorp", "Australia", 5.0, "12 months", "Should we expand?")
        print(f"Track A Researcher: {t1['recommendation']}, conf={t1['confidence']}")
        assert t1['recommendation'] == "YES"
        assert t1['confidence'] == 90

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! (TESTS A - F)")
    print("==================================================")

if __name__ == '__main__':
    run_tests()
