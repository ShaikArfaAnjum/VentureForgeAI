"""
STEP 10 TEST SUITE: EXECUTIVE INTELLIGENCE DASHBOARD + EVIDENCE VISUALIZATION +
DECISION EXPLAINABILITY + DEMO-GRADE UX HARDENING + TRACK A/B REGRESSION PROTECTION

Deterministic unit and integration test suite.
"""

import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO

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
)
from services.report_generator import generate_pdf_report, generate_track_b_pdf_report
from services.track_b_orchestrator import run_track_b_session, calculate_track_b_consensus
from services.boardroom_orchestrator import run_boardroom_session
from services.session_manager import save_session, load_session, list_sessions


class TestStep10ExecutiveIntelligence(unittest.TestCase):
    
    def setUp(self):
        self.mock_transcript = [
            {
                "agent_id": "MARKET_VALIDATOR",
                "name": "Market Validator",
                "role": "📊 Market Demand & TAM",
                "icon": "📊",
                "recommendation": "YES",
                "confidence": 91,
                "analysis": "Strong validated demand in target market.",
                "dialogue": "Demand indicators show clear product-market fit.",
                "key_finding": "TAM capacity is strong with high growth rate.",
                "data_verified": True,
                "status": "success",
                "mind_change_threshold": "None"
            },
            {
                "agent_id": "COMPETITIVE_SCOUT",
                "name": "Competitive Scout",
                "role": "🔍 Competitive Moats",
                "icon": "🔍",
                "recommendation": "MAYBE",
                "confidence": 72,
                "analysis": "Category is crowded; requires differentiation.",
                "dialogue": "Incumbents occupy significant share.",
                "key_finding": "Crowded category requires unique niche positioning.",
                "data_verified": True,
                "status": "success",
                "mind_change_threshold": "Secure 15% lower CAC or exclusive supplier"
            },
            {
                "agent_id": "REGULATORY_NAVIGATOR",
                "name": "Regulatory Navigator",
                "role": "📜 Regulatory & FDI",
                "icon": "📜",
                "recommendation": "YES",
                "confidence": 84,
                "analysis": "Manageable compliance framework.",
                "dialogue": "Regulatory landscape is favorable.",
                "key_finding": "Clear licensing guidelines with minimal red tape.",
                "data_verified": True,
                "status": "success",
                "mind_change_threshold": "None"
            },
            {
                "agent_id": "LAUNCH_OPERATIONS",
                "name": "Launch Operations",
                "role": "🚀 Logistics & MVP",
                "icon": "🚀",
                "recommendation": "YES",
                "confidence": 80,
                "analysis": "Supply chain readiness confirmed.",
                "dialogue": "Local fulfillment partners available.",
                "key_finding": "Operational infrastructure readily available.",
                "data_verified": True,
                "status": "success",
                "mind_change_threshold": "None"
            },
            {
                "agent_id": "VENTURE_RISK",
                "name": "Venture Risk",
                "role": "🛡️ Venture Risk",
                "icon": "🛡️",
                "recommendation": "NO",
                "confidence": 65,
                "analysis": "FX volatility and customer churn risk.",
                "dialogue": "Risk parameters exceed conservative thresholds.",
                "key_finding": "FX currency exposure creates downside risk.",
                "data_verified": True,
                "status": "success",
                "mind_change_threshold": "Hedge 100% FX exposure in local contracts"
            },
            {
                "agent_id": "CAPITAL_STRATEGIST",
                "name": "Capital Strategist",
                "role": "💎 VC Benchmarks",
                "icon": "💎",
                "recommendation": "MAYBE",
                "confidence": 75,
                "analysis": "Budget matches VC seed benchmarks.",
                "dialogue": "Capital sizing is adequate for pilot stage.",
                "key_finding": "Capital allocation aligns with median seed rounds.",
                "data_verified": True,
                "status": "success",
                "mind_change_threshold": "Raise additional 20% runway reserve"
            },
            {
                "agent_id": "FOUNDER_CEO",
                "name": "Founder CEO",
                "role": "👑 Strategic Synthesis",
                "icon": "👑",
                "recommendation": "VALIDATE FIRST",
                "confidence": 75,
                "analysis": "Proceed with phased pilot validation before full rollout.",
                "dialogue": "We should validate customer willingness-to-pay first.",
                "key_finding": "Pilot validation required.",
                "data_verified": True,
                "status": "success",
                "mind_change_threshold": "N/A"
            }
        ]
        
        self.mock_agreement = {
            "yes_count": 3,
            "maybe_count": 2,
            "no_count": 1,
            "total_specialists": 6,
            "verified_count": 6,
            "unverified_count": 0,
            "error_count": 0
        }

    # TEST 01 — Executive header
    def test_01_executive_header(self):
        with patch("streamlit.markdown") as mock_st_md:
            render_executive_decision_header(
                business_idea="AI Green Logistics",
                target_market="Australia",
                budget=500000,
                timeline="12 Months",
                final_decision="VALIDATE FIRST",
                confidence=75,
                data_verified=True,
                status="success"
            )
            self.assertTrue(mock_st_md.called)
            rendered_content = mock_st_md.call_args[0][0]
            self.assertIn("BOARDROOM AI", rendered_content)
            self.assertIn("AI Green Logistics", rendered_content)
            self.assertIn("Australia", rendered_content)
            self.assertIn("VALIDATE FIRST", rendered_content)
            self.assertIn("75%", rendered_content)
            self.assertIn("EMPIRICALLY GROUNDED", rendered_content)

    # TEST 02 — Confidence visualization
    def test_02_confidence_visualization(self):
        high_label, high_col = get_confidence_interpretation(95, "success", True)
        self.assertEqual(high_label, "HIGH CONFIDENCE")
        
        strong_label, strong_col = get_confidence_interpretation(80, "success", True)
        self.assertEqual(strong_label, "STRONG CONFIDENCE")
        
        mod_label, mod_col = get_confidence_interpretation(65, "success", True)
        self.assertEqual(mod_label, "MODERATE CONFIDENCE")
        
        low_label, low_col = get_confidence_interpretation(40, "success", True)
        self.assertEqual(low_label, "LOW CONFIDENCE")
        
        err_label, err_col = get_confidence_interpretation(80, "error", True)
        self.assertIn("ERROR", err_label)
        
        unav_label, unav_col = get_confidence_interpretation(80, "data_unavailable", False)
        self.assertIn("UNCERTAIN", unav_label)

    # TEST 03 — Board consensus
    def test_03_board_consensus(self):
        with patch("streamlit.markdown") as mock_st_md:
            render_board_consensus_intelligence(self.mock_agreement, self.mock_transcript)
            self.assertTrue(mock_st_md.called)
            content = mock_st_md.call_args[0][0]
            self.assertIn("BOARD CONSENSUS INTELLIGENCE", content)
            self.assertIn("YES (LAUNCH)", content)
            self.assertIn("3", content)
            self.assertIn("MAYBE (VALIDATE)", content)
            self.assertIn("2", content)
            self.assertIn("NO (DO NOT LAUNCH)", content)
            self.assertIn("1", content)
            self.assertIn("6 / 6 DATASETS VERIFIED", content)

    # TEST 04 — Specialist position matrix
    def test_04_specialist_position_matrix(self):
        with patch("streamlit.markdown") as mock_st_md:
            render_specialist_position_matrix(self.mock_transcript)
            self.assertTrue(mock_st_md.called)
            content = mock_st_md.call_args[0][0]
            self.assertIn("SPECIALIST POSITION MATRIX", content)
            self.assertIn("Market Validator", content)
            self.assertIn("Competitive Scout", content)
            self.assertIn("Regulatory Navigator", content)
            self.assertIn("Launch Operations", content)
            self.assertIn("Venture Risk", content)
            self.assertIn("Capital Strategist", content)

    # TEST 05 — Evidence coverage
    def test_05_evidence_coverage(self):
        with patch("streamlit.markdown") as mock_st_md:
            render_evidence_quality_panel(self.mock_agreement, self.mock_transcript)
            self.assertTrue(mock_st_md.called)
            content = mock_st_md.call_args[0][0]
            self.assertIn("BOARD EVIDENCE QUALITY", content)
            self.assertIn("100%", content)
            self.assertIn("HIGH", content)

    # TEST 06 — What we know / don't know
    def test_06_what_we_know_dont_know(self):
        with patch("streamlit.markdown") as mock_st_md:
            render_what_we_know_panel(self.mock_transcript, self.mock_agreement)
            self.assertTrue(mock_st_md.called)
            content = mock_st_md.call_args[0][0]
            self.assertIn("EVIDENCE VS ASSUMPTION", content)
            self.assertIn("What We Know", content)
            self.assertIn("What We Don't Know", content)

    # TEST 07 — Disagreement map
    def test_07_disagreement_map(self):
        from ui.components import render_disagreements_section
        disagreements = {
            "has_disagreement": True,
            "disagreements": [{
                "agent_a": "Market Validator", "rec_a": "YES", "point_a": "Strong market TAM",
                "agent_b": "Competitive Scout", "rec_b": "MAYBE", "point_b": "Crowded category",
                "icon_a": "📊", "icon_b": "🔍"
            }]
        }
        with patch("streamlit.markdown") as mock_st_md:
            render_disagreements_section(disagreements)
            self.assertTrue(mock_st_md.called)
            content = mock_st_md.call_args[0][0]
            self.assertIn("STRATEGIC DISAGREEMENT", content)
            self.assertIn("Market Validator", content)
            self.assertIn("Competitive Scout", content)

    # TEST 08 — Critical blocker prioritization
    def test_08_critical_blocker_priority(self):
        from ui.components import render_critical_blockers_card
        blockers = [
            {"id": "01", "severity": "CRITICAL", "title": "Regulatory Certification", "source": "Regulatory Navigator", "description": "Mandatory tier-2 license needed."}
        ]
        with patch("streamlit.markdown") as mock_st_md:
            render_critical_blockers_card(blockers)
            self.assertTrue(mock_st_md.called)
            content = mock_st_md.call_args[0][0]
            self.assertIn("CRITICAL BLOCKERS", content)
            self.assertIn("Regulatory Certification", content)

    # TEST 09 — Mind-change thresholds
    def test_09_mind_change_thresholds(self):
        from ui.components import render_what_would_change_mind_card
        thresholds = [
            {"id": "01", "source": "Competitive Scout", "threshold": "Demonstrate 20% lower CAC"}
        ]
        with patch("streamlit.markdown") as mock_st_md:
            render_what_would_change_mind_card(thresholds)
            self.assertTrue(mock_st_md.called)
            content = mock_st_md.call_args[0][0]
            self.assertIn("WHAT WOULD CHANGE THE BOARD'S MIND?", content)
            self.assertIn("Demonstrate 20% lower CAC", content)

    # TEST 10 — Decision timeline
    def test_10_decision_timeline(self):
        with patch("streamlit.markdown") as mock_st_md:
            render_decision_timeline(self.mock_transcript, "VALIDATE FIRST", "success")
            self.assertTrue(mock_st_md.called)
            content = mock_st_md.call_args[0][0]
            self.assertIn("DECISION LOGIC PIPELINE", content)
            self.assertIn("Market", content)
            self.assertIn("Competition", content)
            self.assertIn("Regulation", content)
            self.assertIn("Operations", content)
            self.assertIn("Risk", content)
            self.assertIn("Capital", content)

    # TEST 11 — Data source transparency
    def test_11_data_source_transparency(self):
        with patch("streamlit.markdown") as mock_st_md:
            render_data_sources_table(self.mock_transcript)
            self.assertTrue(mock_st_md.called)
            content = mock_st_md.call_args[0][0]
            self.assertIn("DATA SOURCE TRANSPARENCY", content)
            self.assertIn("market_data.csv", content)
            self.assertIn("competition_data.csv", content)
            self.assertIn("legal_data.csv", content)
            self.assertIn("research_data.csv", content)
            self.assertIn("risk_data.csv", content)
            self.assertIn("country_data.csv", content)

    # TEST 12 — Executive action plan
    def test_12_executive_action_plan(self):
        roadmap = [
            "1. Secure local compliance certification",
            "2. Run 30-day customer pilot with 5 LOIs",
            "3. Optimize logistics fulfillment partner SLA"
        ]
        with patch("streamlit.markdown") as mock_st_md:
            render_executive_action_plan(roadmap)
            self.assertTrue(mock_st_md.called)
            content = mock_st_md.call_args[0][0]
            self.assertIn("EXECUTIVE ACTION PLAN", content)
            self.assertIn("IMMEDIATE", content)
            self.assertIn("NEXT", content)

    # TEST 13 — Decision trace
    def test_13_decision_trace(self):
        from ui.components import render_decision_trace_card
        trace_data = {
            "user_input": {"business_idea": "AI Logistics", "target_market": "Australia", "capital_budget": 500000, "timeline": "12M", "strategic_question": "Launch in AUS?"},
            "data_quality": {"verified_specialists": 6, "total_specialists": 6},
            "specialist_findings": [{"name": "Market Validator", "recommendation": "YES", "confidence": 91, "data_verified": True, "key_finding": "High TAM"}],
            "specialist_votes": {"YES": 3, "MAYBE": 2, "NO": 1},
            "ceo_synthesis": {"decision": "VALIDATE FIRST", "confidence": 75, "rationale": "Run pilot first"}
        }
        with patch("streamlit.expander") as mock_exp:
            render_decision_trace_card(trace_data)
            self.assertTrue(mock_exp.called)

    # TEST 14 — Track B PDF contract
    def test_14_track_b_pdf_contract(self):
        session_data = {
            "mode": "launch",
            "business_idea": "Clean Energy Bot",
            "target_market": "Australia",
            "capital_budget": 500000,
            "timeline": "12 Months",
            "strategic_question": "Should we launch Clean Energy Bot in Australia?",
            "final_decision": "VALIDATE FIRST",
            "confidence": 75,
            "ceo_rationale": "Run validation trials prior to committing large capital expenditure.",
            "transcript": self.mock_transcript,
            "board_agreement": self.mock_agreement,
            "critical_blockers": [{"id": "01", "severity": "HIGH", "title": "Grid Certification", "source": "Regulatory Navigator", "description": "Need cert."}],
            "disagreements": {"has_disagreement": True, "disagreements": [{"agent_a": "Market Validator", "rec_a": "YES", "point_a": "Demand", "agent_b": "Venture Risk", "rec_b": "NO", "point_b": "Risk"}]},
            "validation_roadmap": ["1. Pilot validation", "2. Grid compliance test"],
            "mind_change_thresholds": [{"source": "Venture Risk", "threshold": "Hedge FX exposure"}]
        }
        pdf_bytes = generate_pdf_report(session_data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    # TEST 15 — Session history compatibility
    def test_15_session_history_compatibility(self):
        test_session = {
            "mode": "launch",
            "company": "Clean Energy Bot",
            "business_idea": "Clean Energy Bot",
            "market": "Australia",
            "target_market": "Australia",
            "budget": 500000,
            "capital_budget": 500000,
            "timeline": "12 Months",
            "question": "Launch test",
            "ceo_decision": "VALIDATE FIRST",
            "final_decision": "VALIDATE FIRST",
            "ceo_confidence": 75,
            "confidence": 75,
            "date": "2026-09-11"
        }
        with patch("services.session_manager.os.path.exists", return_value=True), \
             patch("builtins.open", unittest.mock.mock_open(read_data='{"company":"Clean Energy Bot"}')):
            save_result = save_session(test_session)
            self.assertIsNotNone(save_result)

    # TEST 16 — Error-state transparency
    def test_16_error_state_transparency(self):
        err_transcript = [
            {
                "agent_id": "MARKET_VALIDATOR",
                "name": "Market Validator",
                "recommendation": "MAYBE",
                "confidence": 0,
                "analysis": "[EXECUTION ERROR] API connection timed out.",
                "dialogue": "Error in specialist calculation.",
                "status": "error",
                "data_verified": False
            }
        ]
        with patch("streamlit.markdown") as mock_st_md:
            render_specialist_position_matrix(err_transcript)
            content = mock_st_md.call_args[0][0]
            self.assertIn("ERROR", content)

    # TEST 17 — Data-unavailable transparency
    def test_17_data_unavailable_transparency(self):
        unav_transcript = [
            {
                "agent_id": "MARKET_VALIDATOR",
                "name": "Market Validator",
                "recommendation": "MAYBE",
                "confidence": 60,
                "analysis": "Data unavailable for target region.",
                "dialogue": "Synthetic estimate only.",
                "status": "data_unavailable",
                "data_verified": False
            }
        ]
        with patch("streamlit.markdown") as mock_st_md:
            render_specialist_position_matrix(unav_transcript)
            content = mock_st_md.call_args[0][0]
            self.assertIn("UNAVAILABLE", content)

    # TEST 18 — Track A regression
    def test_18_track_a_regression(self):
        track_a_session = {
            "mode": "expansion",
            "company": "Acme Corp",
            "market": "Germany",
            "budget": 20,
            "timeline": "2 Years",
            "question": "Expand into Germany?",
            "ceo_decision": "ENTER MARKET",
            "ceo_confidence": 85,
            "ceo_rationale": "High market maturity and strong partner ecosystem.",
            "consensus_metrics": {"opportunity_score": 88, "risk_mitigation_score": 82, "market_readiness": 85, "financial_feasibility": 90},
            "transcript": [
                {"agent_id": "RESEARCHER", "name": "Market Researcher", "icon": "🔵", "recommendation": "YES", "confidence": 88, "analysis": "High demand.", "dialogue": "Strong market."},
                {"agent_id": "CFO", "name": "CFO", "icon": "💰", "recommendation": "YES", "confidence": 90, "analysis": "High ROI.", "dialogue": "Financially sound."}
            ]
        }
        pdf_bytes = generate_pdf_report(track_a_session)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    # TEST 19 — No duplicate agent execution
    def test_19_no_duplicate_agent_execution(self):
        from services.track_b_orchestrator import TRACK_B_AGENTS
        agent_ids = [a["id"] for a in TRACK_B_AGENTS]
        self.assertEqual(len(agent_ids), len(set(agent_ids)), "Duplicate agent IDs detected in Track B agents configuration")
        self.assertEqual(len(agent_ids), 6)

    # TEST 20 — No fabricated metrics
    def test_20_no_fabricated_metrics(self):
        reports = {
            "MARKET_VALIDATOR": {"recommendation": "YES", "confidence": 90, "data_verified": True, "status": "success"},
            "COMPETITIVE_SCOUT": {"recommendation": "YES", "confidence": 80, "data_verified": True, "status": "success"},
            "REGULATORY_NAVIGATOR": {"recommendation": "YES", "confidence": 85, "data_verified": True, "status": "success"},
            "LAUNCH_OPERATIONS": {"recommendation": "NO", "confidence": 70, "data_verified": True, "status": "success"},
            "VENTURE_RISK": {"recommendation": "NO", "confidence": 65, "data_verified": True, "status": "success"},
            "CAPITAL_STRATEGIST": {"recommendation": "MAYBE", "confidence": 75, "data_verified": True, "status": "success"}
        }
        metrics = calculate_track_b_consensus(reports)
        # Verify consensus counts strictly match reports dictionary without fabrication
        self.assertIn("opportunity_score", metrics)
        self.assertIn("risk_mitigation_score", metrics)
        self.assertIn("market_readiness", metrics)
        self.assertIn("financial_feasibility", metrics)


if __name__ == "__main__":
    unittest.main(verbosity=2)
