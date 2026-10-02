"""
BOARDROOM AI — STEP 8 DECISION INTELLIGENCE TEST SUITE
Deterministic verification of the 12 Step 8 requirements.
"""
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Force UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from services.track_b_orchestrator import (
    run_track_b_session,
    calculate_track_b_consensus,
    analyze_board_agreement,
    detect_board_disagreements,
    extract_critical_blockers,
    generate_decision_explanation,
    extract_mind_change_thresholds,
    compile_decision_trace,
    TRACK_B_AGENTS
)
from agents.founder_ceo_agent import decide_founder_ceo
from agents.market_validator_agent import validate_market
from agents.competitive_scout_agent import scout_competition
from agents.regulatory_navigator_agent import navigate_regulations
from agents.launch_operations_agent import evaluate_launch_operations
from agents.venture_risk_agent import assess_venture_risk
from agents.capital_strategist_agent import strategize_capital
from services.boardroom_orchestrator import run_boardroom_session, CORE_AGENTS
from services.consensus_engine import calculate_consensus

def create_mock_completion(content_str):
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = content_str
    return mock_resp

def get_standard_mock_json():
    return json.dumps({
        "analysis": "Empirical datasets and market indicators in Australia indicate strong venture viability.",
        "recommendation": "YES",
        "confidence": 85,
        "dialogue": "Market metrics support proceeding.",
        "key_finding": "High demand with fragmented competition.",
        "strongest_evidence": "Empirical datasets indicate positive margin trajectory.",
        "primary_concern": "Initial customer acquisition cost must be controlled.",
        "mind_change_threshold": "If regulatory clearance timeline exceeds 180 days."
    })

def get_ceo_mock_json(rec="LAUNCH", conf=88):
    return json.dumps({
        "analysis": "Consolidated findings show favorable unit economics and market demand. Recommend proceeding.",
        "recommendation": rec,
        "confidence": conf,
        "dialogue": "The board consensus is favorable. We are ready to launch.",
        "validation_roadmap": [
            "1. Conduct 30 customer discovery interviews (addressing Market Validator).",
            "2. Complete regulatory and licensing pre-filings (addressing Regulatory Navigator).",
            "3. Deploy lean MVP to validate acquisition unit economics (addressing Capital Strategist)."
        ]
    })

# Track results
test_results = []

def record_test(test_id, name, passed, error_msg=None):
    dots = "." * (45 - len(name))
    status_str = "PASS" if passed else "FAIL"
    print(f"{test_id} — {name} {dots} {status_str}")
    if not passed and error_msg:
        print(f"   ↳ Error: {error_msg}")
    test_results.append((test_id, name, passed, error_msg))

# -------------------------------------------------------------
# TEST 01: Track B Successful Live-Node Execution
# -------------------------------------------------------------
def test_01():
    try:
        def llm_side_effect(*args, **kwargs):
            messages = kwargs.get("messages", [])
            content = messages[-1]["content"] if messages else ""
            if "Founder CEO" in content or "FOUNDER_CEO" in str(messages):
                return create_mock_completion(get_ceo_mock_json("LAUNCH", 90))
            return create_mock_completion(get_standard_mock_json())

        with patch('time.sleep', return_value=None):
            with patch.object(config.client.chat.completions, 'create', side_effect=llm_side_effect):
                res = run_track_b_session(
                    business_idea="AI-driven Fleet Telematics",
                    target_market="Australia",
                    capital_budget=1000000,
                    timeline="12 months",
                    strategic_question="Should we launch an AI fleet telematics startup in Australia?"
                )
                assert res["mode"] == "launch"
                assert res["status"] == "success"
                assert res["data_verified"] is True
                assert len(res["specialist_reports"]) == 7
                record_test("TEST 01", "Track B successful execution", True)
    except Exception as e:
        record_test("TEST 01", "Track B successful execution", False, str(e))

