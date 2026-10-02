"""
BoardRoomAI — Deterministic Risk Mitigation & Trust Audit Regression Test Suite
Validates that Risk Mitigation is a real, dynamic, deterministic metric derived
from canonical risk state, blockers, validation gates, and empirical data grounding.
"""

import unittest
import os
import sys
import copy

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.canonical_result import (
    compute_deterministic_risk_mitigation,
    build_risk_matrix,
    build_critical_blockers,
    build_validation_gates,
    get_evidence_quality,
    build_evidence_ledger
)
from services.deterministic_decision_engine import evaluate_deterministic_decision
from services.track_b_orchestrator import run_track_b_session, calculate_track_b_consensus
from services.report_generator import generate_pdf_report
from services.consistency_validator import validate_consistency
from services.data_service import get_data


class TestRiskMitigationEngine(unittest.TestCase):
    
    def setUp(self):
        self.specialist_reports = {
            "MARKET_VALIDATOR": {
                "name": "Market Validator",
                "recommendation": "YES",
                "confidence": 88,
                "data_verified": True,
                "status": "success",
                "key_finding": "Strong market size.",
                "primary_concern": "Customer CAC may fluctuate."
            },
            "COMPETITIVE_SCOUT": {
                "name": "Competitive Scout",
                "recommendation": "YES",
                "confidence": 85,
                "data_verified": True,
                "status": "success",
                "key_finding": "Identified niche void.",
                "primary_concern": "Incumbent pricing power."
            },
            "REGULATORY_NAVIGATOR": {
                "name": "Regulatory Navigator",
                "recommendation": "YES",
                "confidence": 86,
                "data_verified": True,
                "status": "success",
                "key_finding": "Structured corporate framework.",
                "primary_concern": "Data residency compliance required."
            },
            "LAUNCH_OPERATIONS": {
                "name": "Launch Operations",
                "recommendation": "YES",
                "confidence": 86,
                "data_verified": True,
                "status": "success",
                "key_finding": "Logistics index supports rollout.",
                "primary_concern": "3PL integration friction."
            },
            "VENTURE_RISK": {
                "name": "Venture Risk",
                "recommendation": "YES",
                "confidence": 88,
                "data_verified": True,
                "status": "success",
                "key_finding": "Sovereign risk is low.",
                "primary_concern": "Currency volatility risk."
            },
            "CAPITAL_STRATEGIST": {
                "name": "Capital Strategist",
                "recommendation": "YES",
                "confidence": 90,
                "data_verified": True,
                "status": "success",
                "key_finding": "Budget aligned with local seed norms.",
                "primary_concern": "Runway governance needed."
            }
        }
        
        self.grounding_facts = {
            "Research Data": {"Startups Tracked": 1420, "Total Funding (USD)": "4.2 Billion", "Average Funding per Startup (USD)": "3.5 Million"},
            "Competition Data": {"Top Company": "Atlassian", "Top Company Market Cap (USD)": "$45B", "Companies Tracked": 68},
            "Legal Data": {"Starting a Business Score": 82.5, "Ease of Doing Business Score": 81.2},
            "Market Data": {"Logistics Performance Score (2023)": 3.8, "Logistics Performance Score": 3.8},
            "Risk Data": {"Fragility Score": 21.5, "Total": 21.5}
        }

    def _build_full_state(self, reports, market="Australia", budget=750000, timeline="12 Months"):
        eq = get_evidence_quality(reports)
        risk_mat = build_risk_matrix(market, reports, self.grounding_facts)
        blockers = build_critical_blockers(reports)
        gates = build_validation_gates(market, budget, blockers)
        votes = {
            "YES": sum(1 for r in reports.values() if str(r.get("recommendation", "")).upper() in ["YES", "LAUNCH"]),
            "MAYBE": sum(1 for r in reports.values() if str(r.get("recommendation", "")).upper() in ["MAYBE", "VALIDATE FIRST"]),
            "NO": sum(1 for r in reports.values() if str(r.get("recommendation", "")).upper() in ["NO", "DO NOT LAUNCH"])
        }
        det_eval = evaluate_deterministic_decision(market, budget, reports, eq, blockers, votes)
        rule_evals = det_eval["rule_evaluations"]
        
        risk_mit_res = compute_deterministic_risk_mitigation(
            risk_matrix=risk_mat,
            blockers=blockers,
            validation_gates=gates,
            rule_evaluations=rule_evals,
            evidence_quality=eq,
            specialist_reports=reports,
            capital_budget=budget,
            target_market=market
        )
        return {
            "evidence_quality": eq,
            "risk_matrix": risk_mat,
            "blockers": blockers,
            "validation_gates": gates,
            "rule_evaluations": rule_evals,
            "deterministic_eval": det_eval,
            "risk_mitigation": risk_mit_res
        }

    # =========================================================================
    # TEST 1: Risk Mitigation is not hardcoded to 100
    # =========================================================================
    def test_01_risk_mitigation_is_not_hardcoded_to_100(self):
        state = self._build_full_state(self.specialist_reports, "Australia", 750000)
        score = state["risk_mitigation"]["risk_mitigation_score"]
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 5)
        self.assertLessEqual(score, 98)
        # Even with strong positive signals, validation gates and standard residual risks ensure it's not a naive 100
        self.assertNotEqual(score, 100, "Risk Mitigation must never default or hardcode to 100%")

    # =========================================================================
    # TEST 2: Risk Mitigation changes when critical blockers are introduced
    # =========================================================================
    def test_02_risk_mitigation_drops_on_critical_blocker(self):
        base_state = self._build_full_state(self.specialist_reports, "Australia", 750000)
        base_score = base_state["risk_mitigation"]["risk_mitigation_score"]
        
        # Introduce a critical blocker by simulating a specialist execution failure or explicit NO vote
        blocked_reports = copy.deepcopy(self.specialist_reports)
        blocked_reports["VENTURE_RISK"]["recommendation"] = "NO"
        blocked_reports["VENTURE_RISK"]["primary_concern"] = "Severe foreign exchange controls and sovereign debt crisis."
        
        blocked_state = self._build_full_state(blocked_reports, "Australia", 750000)
        blocked_score = blocked_state["risk_mitigation"]["risk_mitigation_score"]
        
        self.assertLess(blocked_score, base_score, "Critical blocker must materially decrease Risk Mitigation score")
        self.assertGreaterEqual(base_score - blocked_score, 15, "Score drop for critical blocker should be significant (>= 15 pts)")

    # =========================================================================
    # TEST 3: Risk Mitigation changes when high-severity risks increase
    # =========================================================================
    def test_03_risk_mitigation_changes_on_high_severity_risks(self):
        base_state = self._build_full_state(self.specialist_reports, "Australia", 750000)
        base_score = base_state["risk_mitigation"]["risk_mitigation_score"]
        
        # Modify risk matrix to introduce high-severity operational & competitive risks
        high_risk_reports = copy.deepcopy(self.specialist_reports)
        high_risk_reports["COMPETITIVE_SCOUT"]["recommendation"] = "NO"
        high_risk_reports["COMPETITIVE_SCOUT"]["primary_concern"] = "Monopolistic incumbent lock-in."
        high_risk_reports["LAUNCH_OPERATIONS"]["recommendation"] = "NO"
        high_risk_reports["LAUNCH_OPERATIONS"]["primary_concern"] = "Zero port logistics connectivity."
        
        high_risk_state = self._build_full_state(high_risk_reports, "Australia", 750000)
        high_risk_score = high_risk_state["risk_mitigation"]["risk_mitigation_score"]
        
        self.assertLess(high_risk_score, base_score)
        self.assertLessEqual(high_risk_score, 55, "Compound high risks should lower mitigation to <= 55%")

    # =========================================================================
    # TEST 4: Missing risk evidence does not become 100%
    # =========================================================================
    def test_04_missing_risk_evidence_never_becomes_100_percent(self):
        unverified_reports = copy.deepcopy(self.specialist_reports)
        for rep in unverified_reports.values():
            rep["data_verified"] = False
            rep["status"] = "data_unavailable"
            
        unverified_state = self._build_full_state(unverified_reports, "Unknown_Country", 500000)
        score = unverified_state["risk_mitigation"]["risk_mitigation_score"]
        
        self.assertNotEqual(score, 100)
        self.assertLessEqual(score, 45, "Absence of empirical evidence must conservatively downgrade Risk Mitigation")
        self.assertEqual(unverified_state["risk_mitigation"]["rating_label"], "ELEVATED RESIDUAL RISK" if score >= 30 else "CRITICAL RISK DEFICIT")

    # =========================================================================
    # TEST 5: Risk Mitigation is deterministic
    # =========================================================================
    def test_05_risk_mitigation_is_strictly_deterministic(self):
        state1 = self._build_full_state(self.specialist_reports, "Australia", 750000)
        state2 = self._build_full_state(self.specialist_reports, "Australia", 750000)
        
        self.assertEqual(state1["risk_mitigation"]["risk_mitigation_score"], state2["risk_mitigation"]["risk_mitigation_score"])
        self.assertEqual(state1["risk_mitigation"]["total_penalty"], state2["risk_mitigation"]["total_penalty"])
        self.assertEqual(state1["risk_mitigation"]["audit_steps"], state2["risk_mitigation"]["audit_steps"])

    # =========================================================================
    # TEST 6: LLM output cannot arbitrarily override Risk Mitigation
    # =========================================================================
    def test_06_llm_cannot_override_risk_mitigation(self):
        # Even if a specialist report contains qualitative text asserting "100% mitigated"
        tampered_reports = copy.deepcopy(self.specialist_reports)
        tampered_reports["VENTURE_RISK"]["analysis"] = "Risk Mitigation: 100% guaranteed success zero risk."
        tampered_reports["VENTURE_RISK"]["recommendation"] = "NO"  # Contradictory vote
        
        state = self._build_full_state(tampered_reports, "Australia", 750000)
        score = state["risk_mitigation"]["risk_mitigation_score"]
        
        self.assertNotEqual(score, 100)
        self.assertTrue(state["risk_mitigation"]["cannot_be_overridden_by_llm"])

    # =========================================================================
    # TEST 7: Dashboard and canonical result have identical Risk Mitigation
    # =========================================================================
    def test_07_dashboard_and_canonical_result_parity(self):
        result = run_track_b_session(
            business_idea="AI Logistics Optimization Platform",
            target_market="Australia",
            capital_budget=750000,
            timeline="12 Months",
            strategic_question="Should we launch?"
        )
        
        canonical_rms = result.get("risk_mitigation_score")
        consensus_rms = result.get("consensus_metrics", {}).get("risk_mitigation_score")
        breakdown_rms = result.get("risk_mitigation_breakdown", {}).get("risk_mitigation_score")
        
        self.assertIsNotNone(canonical_rms)
        self.assertEqual(canonical_rms, consensus_rms, "Dashboard consensus metric must match canonical risk mitigation")
        self.assertEqual(canonical_rms, breakdown_rms, "Breakdown score must match root metric")

    # =========================================================================
    # TEST 8: PDF and canonical result have identical Risk Mitigation
    # =========================================================================
    def test_08_pdf_and_canonical_result_parity(self):
        result = run_track_b_session(
            business_idea="AI Logistics SaaS",
            target_market="Australia",
            capital_budget=750000,
            timeline="12 Months",
            strategic_question="Validate launch feasibility"
        )
        
        pdf_bytes = generate_pdf_report(result)
        self.assertGreater(len(pdf_bytes), 10000)
        
        is_valid, errors = validate_consistency(result)
        self.assertTrue(is_valid, f"Consistency validation failed: {errors}")

    # =========================================================================
    # TEST 9: Risk Mitigation remains bounded between 0 and 100
    # =========================================================================
    def test_09_risk_mitigation_remains_in_bounds(self):
        # Extreme worst-case state with all errors, NO votes, and missing data
        worst_reports = copy.deepcopy(self.specialist_reports)
        for r in worst_reports.values():
            r["recommendation"] = "NO"
            r["status"] = "error"
            r["data_verified"] = False
            
        state = self._build_full_state(worst_reports, "Unknown", 1000)
        score = state["risk_mitigation"]["risk_mitigation_score"]
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    # =========================================================================
    # TEST 10: No double-counting of the same risk
    # =========================================================================
    def test_10_no_double_counting_of_risks(self):
        state = self._build_full_state(self.specialist_reports, "Australia", 750000)
        penalties = state["risk_mitigation"]["penalties"]
        
        # Verify source IDs are distinct per category/domain
        source_ids = [p["source_id"] for p in penalties]
        self.assertEqual(len(source_ids), len(set(source_ids)), "Penalties should not contain duplicate source IDs")

    # =========================================================================
    # TEST 11: Capital-constrained input sensitivity ($50k vs $750k)
    # =========================================================================
    def test_11_capital_constraint_reduces_risk_mitigation(self):
        normal_state = self._build_full_state(self.specialist_reports, "Australia", 750000, "12 Months")
        normal_score = normal_state["risk_mitigation"]["risk_mitigation_score"]
        
        # Capital constrained scenario: $50k for 6 months (severe deficit against $3.5M benchmark)
        constrained_reports = copy.deepcopy(self.specialist_reports)
        constrained_reports["CAPITAL_STRATEGIST"]["recommendation"] = "NO"
        constrained_reports["CAPITAL_STRATEGIST"]["primary_concern"] = "Severe capital deficit: $50k represents <2% of ecosystem average round."
        
        constrained_state = self._build_full_state(constrained_reports, "Australia", 50000, "6 Months")
        constrained_score = constrained_state["risk_mitigation"]["risk_mitigation_score"]
        
        self.assertLess(constrained_score, normal_score, "Capital-constrained plan must have lower Risk Mitigation score than well-funded plan")
        self.assertIn("Capital Risk", constrained_state["risk_mitigation"]["category_breakdown"])
        self.assertIn(constrained_state["risk_mitigation"]["category_breakdown"]["Capital Risk"]["level"], ["HIGH", "MEDIUM"])

    # =========================================================================
    # TEST 12: Unknown Country scenario drops Risk Mitigation safely
    # =========================================================================
    def test_12_unknown_country_drops_risk_mitigation_safely(self):
        result_wakanda = run_track_b_session(
            business_idea="AI Supply Chain Platform",
            target_market="Wakanda",
            capital_budget=500000,
            timeline="12 Months",
            strategic_question="Should we expand into Wakanda?"
        )
        
        rms = result_wakanda.get("risk_mitigation_score")
        self.assertIsNotNone(rms)
        self.assertNotEqual(rms, 100, "Unknown country must never produce 100% Risk Mitigation")
        self.assertLessEqual(rms, 55, "Unknown country must have conservative low Risk Mitigation score")


if __name__ == "__main__":
    unittest.main()
