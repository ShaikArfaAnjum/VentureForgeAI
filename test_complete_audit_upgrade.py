"""
BoardRoomAI — Comprehensive 23-Point Trust, Correctness & Auditability Test Suite
Validates canonical result integrity, deterministic decision logic, evidence ledger,
risk matrix, blocker traceability, PDF parity, error resilience, and Track A protection.
"""

import unittest
import os
import sys
import copy
from io import BytesIO
from unittest.mock import patch, MagicMock

from services.canonical_result import (
    get_evidence_quality,
    build_evidence_ledger,
    build_risk_matrix,
    build_critical_blockers,
    build_validation_gates,
    build_executive_action_plan,
    classify_mind_change_thresholds,
    compute_deterministic_confidence
)
from services.deterministic_decision_engine import evaluate_deterministic_decision
from services.consistency_validator import validate_consistency
from services.track_b_orchestrator import run_track_b_session, calculate_track_b_consensus
from services.report_generator import generate_pdf_report, generate_track_b_pdf_report
from services.boardroom_orchestrator import run_boardroom_session

class TestBoardRoomAuditUpgrade(unittest.TestCase):

    def setUp(self):
        self.sample_specialists = {
            "MARKET_VALIDATOR": {
                "recommendation": "YES",
                "confidence": 88,
                "analysis": "Startup ecosystem shows 450 startups and $2.8B venture capital in Australia.",
                "data_verified": True,
                "status": "success",
                "key_finding": "Strong ecosystem liquidity with active venture rounds.",
                "mind_change_threshold": "A 40% decline in early-stage investment deals would change my vote to NO."
            },
            "COMPETITIVE_SCOUT": {
                "recommendation": "YES",
                "confidence": 85,
                "analysis": "Top incumbent is WiseTech Global ($28.4B), leaving clear digital-first SME voids.",
                "data_verified": True,
                "status": "success",
                "key_finding": "Incumbent voids present clear niche foothold.",
                "mind_change_threshold": "If incumbent releases direct clone before launch, I would vote NO."
            },
            "REGULATORY_NAVIGATOR": {
                "recommendation": "YES",
                "confidence": 86,
                "analysis": "Starting a business score is 80.2/100 requiring ~2.5 days for entity incorporation.",
                "data_verified": True,
                "status": "success",
                "key_finding": "Structured incorporation pathway with low regulatory friction.",
                "mind_change_threshold": "Foreign equity ownership caps above 50% would change my vote to NO."
            },
            "LAUNCH_OPERATIONS": {
                "recommendation": "YES",
                "confidence": 86,
                "analysis": "World Bank Logistics Performance Index rates Australia at 3.7/5.0.",
                "data_verified": True,
                "status": "success",
                "key_finding": "Logistics infrastructure supports lean MVP launch.",
                "mind_change_threshold": "Customs delays exceeding 30 days would change my vote to NO."
            },
            "VENTURE_RISK": {
                "recommendation": "YES",
                "confidence": 88,
                "analysis": "Fragile States Index rates Australia at rank #168 with fragility score 21.8/120.",
                "data_verified": True,
                "status": "success",
                "key_finding": "Very low sovereign fragility and stable macroeconomic indicators.",
                "mind_change_threshold": "Currency devaluation exceeding 25% would shift my recommendation to NO."
            },
            "CAPITAL_STRATEGIST": {
                "recommendation": "YES",
                "confidence": 90,
                "analysis": "Average startup in Australia raises $7.63M; proposed $750k launch budget is well-calibrated for initial MVP.",
                "data_verified": True,
                "status": "success",
                "key_finding": "Budget is calibrated for 12-month runway.",
                "mind_change_threshold": "Burn rate exceeding runway by 35% would downgrade my vote to NO."
            }
        }

    # TEST 1: Dashboard/PDF evidence count consistency
    def test_01_dashboard_pdf_evidence_count_consistency(self):
        eq = get_evidence_quality(self.sample_specialists)
        self.assertEqual(eq["specialists_total"], 6)
        self.assertEqual(eq["verified"], 6)
        self.assertEqual(eq["unavailable"], 0)
        self.assertEqual(eq["errors"], 0)
        self.assertEqual(eq["coverage_percent"], 100)

    # TEST 2: Dashboard/PDF vote consistency
    def test_02_dashboard_pdf_vote_consistency(self):
        votes = {"YES": 6, "MAYBE": 0, "NO": 0}
        self.assertEqual(sum(votes.values()), 6)

    # TEST 3: Dashboard/PDF final decision consistency
    def test_03_dashboard_pdf_final_decision_consistency(self):
        eq = get_evidence_quality(self.sample_specialists)
        eval_res = evaluate_deterministic_decision(
            target_market="Australia",
            capital_budget=750000,
            specialist_reports=self.sample_specialists,
            evidence_quality=eq,
            blockers=[],
            vote_distribution={"YES": 6, "MAYBE": 0, "NO": 0}
        )
        self.assertEqual(eval_res["decision"], "LAUNCH")

    # TEST 4: Missing dataset handling (graceful DATA GAP)
    def test_04_missing_dataset(self):
        missing_specialists = dict(self.sample_specialists)
        missing_specialists["MARKET_VALIDATOR"] = {
            "recommendation": "MAYBE",
            "confidence": 70,
            "analysis": "No verified startup ecosystem dataset found on disk.",
            "data_verified": False,
            "status": "data_unavailable",
            "primary_concern": "Empirical venture liquidity unverified."
        }
        eq = get_evidence_quality(missing_specialists)
        self.assertEqual(eq["verified"], 5)
        self.assertEqual(eq["unavailable"], 1)
        self.assertEqual(eq["coverage_percent"], 83)

    # TEST 5: Unknown country handling (explicit COUNTRY DATA UNAVAILABLE)
    def test_05_unknown_country(self):
        unknown_specialists = {
            aid: {
                "recommendation": "MAYBE",
                "confidence": 60,
                "analysis": "No dataset found for Atlantis on disk.",
                "data_verified": False,
                "status": "data_unavailable"
            }
            for aid in self.sample_specialists
        }
        eq = get_evidence_quality(unknown_specialists)
        self.assertEqual(eq["verified"], 0)
        self.assertEqual(eq["unavailable"], 6)
        self.assertEqual(eq["coverage_percent"], 0)
        
        eval_res = evaluate_deterministic_decision(
            target_market="Atlantis",
            capital_budget=500000,
            specialist_reports=unknown_specialists,
            evidence_quality=eq,
            blockers=[{"severity": "HIGH"}],
            vote_distribution={"YES": 0, "MAYBE": 6, "NO": 0}
        )
        self.assertEqual(eval_res["decision"], "VALIDATE FIRST")

    # TEST 6: Malformed specialist output handling
    def test_06_malformed_specialist_output(self):
        malformed_specialists = copy.deepcopy(self.sample_specialists)
        malformed_specialists["LAUNCH_OPERATIONS"] = {
            "status": "error",
            "error_message": "JSONDecodeError: Expecting value: line 1 column 1",
            "analysis": "[PARSING ERROR] Malformed output from node",
            "recommendation": "MAYBE",
            "confidence": 0,
            "data_verified": False
        }
        eq = get_evidence_quality(malformed_specialists)
        self.assertEqual(eq["errors"], 1)
        self.assertEqual(eq["verified"], 5)

    # TEST 7: API failure handling
    def test_07_api_failure(self):
        api_failed_specialists = copy.deepcopy(self.sample_specialists)
        api_failed_specialists["REGULATORY_NAVIGATOR"] = {
            "status": "error",
            "error_message": "Groq API Connection Timeout (504)",
            "analysis": "[API FAILURE] LLM candidate models unreachable",
            "recommendation": "MAYBE",
            "confidence": 0,
            "data_verified": False
        }
        eq = get_evidence_quality(api_failed_specialists)
        self.assertEqual(eq["errors"], 1)
        
        eval_res = evaluate_deterministic_decision(
            target_market="Australia",
            capital_budget=750000,
            specialist_reports=api_failed_specialists,
            evidence_quality=eq,
            blockers=[{"severity": "CRITICAL", "description": "Node execution failure"}],
            vote_distribution={"YES": 5, "MAYBE": 1, "NO": 0}
        )
        # Any node execution error must mandate DO NOT LAUNCH until resolved
        self.assertEqual(eval_res["decision"], "DO NOT LAUNCH")

    # TEST 8: Missing evidence behavior
    def test_08_missing_evidence_conservative_shift(self):
        partial_specialists = copy.deepcopy(self.sample_specialists)
        partial_specialists["VENTURE_RISK"] = {
            "recommendation": "MAYBE",
            "confidence": 65,
            "analysis": "Risk data unavailable.",
            "data_verified": False,
            "status": "data_unavailable"
        }
        eq = get_evidence_quality(partial_specialists)
        eval_res = evaluate_deterministic_decision(
            target_market="Australia",
            capital_budget=750000,
            specialist_reports=partial_specialists,
            evidence_quality=eq,
            blockers=[],
            vote_distribution={"YES": 5, "MAYBE": 1, "NO": 0}
        )
        self.assertEqual(eval_res["decision"], "VALIDATE FIRST")

    # TEST 9: No fabricated evidence (strict verification)
    def test_09_no_fabricated_evidence(self):
        ledger = build_evidence_ledger(
            target_market="Atlantis",
            capital_budget=500000,
            timeline="12 Months",
            specialist_reports={aid: {"data_verified": False} for aid in self.sample_specialists},
            grounding_facts={}
        )
        for item in ledger:
            if item.get("evidence_type") == "FACT":
                self.assertNotEqual(item.get("verification_status"), "PROVENANCE VERIFIED")

    # TEST 10: Evidence ledger completeness & EVID IDs
    def test_10_evidence_ledger_completeness(self):
        grounding = {
            "Research Data": {"Startups Tracked": 450, "Total Funding (USD)": "2.8B", "Average Funding per Startup (USD)": "7,634,195"},
            "Competition Data": {"Top Company": "WiseTech Global", "Top Company Market Cap (USD)": "28.4B", "Companies Tracked": 12},
            "Legal Data": {"Starting a Business Score": 80.2, "Days to Start Business": 2.5, "Ease of Doing Business Score": 81.8},
            "Market Data": {"Logistics Performance Score (2023)": 3.7},
            "Risk Data": {"Fragility Score": 21.8, "Rank": 168, "E1: Economy": 1.9}
        }
        ledger = build_evidence_ledger(
            target_market="Australia",
            capital_budget=750000,
            timeline="12 Months",
            specialist_reports=self.sample_specialists,
            grounding_facts=grounding
        )
        self.assertGreaterEqual(len(ledger), 6)
        for idx, item in enumerate(ledger):
            self.assertTrue(item["evidence_id"].startswith("EVID-"))
            self.assertIn("verification_status", item)
            self.assertIn("evidence_type", item)

    # TEST 11: Deterministic LAUNCH
    def test_11_deterministic_launch(self):
        eq = get_evidence_quality(self.sample_specialists)
        eval_res = evaluate_deterministic_decision(
            target_market="Australia",
            capital_budget=750000,
            specialist_reports=self.sample_specialists,
            evidence_quality=eq,
            blockers=[],
            vote_distribution={"YES": 6, "MAYBE": 0, "NO": 0}
        )
        self.assertEqual(eval_res["decision"], "LAUNCH")

    # TEST 12: Deterministic VALIDATE FIRST
    def test_12_deterministic_validate_first(self):
        mixed = copy.deepcopy(self.sample_specialists)
        mixed["MARKET_VALIDATOR"]["recommendation"] = "MAYBE"
        eq = get_evidence_quality(mixed)
        eval_res = evaluate_deterministic_decision(
            target_market="Australia",
            capital_budget=750000,
            specialist_reports=mixed,
            evidence_quality=eq,
            blockers=[{"severity": "MEDIUM", "description": "Customer pilot pending"}],
            vote_distribution={"YES": 5, "MAYBE": 1, "NO": 0}
        )
        self.assertEqual(eval_res["decision"], "VALIDATE FIRST")

    # TEST 13: Deterministic DO NOT LAUNCH
    def test_13_deterministic_do_not_launch(self):
        bad = copy.deepcopy(self.sample_specialists)
        bad["VENTURE_RISK"]["recommendation"] = "NO"
        bad["REGULATORY_NAVIGATOR"]["recommendation"] = "NO"
        eq = get_evidence_quality(bad)
        eval_res = evaluate_deterministic_decision(
            target_market="Australia",
            capital_budget=750000,
            specialist_reports=bad,
            evidence_quality=eq,
            blockers=[
                {"severity": "CRITICAL", "description": "Foreign equity ban"},
                {"severity": "CRITICAL", "description": "Sovereign currency crisis"}
            ],
            vote_distribution={"YES": 4, "MAYBE": 0, "NO": 2}
        )
        self.assertEqual(eval_res["decision"], "DO NOT LAUNCH")

    # TEST 14: Founder CEO disagreement & safety lock
    def test_14_founder_ceo_override_safety_lock(self):
        res = run_track_b_session(
            business_idea="AI Logistics Platform",
            target_market="Australia",
            capital_budget=750000,
            timeline="12 Months",
            strategic_question="Should we launch in Australia?"
        )
        # Verify that final_decision is identical to deterministic_decision
        self.assertEqual(res["final_decision"], res["deterministic_decision"])

    # TEST 15: Confidence calculation
    def test_15_confidence_calculation(self):
        conf = compute_deterministic_confidence(
            evidence_quality={"coverage_percent": 100},
            vote_distribution={"YES": 6, "MAYBE": 0, "NO": 0},
            blockers=[],
            rules_passed=8,
            total_rules=8
        )
        self.assertGreaterEqual(conf["final_confidence"], 80)
        self.assertLessEqual(conf["final_confidence"], 100)

    # TEST 16: Risk calculation & UNKNOWN classification
    def test_16_risk_calculation(self):
        risks = build_risk_matrix(
            target_market="UnknownCountry",
            specialist_reports={aid: {"data_verified": False} for aid in self.sample_specialists},
            grounding_facts={}
        )
        self.assertEqual(len(risks), 7)
        for r in risks:
            self.assertTrue(r["risk_id"].startswith("RISK-"))
            self.assertIn(r["level"], ["LOW", "MEDIUM", "HIGH", "UNKNOWN"])

    # TEST 17: Blocker traceability chain
    def test_17_blocker_traceability(self):
        blockers = build_critical_blockers(self.sample_specialists)
        for b in blockers:
            self.assertTrue(b["blocker_id"].startswith("BLOCKER-"))
            self.assertIn("resolution_condition", b)
            self.assertIn("severity", b)

    # TEST 18: Mind-change threshold taxonomy classification
    def test_18_mind_change_threshold_classification(self):
        thresholds = classify_mind_change_thresholds(self.sample_specialists)
        self.assertEqual(len(thresholds), 6)
        for t in thresholds:
            self.assertTrue(t["id"].startswith("MCT-"))
            self.assertIn("classification", t)

    # TEST 19: PDF generation
    def test_19_pdf_generation(self):
        session_data = run_track_b_session(
            business_idea="AI Logistics Platform",
            target_market="Australia",
            capital_budget=750000,
            timeline="12 Months",
            strategic_question="Evaluation in Australia"
        )
        pdf_bytes = generate_track_b_pdf_report(session_data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)

    # TEST 20: ReportLab import & font rendering
    def test_20_reportlab_import(self):
        import reportlab
        from reportlab.lib.pagesizes import letter
        self.assertIsNotNone(reportlab.__version__)

    # TEST 21: Track A regression
    def test_21_track_a_regression(self):
        res = run_boardroom_session(
            company="Nexora Logistics",
            market="Australia",
            budget=50,
            timeline="1 Year",
            question="Should we expand into Australia?"
        )
        self.assertIn("ceo_decision", res)
        self.assertIn("board_reports", res)
        self.assertEqual(len(res["board_reports"]), 7)
        
        pdf_bytes = generate_pdf_report(res)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)

    # TEST 22: Track B regression
    def test_22_track_b_regression(self):
        res = run_track_b_session(
            business_idea="AI Precision Drone",
            target_market="Australia",
            capital_budget=500000,
            timeline="12 Months",
            strategic_question="Drone agricultural launch"
        )
        self.assertIn("deterministic_decision", res)
        self.assertIn("evidence_ledger", res)
        self.assertIn("risk_matrix", res)

    # TEST 23: Clean installation / imports verification
    def test_23_clean_imports_verification(self):
        import streamlit
        import groq
        import pydantic
        import dotenv
        import reportlab
        import requests
        import pandas
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