# -------------------------------------------------------------
# TEST 02: Six Specialists Execute
# -------------------------------------------------------------
def test_02():
    try:
        mock_json = get_standard_mock_json()
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(mock_json)):
            mv = validate_market("SaaS Logistics", "Germany", 500000, "12 mo", "Launch in Germany?")
            cs = scout_competition("SaaS Logistics", "Germany", 500000, "12 mo", "Launch in Germany?")
            rn = navigate_regulations("SaaS Logistics", "Germany", 500000, "12 mo", "Launch in Germany?")
            lo = evaluate_launch_operations("SaaS Logistics", "Germany", 500000, "12 mo", "Launch in Germany?")
            vr = assess_venture_risk("SaaS Logistics", "Germany", 500000, "12 mo", "Launch in Germany?")
            cap = strategize_capital("SaaS Logistics", "Germany", 500000, "12 mo", "Launch in Germany?")
            
            for agent_rep, name in [(mv, "MV"), (cs, "CS"), (rn, "RN"), (lo, "LO"), (vr, "VR"), (cap, "CAP")]:
                assert "recommendation" in agent_rep, f"{name} missing recommendation"
                assert "confidence" in agent_rep, f"{name} missing confidence"
                assert "data_verified" in agent_rep, f"{name} missing data_verified"
                assert "analysis" in agent_rep, f"{name} missing analysis"
                assert "status" in agent_rep, f"{name} missing status"
            record_test("TEST 02", "Six specialists execute", True)
    except Exception as e:
        record_test("TEST 02", "Six specialists execute", False, str(e))

# -------------------------------------------------------------
# TEST 03: Founder CEO Synthesis
# -------------------------------------------------------------
def test_03():
    try:
        mock_specialists = {
            "MARKET_VALIDATOR": {"recommendation": "YES", "confidence": 85, "data_verified": True, "analysis": "High demand.", "status": "success"},
            "COMPETITIVE_SCOUT": {"recommendation": "YES", "confidence": 80, "data_verified": True, "analysis": "Fragmented incumbents.", "status": "success"},
            "REGULATORY_NAVIGATOR": {"recommendation": "MAYBE", "confidence": 70, "data_verified": True, "analysis": "Standard permits.", "status": "success"},
            "LAUNCH_OPERATIONS": {"recommendation": "YES", "confidence": 80, "data_verified": True, "analysis": "3 month MVP.", "status": "success"},
            "VENTURE_RISK": {"recommendation": "YES", "confidence": 85, "data_verified": True, "analysis": "Low country risk.", "status": "success"},
            "CAPITAL_STRATEGIST": {"recommendation": "YES", "confidence": 90, "data_verified": True, "analysis": "Budget aligned.", "status": "success"}
        }
        ceo_json = get_ceo_mock_json("LAUNCH", 88)
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(ceo_json)):
            ceo_res = decide_founder_ceo(
                business_idea="Fintech App",
                target_market="United Kingdom",
                capital_budget=750000,
                timeline="6 months",
                strategic_question="Launch Fintech in UK?",
                specialist_reports=mock_specialists
            )
            assert ceo_res["recommendation"] in ["LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"]
            assert ceo_res["confidence"] > 0
            assert len(ceo_res["validation_roadmap"]) >= 3
            record_test("TEST 03", "Founder CEO synthesis", True)
    except Exception as e:
        record_test("TEST 03", "Founder CEO synthesis", False, str(e))

# -------------------------------------------------------------
# TEST 04: Status Propagation
# -------------------------------------------------------------
def test_04():
    try:
        mock_reports = {
            "MARKET_VALIDATOR": {"recommendation": "YES", "confidence": 85, "data_verified": True, "status": "success"},
            "COMPETITIVE_SCOUT": {"recommendation": "NO", "confidence": 75, "data_verified": False, "status": "data_unavailable"},
            "REGULATORY_NAVIGATOR": {"recommendation": "MAYBE", "confidence": 0, "data_verified": False, "status": "error", "analysis": "[EXECUTION ERROR] Timeout"},
            "LAUNCH_OPERATIONS": {"recommendation": "YES", "confidence": 80, "data_verified": True, "status": "success"},
            "VENTURE_RISK": {"recommendation": "YES", "confidence": 85, "data_verified": True, "status": "success"},
            "CAPITAL_STRATEGIST": {"recommendation": "MAYBE", "confidence": 70, "data_verified": True, "status": "success"}
        }
        agreement = analyze_board_agreement(mock_reports)
        assert agreement["yes_count"] == 3
        assert agreement["no_count"] == 1
        assert agreement["maybe_count"] == 2
        assert agreement["verified_count"] == 4
        assert agreement["data_unavailable_count"] == 1
        assert agreement["error_count"] == 1
        assert agreement["is_reliable"] is False
        record_test("TEST 04", "Status propagation", True)
    except Exception as e:
        record_test("TEST 04", "Status propagation", False, str(e))

