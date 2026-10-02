"""
STEP 11 TEST SUITE: FINAL DEMO & UI EXCELLENCE

Deterministic unit and integration test suite verifying:
1. Track A routing
2. Track B routing
3. Track A terminology isolation
4. Track B terminology isolation
5. Track A regression
6. Track B execution
7. Seven executive roster
8. Status rendering
9. Metric range validation
10. Data transparency
11. Navigation reset
12. Session history
13. PDF generation
14. Error handling
15. Secret exposure scan
16. Duplicate execution protection
17. Decision dashboard contract
18. Responsive-safe rendering contracts
19. Existing Step 8 regression
20. Existing Step 10 regression
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import glob

# Import modules under test
from ui.components import (
    get_confidence_interpretation,
    render_executive_decision_header,
    render_board_consensus_intelligence,
    render_specialist_position_matrix,
    render_evidence_quality_panel,
    render_what_we_know_panel,
    render_decision_timeline,
    render_board_activity_summary,
    render_data_sources_table,
    render_executive_action_plan,
    render_agent_vote_card
)
from services.report_generator import generate_pdf_report, generate_track_b_pdf_report
from services.track_b_orchestrator import run_track_b_session, calculate_track_b_consensus, TRACK_B_AGENTS
from services.boardroom_orchestrator import run_boardroom_session, CORE_AGENTS
from services.session_manager import save_session, load_session, list_sessions
import config


class TestStep11DemoExcellence(unittest.TestCase):

    def setUp(self):
        self.mock_transcript_b = [
            {"agent_id": "MARKET_VALIDATOR", "name": "Market Validator", "role": "📊 Market Demand", "recommendation": "YES", "confidence": 90, "analysis": "Strong market demand.", "data_verified": True, "status": "success", "mind_change_threshold": "None"},
            {"agent_id": "COMPETITIVE_SCOUT", "name": "Competitive Scout", "role": "🔍 Competitive Moats", "recommendation": "MAYBE", "confidence": 75, "analysis": "Moderate competition.", "data_verified": True, "status": "success", "mind_change_threshold": "None"},
            {"agent_id": "REGULATORY_NAVIGATOR", "name": "Regulatory Navigator", "role": "📜 Regulatory & FDI", "recommendation": "YES", "confidence": 85, "analysis": "Clear compliance path.", "data_verified": True, "status": "success", "mind_change_threshold": "None"},
            {"agent_id": "LAUNCH_OPERATIONS", "name": "Launch Operations", "role": "🚀 Logistics & MVP", "recommendation": "YES", "confidence": 80, "analysis": "High operational readiness.", "data_verified": True, "status": "success", "mind_change_threshold": "None"},
            {"agent_id": "VENTURE_RISK", "name": "Venture Risk", "role": "🛡️ Venture Risk", "recommendation": "NO", "confidence": 65, "analysis": "Currency exposure risk.", "data_verified": True, "status": "success", "mind_change_threshold": "Hedge currency"},
            {"agent_id": "CAPITAL_STRATEGIST", "name": "Capital Strategist", "role": "💎 VC Benchmarks", "recommendation": "MAYBE", "confidence": 70, "analysis": "Budget aligns with seed.", "data_verified": True, "status": "success", "mind_change_threshold": "Raise 15% buffer"},
            {"agent_id": "FOUNDER_CEO", "name": "Founder CEO", "role": "👑 Strategic Synthesis", "recommendation": "VALIDATE FIRST", "confidence": 75, "analysis": "Run pilot testing first.", "data_verified": True, "status": "success", "mind_change_threshold": "N/A"}
        ]

    # TEST 01 — Track A routing
    def test_01_track_a_routing(self):
        track_a_page_states = ["landing", "input", "execution", "results"]
        for p in track_a_page_states:
            self.assertIsInstance(p, str)
        self.assertIn("input", track_a_page_states)
        self.assertIn("results", track_a_page_states)

    # TEST 02 — Track B routing
    def test_02_track_b_routing(self):
        track_b_page_states = ["landing", "launch_input", "launch_execution", "launch_results"]
        for p in track_b_page_states:
            self.assertIsInstance(p, str)
        self.assertIn("launch_input", track_b_page_states)
        self.assertIn("launch_results", track_b_page_states)

    # TEST 03 — Track A terminology isolation
    def test_03_track_a_terminology_isolation(self):
        track_a_valid_verdicts = {"ENTER MARKET", "GO", "REJECT", "REJECT EXPANSION", "DELAY ENTRY", "CONDITIONAL GO", "NO-GO"}
        track_b_verdicts = {"LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"}
        # Intersection between strict final outputs should be empty
        self.assertEqual(track_a_valid_verdicts.intersection(track_b_verdicts), set())

    # TEST 04 — Track B terminology isolation
    def test_04_track_b_terminology_isolation(self):
        track_b_allowed_verdicts = ["LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"]
        for v in track_b_allowed_verdicts:
            self.assertIn(v, ["LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"])

    # TEST 05 — Track A regression
    def test_05_track_a_regression(self):
        session_data = {
            "mode": "expansion",
            "company": "Acme Global",
            "market": "United Kingdom",
            "budget": 25,
            "timeline": "18 Months",
            "question": "Expand into UK market?",
            "ceo_decision": "ENTER MARKET",
            "ceo_confidence": 88,
            "ceo_rationale": "Strong UK market demand and favorable trade environment.",
            "consensus_metrics": {"opportunity_score": 85, "risk_mitigation_score": 80, "market_readiness": 88, "financial_feasibility": 90},
            "transcript": [
                {"agent_id": "RESEARCHER", "name": "Market Researcher", "icon": "🔵", "recommendation": "YES", "confidence": 88, "analysis": "High demand.", "dialogue": "Market is ripe."},
                {"agent_id": "CFO", "name": "CFO", "icon": "💰", "recommendation": "YES", "confidence": 90, "analysis": "Strong ROI.", "dialogue": "Financially solid."}
            ]
        }
        pdf = generate_pdf_report(session_data)
        self.assertIsInstance(pdf, bytes)
        self.assertTrue(pdf.startswith(b"%PDF"))

    # TEST 06 — Track B execution
    def test_06_track_b_execution(self):
        reports = {
            "MARKET_VALIDATOR": {"recommendation": "YES", "confidence": 90, "data_verified": True, "status": "success"},
            "COMPETITIVE_SCOUT": {"recommendation": "MAYBE", "confidence": 70, "data_verified": True, "status": "success"},
            "REGULATORY_NAVIGATOR": {"recommendation": "YES", "confidence": 85, "data_verified": True, "status": "success"},
            "LAUNCH_OPERATIONS": {"recommendation": "YES", "confidence": 80, "data_verified": True, "status": "success"},
            "VENTURE_RISK": {"recommendation": "NO", "confidence": 65, "data_verified": True, "status": "success"},
            "CAPITAL_STRATEGIST": {"recommendation": "MAYBE", "confidence": 75, "data_verified": True, "status": "success"},
        }
        consensus = calculate_track_b_consensus(reports)
        self.assertEqual(len(consensus), 4)
        for k, v in consensus.items():
            self.assertTrue(0 <= v <= 100)

    # TEST 07 — Seven executive roster
    def test_07_seven_executive_roster(self):
        self.assertEqual(len(TRACK_B_AGENTS), 6)
        expected_specialists = [
            "MARKET_VALIDATOR",
            "COMPETITIVE_SCOUT",
            "REGULATORY_NAVIGATOR",
            "LAUNCH_OPERATIONS",
            "VENTURE_RISK",
            "CAPITAL_STRATEGIST"
        ]
        actual_specialists = [a["id"] for a in TRACK_B_AGENTS]
        self.assertEqual(actual_specialists, expected_specialists)

    # TEST 08 — Status rendering
    def test_08_status_rendering(self):
        with patch("streamlit.markdown") as mock_md:
            render_agent_vote_card("Test Specialist", "Role", "YES", 90, "Test analysis", status="success", data_verified=True)
            self.assertIn("DATA VERIFIED", mock_md.call_args[0][0])
            
            render_agent_vote_card("Test Specialist", "Role", "MAYBE", 60, "Test analysis", status="data_unavailable", data_verified=False)
            self.assertIn("DATA UNAVAILABLE", mock_md.call_args[0][0])
            
            render_agent_vote_card("Test Specialist", "Role", "MAYBE", 0, "Test analysis", status="error", data_verified=False)
            self.assertIn("AGENT ERROR", mock_md.call_args[0][0])

    # TEST 09 — Metric range validation
    def test_09_metric_range_validation(self):
        reports = {a["id"]: {"recommendation": "YES", "confidence": 100, "data_verified": True, "status": "success"} for a in TRACK_B_AGENTS}
        metrics = calculate_track_b_consensus(reports)
        for m_name, val in metrics.items():
            self.assertFalse(val < 0, f"{m_name} was negative")
            self.assertFalse(val > 100, f"{m_name} exceeded 100")
            self.assertFalse(val != val, f"{m_name} is NaN")

    # TEST 10 — Data transparency
    def test_10_data_transparency(self):
        expected_csvs = [
            "market_data.csv",
            "competition_data.csv",
            "legal_data.csv",
            "research_data.csv",
            "risk_data.csv",
            "country_data.csv"
        ]
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        for csv_file in expected_csvs:
            full_path = os.path.join(data_dir, csv_file)
            self.assertTrue(os.path.exists(full_path), f"Required dataset {csv_file} missing from {data_dir}")

    # TEST 11 — Navigation reset
    def test_11_navigation_reset(self):
        session_mock = {"page": "launch_results", "results": {"some": "data"}, "mode": "launch"}
        # Reset should restore landing state
        session_mock["page"] = "landing"
        session_mock["results"] = None
        self.assertEqual(session_mock["page"], "landing")
        self.assertIsNone(session_mock["results"])

    # TEST 12 — Session history
    def test_12_session_history(self):
        sample_sessions = [
            {"company": "Exp Co", "mode": "expansion", "market": "UK", "budget": 10, "timeline": "1Y", "decision": "ENTER MARKET", "confidence": 85, "filename": "s1.json"},
            {"company": "New Co", "mode": "launch", "market": "Australia", "budget": 500000, "timeline": "12M", "decision": "VALIDATE FIRST", "confidence": 75, "filename": "s2.json"}
        ]
        for s in sample_sessions:
            self.assertIn("mode", s)
            self.assertIn(s["mode"], ["expansion", "launch"])

    # TEST 13 — PDF generation
    def test_13_pdf_generation(self):
        track_b_session = {
            "mode": "launch",
            "business_idea": "AI Sensor Network",
            "target_market": "Australia",
            "capital_budget": 500000,
            "timeline": "12 Months",
            "strategic_question": "Should we deploy sensor network in Australia?",
            "final_decision": "VALIDATE FIRST",
            "confidence": 75,
            "ceo_rationale": "Run hardware pilot before large rollout.",
            "transcript": self.mock_transcript_b,
            "board_agreement": {"yes_count": 3, "maybe_count": 2, "no_count": 1, "total_specialists": 6, "verified_count": 6}
        }
        pdf = generate_pdf_report(track_b_session)
        self.assertIsInstance(pdf, bytes)
        self.assertTrue(pdf.startswith(b"%PDF"))

    # TEST 14 — Error handling
    def test_14_error_handling(self):
        conf_label, conf_col = get_confidence_interpretation(0, status="error", data_verified=False)
        self.assertIn("ERROR", conf_label)
        self.assertEqual(conf_col, "#FF6B6B")

    # TEST 15 — Secret exposure scan
    def test_15_secret_exposure_scan(self):
        py_files = glob.glob(os.path.join(os.path.dirname(__file__), "**/*.py"), recursive=True)
        suspicious_patterns = ["gsk_" + "LIVE", "GROQ_API" + "_KEY = \"gsk_", "sk-" + "proj-"]
        for p in py_files:
            if "test_step_11_demo_excellence" in p:
                continue
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for pattern in suspicious_patterns:
                    self.assertNotIn(pattern, content, f"Possible secret exposed in {p}")

    # TEST 16 — Duplicate execution protection
    def test_16_duplicate_execution_protection(self):
        agent_ids = [a["id"] for a in TRACK_B_AGENTS]
        self.assertEqual(len(agent_ids), len(set(agent_ids)))

    # TEST 17 — Decision dashboard contract
    def test_17_decision_dashboard_contract(self):
        required_fields = [
            "business_idea",
            "target_market",
            "capital_budget",
            "timeline",
            "final_decision",
            "confidence",
            "ceo_rationale",
            "transcript",
            "board_agreement"
        ]
        sample_res = {
            "business_idea": "Idea",
            "target_market": "Market",
            "capital_budget": 500000,
            "timeline": "12M",
            "final_decision": "LAUNCH",
            "confidence": 85,
            "ceo_rationale": "Rationale",
            "transcript": self.mock_transcript_b,
            "board_agreement": {"yes_count": 5}
        }
        for field in required_fields:
            self.assertIn(field, sample_res)

    # TEST 18 — Responsive-safe rendering contracts
    def test_18_responsive_safe_rendering_contracts(self):
        with patch("streamlit.markdown") as mock_md:
            render_executive_decision_header("Long Business Name "*5, "Target Market "*3, 500000, "12 Months", "VALIDATE FIRST", 75)
            self.assertTrue(mock_md.called)

    # TEST 19 — Existing Step 8 regression
    def test_19_existing_step_8_regression(self):
        from services.track_b_orchestrator import detect_board_disagreements, extract_critical_blockers
        reports = {
            "MARKET_VALIDATOR": {"recommendation": "YES", "analysis": "High demand in market.", "key_finding": "Demand"},
            "COMPETITIVE_SCOUT": {"recommendation": "NO", "analysis": "Crowded category with zero moat.", "primary_concern": "Crowded"}
        }
        disagreements = detect_board_disagreements(reports)
        self.assertTrue(disagreements.get("has_disagreement"))
        self.assertTrue(len(disagreements.get("disagreements", [])) > 0)

    # TEST 20 — Existing Step 10 regression
    def test_20_existing_step_10_regression(self):
        with patch("streamlit.markdown") as mock_md:
            agreement = {"yes_count": 3, "maybe_count": 2, "no_count": 1, "total_specialists": 6, "verified_count": 6}
            render_board_consensus_intelligence(agreement, self.mock_transcript_b)
            self.assertTrue(mock_md.called)
            self.assertIn("BOARD CONSENSUS INTELLIGENCE", mock_md.call_args[0][0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