# -------------------------------------------------------------
# TEST 05: Data Unavailable Handling
# -------------------------------------------------------------
def test_05():
    try:
        mock_unverified = {
            "MARKET_VALIDATOR": {"recommendation": "YES", "confidence": 90, "data_verified": False, "status": "data_unavailable", "analysis": "Estimated TAM."},
            "COMPETITIVE_SCOUT": {"recommendation": "YES", "confidence": 90, "data_verified": False, "status": "data_unavailable", "analysis": "Estimated competitors."},
            "REGULATORY_NAVIGATOR": {"recommendation": "YES", "confidence": 90, "data_verified": False, "status": "data_unavailable", "analysis": "Estimated rules."},
            "LAUNCH_OPERATIONS": {"recommendation": "YES", "confidence": 90, "data_verified": False, "status": "data_unavailable", "analysis": "Estimated logistics."},
            "VENTURE_RISK": {"recommendation": "YES", "confidence": 90, "data_verified": False, "status": "data_unavailable", "analysis": "Estimated risk."},
            "CAPITAL_STRATEGIST": {"recommendation": "YES", "confidence": 90, "data_verified": False, "status": "data_unavailable", "analysis": "Estimated benchmark."}
        }
        ceo_json = get_ceo_mock_json("LAUNCH", 90) # LLM attempts LAUNCH despite no data
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(ceo_json)):
            ceo_res = decide_founder_ceo(
                business_idea="Quantum Cloud",
                target_market="Atlantis",
                capital_budget=500000,
                timeline="6 months",
                strategic_question="Launch in Atlantis?",
                specialist_reports=mock_unverified
            )
            # Conservative safeguard MUST downgrade recommendation to VALIDATE FIRST and cap confidence
            assert ceo_res["recommendation"] == "VALIDATE FIRST", f"Expected VALIDATE FIRST, got {ceo_res['recommendation']}"
            assert ceo_res["confidence"] <= 50
            assert ceo_res["data_verified"] is False
            record_test("TEST 05", "Data unavailable", True)
    except Exception as e:
        record_test("TEST 05", "Data unavailable", False, str(e))

# -------------------------------------------------------------
# TEST 06: Execution Error Handling
# -------------------------------------------------------------
def test_06():
    try:
        def error_side_effect(*args, **kwargs):
            raise RuntimeError("Groq node connectivity dropped")

        with patch('time.sleep', return_value=None):
            with patch.object(config.client.chat.completions, 'create', side_effect=error_side_effect):
                res = run_track_b_session(
                    business_idea="Autonomous Drone Delivery",
                    target_market="Germany",
                    capital_budget=1000000,
                    timeline="12 months",
                    strategic_question="Launch drones in Germany?"
                )
                assert res["status"] == "error"
                assert res["agreement_analysis"]["error_count"] > 0
                assert len(res["critical_blockers"]) > 0
                assert any("Execution Failure" in b["title"] for b in res["critical_blockers"])
                record_test("TEST 06", "Execution error", True)
    except Exception as e:
        record_test("TEST 06", "Execution error", False, str(e))

# -------------------------------------------------------------
# TEST 07: Malformed Response Handling
# -------------------------------------------------------------
def test_07():
    try:
        # LLM returns malformed JSON with missing recommendation and invalid types
        malformed_json = '{"random_key": 1234, "dialogue": "Unexpected format"}'
        with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(malformed_json)):
            mv = validate_market("SaaS Logistics", "Germany", 500000, "12 mo", "Launch in Germany?")
            assert mv["recommendation"] in ["YES", "NO", "MAYBE"]
            assert isinstance(mv["confidence"], int)
            assert "mind_change_threshold" in mv
            record_test("TEST 07", "Malformed response", True)
    except Exception as e:
        record_test("TEST 07", "Malformed response", False, str(e))

# -------------------------------------------------------------
# TEST 08: Disagreement Extraction
# -------------------------------------------------------------
def test_08():
    try:
        mock_conflicting = {
            "MARKET_VALIDATOR": {
                "name": "Market Validator",
                "recommendation": "YES",
                "confidence": 85,
                "key_finding": "High customer willingness to pay ($3.5B TAM).",
                "strongest_evidence": "Survey shows 78% eager to switch.",
                "data_verified": True
            },
            "COMPETITIVE_SCOUT": {
                "name": "Competitive Scout",
                "recommendation": "NO",
                "confidence": 80,
                "primary_concern": "Top 2 incumbents control 85% market share with long-term lock-in.",
                "data_verified": True
            },
            "REGULATORY_NAVIGATOR": {"name": "Regulatory Navigator", "recommendation": "MAYBE", "primary_concern": "Permits needed.", "data_verified": True},
            "LAUNCH_OPERATIONS": {"name": "Launch Operations", "recommendation": "YES", "key_finding": "Lean MVP ready.", "data_verified": True},
            "VENTURE_RISK": {"name": "Venture Risk", "recommendation": "MAYBE", "primary_concern": "Macro stability.", "data_verified": True},
            "CAPITAL_STRATEGIST": {"name": "Capital Strategist", "recommendation": "YES", "key_finding": "Budget aligned.", "data_verified": True}
        }
        disagreements = detect_board_disagreements(mock_conflicting)
        assert disagreements["has_disagreement"] is True
        assert len(disagreements["disagreements"]) > 0
        found_conflict = any(
            (d["agent_a"] == "Market Validator" and d["agent_b"] == "Competitive Scout")
            for d in disagreements["disagreements"]
        )
        assert found_conflict is True
        
        # Test broad alignment when all agree
        mock_aligned = {aid: {"recommendation": "YES", "key_finding": "All good.", "data_verified": True} for aid in mock_conflicting}
        aligned_res = detect_board_disagreements(mock_aligned)
        assert aligned_res["has_disagreement"] is False
        assert aligned_res["aligned_message"] == "✓ SPECIALISTS ARE BROADLY ALIGNED"
        record_test("TEST 08", "Disagreement extraction", True)
    except Exception as e:
        record_test("TEST 08", "Disagreement extraction", False, str(e))

# -------------------------------------------------------------
# TEST 09: Confidence Calculation
# -------------------------------------------------------------
def test_09():
    try:
        mock_specialists = {
            "MARKET_VALIDATOR": {"recommendation": "YES", "confidence": 80},
            "COMPETITIVE_SCOUT": {"recommendation": "NO", "confidence": 70},
            "REGULATORY_NAVIGATOR": {"recommendation": "MAYBE", "confidence": 60},
            "LAUNCH_OPERATIONS": {"recommendation": "YES", "confidence": 75},
            "VENTURE_RISK": {"recommendation": "YES", "confidence": 85},
            "CAPITAL_STRATEGIST": {"recommendation": "MAYBE", "confidence": 70}
        }
        metrics = calculate_track_b_consensus(mock_specialists)
        assert 0 <= metrics["opportunity_score"] <= 100
        assert 0 <= metrics["risk_mitigation_score"] <= 100
        assert 0 <= metrics["market_readiness"] <= 100
        assert 0 <= metrics["financial_feasibility"] <= 100
        record_test("TEST 09", "Confidence calculation", True)
    except Exception as e:
        record_test("TEST 09", "Confidence calculation", False, str(e))

# -------------------------------------------------------------
# TEST 10: Verdict Consistency
# -------------------------------------------------------------
def test_10():
    try:
        mock_specialists = {
            "MARKET_VALIDATOR": {"recommendation": "YES", "confidence": 85, "data_verified": True, "analysis": "OK", "status": "success"},
            "COMPETITIVE_SCOUT": {"recommendation": "YES", "confidence": 85, "data_verified": True, "analysis": "OK", "status": "success"},
            "REGULATORY_NAVIGATOR": {"recommendation": "YES", "confidence": 85, "data_verified": True, "analysis": "OK", "status": "success"},
            "LAUNCH_OPERATIONS": {"recommendation": "YES", "confidence": 85, "data_verified": True, "analysis": "OK", "status": "success"},
            "VENTURE_RISK": {"recommendation": "YES", "confidence": 85, "data_verified": True, "analysis": "OK", "status": "success"},
            "CAPITAL_STRATEGIST": {"recommendation": "YES", "confidence": 85, "data_verified": True, "analysis": "OK", "status": "success"}
        }
        for rec in ["LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"]:
            with patch.object(config.client.chat.completions, 'create', return_value=create_mock_completion(get_ceo_mock_json(rec, 85))):
                res = decide_founder_ceo("Test Idea", "Germany", 500000, "12 mo", "Launch?", mock_specialists)
                assert res["recommendation"] in ["LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"]
                assert 0 <= res["confidence"] <= 100
        record_test("TEST 10", "Verdict consistency", True)
    except Exception as e:
        record_test("TEST 10", "Verdict consistency", False, str(e))

# -------------------------------------------------------------
# TEST 11: Result/UI Contract
# -------------------------------------------------------------
def test_11():
    try:
        def llm_side_effect(*args, **kwargs):
            messages = kwargs.get("messages", [])
            content = messages[-1]["content"] if messages else ""
            if "Founder CEO" in content or "FOUNDER_CEO" in str(messages):
                return create_mock_completion(get_ceo_mock_json("VALIDATE FIRST", 75))
            return create_mock_completion(get_standard_mock_json())

        with patch('time.sleep', return_value=None):
            with patch.object(config.client.chat.completions, 'create', side_effect=llm_side_effect):
                res = run_track_b_session(
                    business_idea="Solar Energy Grid Analytics",
                    target_market="Germany",
                    capital_budget=500000,
                    timeline="12 months",
                    strategic_question="Should we launch?"
                )
                required_keys = [
                    "mode", "status", "business_idea", "target_market", "capital_budget",
                    "timeline", "strategic_question", "specialist_reports", "transcript",
                    "consensus_metrics", "founder_ceo_report", "final_recommendation",
                    "ceo_decision", "ceo_confidence", "ceo_rationale", "validation_roadmap",
                    "data_verified", "agreement_analysis", "disagreements", "critical_blockers",
                    "decision_explanation", "mind_change_thresholds", "decision_trace"
                ]
                for k in required_keys:
                    assert k in res, f"Missing required result key: {k}"
                record_test("TEST 11", "Result/UI contract", True)
    except Exception as e:
        record_test("TEST 11", "Result/UI contract", False, str(e))

# -------------------------------------------------------------
# TEST 12: Track A Regression Protection
# -------------------------------------------------------------
def test_12():
    try:
        track_a_mock_json = json.dumps({
            "analysis": "Expansion into Germany shows strong operational synergy.",
            "recommendation": "YES",
            "confidence": 85,
            "dialogue": "Expansion conditions are favorable."
        })
        track_a_ceo_json = json.dumps({
            "analysis": "Consolidated findings support strategic expansion.",
            "decision": "ENTER MARKET",
            "confidence": 88,
            "dialogue": "We approve expansion into Germany."
        })
        
        def track_a_llm_side_effect(*args, **kwargs):
            messages = kwargs.get("messages", [])
            content = messages[-1]["content"] if messages else ""
            if "Chief Executive Officer" in content or "CEO" in str(messages):
                return create_mock_completion(track_a_ceo_json)
            return create_mock_completion(track_a_mock_json)

        with patch('time.sleep', return_value=None):
            with patch.object(config.client.chat.completions, 'create', side_effect=track_a_llm_side_effect):
                res = run_boardroom_session(
                    company="TechCorp Global",
                    market="Germany",
                    budget=100,
                    timeline="1 Year",
                    question="Should TechCorp expand into Germany?"
                )
                assert "ceo_decision" in res
                assert res["ceo_decision"] in ["ENTER MARKET", "REJECT EXPANSION", "DELAY ENTRY", "GO", "NO-GO", "CONDITIONAL GO"]
                assert "consensus_metrics" in res
                assert len(res["board_reports"]) == 7
                
                # Check Track A consensus calculation
                metrics = calculate_consensus({
                    "MARKET_RESEARCH": {"recommendation": "YES", "confidence": 80},
                    "COMPETITOR": {"recommendation": "YES", "confidence": 75},
                    "LEGAL_REGULATORY": {"recommendation": "MAYBE", "confidence": 70},
                    "OPERATIONS": {"recommendation": "YES", "confidence": 85},
                    "RISK_ASSESSMENT": {"recommendation": "YES", "confidence": 80},
                    "CFO": {"recommendation": "YES", "confidence": 80}
                })
                assert "opportunity_score" in metrics
                assert "risk_mitigation_score" in metrics
                record_test("TEST 12", "Track A regression", True)
    except Exception as e:
        record_test("TEST 12", "Track A regression", False, str(e))

def main():
    print("==================================================")
    print("BOARDROOM AI — STEP 8 DECISION INTELLIGENCE TEST")
    print("==================================================\n")

    test_01()
    test_02()
    test_03()
    test_04()
    test_05()
    test_06()
    test_07()
    test_08()
    test_09()
    test_10()
    test_11()
    test_12()

    passed_count = sum(1 for _, _, p, _ in test_results if p)
    total_count = len(test_results)

    print("\n==================================================")
    if passed_count == total_count:
        print("STEP 8 RESULT: PASS")
        print(f"{passed_count}/{total_count} TESTS PASSED")
    else:
        print("STEP 8 RESULT: FAIL")
        print(f"{passed_count}/{total_count} TESTS PASSED")
        print("FAILED TESTS:")
        for t_id, name, p, err in test_results:
            if not p:
                print(f"- {t_id} ({name}): {err}")
    print("==================================================")

    if passed_count != total_count:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
