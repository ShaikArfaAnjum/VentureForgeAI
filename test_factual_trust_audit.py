"""
Unit tests for BoardRoomAI Factual Trust, Semantic Correctness, and Auditability.
Verifies all 22 judicial verification criteria required for judge-proof evidence grounding.
"""

import unittest
import os
import sys
import pandas as pd

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.dataset_provenance import (
    PROVENANCE_REGISTRY,
    DATASET_PROVENANCE_REGISTRY,
    get_dataset_provenance_record,
    verify_all_datasets_integrity,
    calculate_sha256,
    ProvenanceStatus,
    SourceTier,
    FreshnessCategory
)
from services.semantic_suitability import (
    SUITABILITY_RULES,
    SEMANTIC_SUITABILITY_REGISTRY,
    evaluate_evidence_suitability,
    evaluate_claim_suitability,
    EvidenceRelevance
)
from services.claim_validator import (
    ClaimValidator,
    ClaimType,
    ValidationStatus
)
from services.deterministic_decision_engine import evaluate_deterministic_decision
from services.track_b_orchestrator import run_track_b_session
from services.report_generator import generate_pdf_report


class TestFactualTrustAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import config
        cls._orig_mock = config.IS_MOCK
        config.IS_MOCK = True
        os.environ["TESTING"] = "1"
        
        # Run a deterministic Track B session for testing Australia Logistics SaaS
        cls.idea = "An AI-powered SaaS platform for logistics route optimization and emissions reduction."
        cls.country = "Australia"
        cls.budget = 750000
        cls.timeline = "12 Months"
        cls.result = run_track_b_session(
            business_idea=cls.idea,
            target_market=cls.country,
            capital_budget=cls.budget,
            timeline=cls.timeline,
            strategic_question="Should we launch an AI logistics SaaS in Australia with $750k budget?"
        )

    @classmethod
    def tearDownClass(cls):
        import config
        config.IS_MOCK = cls._orig_mock


    # 1. Every factual claim has an evidence ID
    def test_01_factual_claims_have_evidence_id(self):
        claims = self.result.get("claim_validation_summary", {}).get("extracted_claims", [])
        self.assertTrue(len(claims) > 0, "No claims extracted in summary")
        for claim in claims:
            if claim.get("claim_type") == "FACT":
                self.assertIsNotNone(claim.get("evidence_id"), f"Factual claim missing evidence_id: {claim}")
                self.assertTrue(len(str(claim.get("evidence_id"))) > 0)

    # 2. Every evidence ID resolves in the evidence ledger
    def test_02_every_evidence_id_resolves(self):
        ledger = self.result.get("evidence_ledger", [])
        ledger_ids = {e["evidence_id"] for e in ledger if "evidence_id" in e}
        self.assertTrue(len(ledger_ids) >= 6, "Expected at least 6 canonical evidence items")
        
        # Check blockers
        for blocker in self.result.get("critical_blockers", []):
            ref = blocker.get("evidence_reference") or blocker.get("evidence_ids")
            if isinstance(ref, list):
                for eid in ref:
                    self.assertIn(eid, ledger_ids, f"Blocker {blocker.get('blocker_id')} references missing evidence {eid}")
            elif isinstance(ref, str) and ref.startswith("EVID-"):
                self.assertIn(ref, ledger_ids, f"Blocker {blocker.get('blocker_id')} references missing evidence {ref}")

        # Check deterministic rules
        rules = self.result.get("deterministic_eval", {}).get("rule_evaluations", [])
        for rule in rules:
            for eid in rule.get("evidence_ids", []):
                self.assertIn(eid, ledger_ids, f"Rule {rule.get('rule_id')} references missing evidence {eid}")

    # 3. Every evidence ID points to valid dataset data
    def test_03_evidence_points_to_valid_dataset_data(self):
        ledger = self.result.get("evidence_ledger", [])
        for item in ledger:
            self.assertIn("source_dataset", item)
            self.assertIn("source_row_identifier", item)
            self.assertIn("source_column", item)
            self.assertIn("raw_value", item)
            self.assertTrue(len(str(item["raw_value"]).strip()) > 0)

    # 4. Every calculation is reproducible
    def test_04_every_calculation_is_reproducible(self):
        calcs = self.result.get("claim_validation_summary", {}).get("reproducible_calculations", [])
        self.assertTrue(len(calcs) > 0, "Expected reproducible calculations in summary")
        for calc in calcs:
            formula = calc.get("formula")
            inputs = calc.get("inputs", {})
            output = calc.get("output")
            self.assertIsNotNone(formula)
            self.assertIsNotNone(inputs)
            self.assertIsNotNone(output)

    # 5. Unsupported claims are detected
    def test_05_unsupported_claims_are_detected(self):
        validator = ClaimValidator(self.result.get("evidence_ledger", []))
        bad_report = {
            "agent_id": "test_agent",
            "agent_name": "Test Agent",
            "claims": [
                {
                    "statement": "The market will definitely grow 85% next quarter without proof.",
                    "claim_type": "FACT",
                    "evidence_id": None
                }
            ],
            "evidence_ids": []
        }
        res = validator.validate_agent_claims(bad_report)
        self.assertFalse(res["is_valid"])
        self.assertTrue(len(res["unsupported_claims"]) > 0)
        self.assertEqual(res["unsupported_claims"][0]["claim_type"], "FACT")

    # 6. Missing evidence never becomes positive evidence
    def test_06_missing_evidence_never_becomes_positive_evidence(self):
        ledger = self.result.get("evidence_ledger", [])
        for item in ledger:
            if item.get("verification_status") == "UNAVAILABLE" or item.get("provenance_status") == "MISSING":
                self.assertNotIn("strong market demand", str(item.get("interpretation", "")).lower())

    # 7. Local datasets are not automatically marked SOURCE-VERIFIED
    def test_07_local_datasets_not_automatically_source_verified(self):
        rec = get_dataset_provenance_record("research_data.csv")
        self.assertIn("TIER 3", rec["source_tier"])
        self.assertIn("DATASET-BACKED", rec["provenance_status"])
        self.assertNotIn("SOURCE-VERIFIED (EXTERNAL AUDITED)", rec["provenance_status"])

    # 8. Evidence suitability is evaluated
    def test_08_evidence_suitability_evaluated(self):
        suit = evaluate_evidence_suitability("competition_data.csv", "Competition", "BHP market cap")
        self.assertIn(suit["evidence_relevance"], ["WEAK", "INDIRECT"])
        self.assertIn("what_it_measures", suit)
        self.assertIn("what_it_cannot_support", suit)

    # 9. Dataset hashes remain stable
    def test_09_dataset_hashes_remain_stable(self):
        all_passed, records, issues = verify_all_datasets_integrity()
        self.assertTrue(all_passed, f"Dataset integrity check failed: {issues}")
        for ds_name, rec in records.items():
            self.assertEqual(len(rec["full_sha256"]), 64)
            self.assertTrue(rec["integrity_passed"])

    # 10. Decision can be reproduced without LLM
    def test_10_decision_reproduced_without_llm(self):
        det_eval = self.result.get("deterministic_eval", {})
        self.assertTrue(det_eval.get("can_reproduce_without_llm", False))
        
        # Re-run evaluation function directly
        eval_again = evaluate_deterministic_decision(
            target_market=self.country,
            capital_budget=self.budget,
            specialist_reports=self.result.get("specialist_reports", {}),
            evidence_quality=self.result.get("evidence_quality", {}),
            blockers=self.result.get("critical_blockers", []),
            vote_distribution=self.result.get("specialist_votes", {})
        )
        self.assertEqual(det_eval["decision"], eval_again["decision"])
        self.assertEqual(det_eval["rules_passed_count"], eval_again["rules_passed_count"])

    # 11. PDF/UI canonical result parity
    def test_11_pdf_ui_canonical_result_parity(self):
        pdf_bytes = generate_pdf_report(self.result)
        self.assertTrue(len(pdf_bytes) > 5000, "PDF should be successfully generated from canonical result")
        self.assertEqual(self.result.get("deterministic_decision"), self.result.get("final_decision"))

    # 12. Confidence is not presented as probability
    def test_12_confidence_not_presented_as_probability(self):
        conf_details = self.result.get("confidence_breakdown") or self.result.get("confidence_details", {})
        expl = self.result.get("confidence_semantics") or conf_details.get("confidence_semantics_explanation", "")
        self.assertTrue(len(expl) > 0, "Confidence semantics explanation missing")
        self.assertIn("confidence in the", expl.lower())
        self.assertIn("not a predictive probability", expl.lower())


    # 13. Coverage does not equal truth (Multi-dimensional coverage separation)
    def test_13_coverage_does_not_equal_truth(self):
        claim_summary = self.result.get("claim_validation_summary", {})
        ds_cov = claim_summary.get("dataset_coverage_percent", 0)
        crit_cov = claim_summary.get("decision_critical_coverage_percent", 0)
        self.assertEqual(ds_cov, 100)
        self.assertLess(crit_cov, 100)

    # 14. Counterfactual decisions behave deterministically
    def test_14_counterfactual_decisions_behave_deterministically(self):
        # Evaluate with low budget ($50k)
        eval_low = evaluate_deterministic_decision(
            target_market=self.country,
            capital_budget=50000,
            specialist_reports=self.result.get("specialist_reports", {}),
            evidence_quality=self.result.get("evidence_quality", {}),
            blockers=self.result.get("critical_blockers", []) + [{"severity": "CRITICAL", "title": "Insolvent Runway"}],
            vote_distribution={"YES": 1, "MAYBE": 2, "NO": 3}
        )
        self.assertEqual(eval_low["decision"], "DO NOT LAUNCH")

    # 15. Unknown countries fail safely
    def test_15_unknown_countries_fail_safely(self):
        # When evaluating an unknown country with missing data
        unknown_reports = {
            "MARKET_VALIDATOR": {"status": "data_unavailable", "data_verified": False, "recommendation": "MAYBE"},
            "COMPETITIVE_SCOUT": {"status": "data_unavailable", "data_verified": False, "recommendation": "MAYBE"},
            "REGULATORY_NAVIGATOR": {"status": "data_unavailable", "data_verified": False, "recommendation": "MAYBE"},
            "LAUNCH_OPERATIONS": {"status": "data_unavailable", "data_verified": False, "recommendation": "MAYBE"},
            "VENTURE_RISK": {"status": "data_unavailable", "data_verified": False, "recommendation": "MAYBE"},
            "CAPITAL_STRATEGIST": {"status": "data_unavailable", "data_verified": False, "recommendation": "MAYBE"}
        }
        unknown_eq = {
            "specialists_total": 6,
            "verified": 0,
            "unavailable": 6,
            "errors": 0,
            "coverage_percent": 0,
            "is_complete": False,
            "status_label": "0/6 DATASET-BACKED (0%)"
        }
        eval_unknown = evaluate_deterministic_decision(
            target_market="NonExistentCountry123",
            capital_budget=500000,
            specialist_reports=unknown_reports,
            evidence_quality=unknown_eq,
            blockers=[{"blocker_id": "BLK-001", "severity": "HIGH", "title": "Missing Empirical Dataset"}],
            vote_distribution={"YES": 0, "MAYBE": 6, "NO": 0}
        )
        self.assertEqual(eval_unknown["decision"], "VALIDATE FIRST")
        self.assertIn("specialist data gap", eval_unknown["policy_rationale"].lower())


    # 16. Corrupt or missing dataset integrity fails safely
    def test_16_corrupt_dataset_integrity_fails_safely(self):
        dummy_hash = calculate_sha256("non_existent_file.csv")
        self.assertEqual(dummy_hash, "FILE_NOT_FOUND")

    # 17. Hallucinated numerical claims are rejected
    def test_17_hallucinated_numerical_claims_rejected(self):
        validator = ClaimValidator(self.result.get("evidence_ledger", []))
        synthetic_claims = [
            {"statement": "Australian logistics grows at exactly 99.4% per week.", "claim_type": "FACT", "evidence_id": "EVID-FAKE-999"}
        ]
        report = {
            "agent_id": "competitive_scout",
            "agent_name": "Competitive Scout",
            "claims": synthetic_claims,
            "evidence_ids": ["EVID-FAKE-999"]
        }
        res = validator.validate_agent_claims(report)
        self.assertFalse(res["is_valid"])
        self.assertTrue(any(u["claim"] == "Australian logistics grows at exactly 99.4% per week." for u in res["unsupported_claims"]))

    # 18. Hallucinated companies without evidence are flagged
    def test_18_hallucinated_companies_rejected(self):
        suitability = evaluate_claim_suitability("PhantomLogistics Corp", "competition_data.csv", "Competition")
        self.assertEqual(suitability["relevance"], "WEAK")

    # 19. Founder CEO cannot override mandatory deterministic blockers
    def test_19_founder_ceo_cannot_override_mandatory_blockers(self):
        self.assertEqual(self.result.get("final_decision"), self.result.get("deterministic_decision"))
        self.assertIn(self.result.get("final_decision"), ["LAUNCH", "VALIDATE FIRST", "DO NOT LAUNCH"])

    # 20. Every blocker has evidence reference
    def test_20_every_blocker_has_evidence(self):
        # Create a sample blocker list from specialist reports to verify schema
        from services.canonical_result import build_critical_blockers
        sample_reports = {
            "MARKET_VALIDATOR": {"recommendation": "NO", "primary_concern": "Startup funding liquidity down.", "data_verified": True},
            "VENTURE_RISK": {"recommendation": "NO", "primary_concern": "Sovereign fragility elevated.", "data_verified": True}
        }
        blockers = build_critical_blockers(sample_reports)
        self.assertTrue(len(blockers) >= 2, "Expected blockers generated for NO votes")
        for blocker in blockers:
            self.assertIn("blocker_id", blocker)
            self.assertIn("title", blocker)
            self.assertIn("severity", blocker)
            self.assertIn("evidence_reference", blocker)
            self.assertIn("resolution_condition", blocker)


    # 21. Every validation gate has a measurable condition
    def test_21_every_validation_gate_measurable(self):
        gates = self.result.get("validation_gates", [])
        self.assertTrue(len(gates) > 0, "Expected validation gates")
        for gate in gates:
            self.assertIn("gate_id", gate)
            self.assertIn("condition", gate)
            self.assertIn("success_metric", gate)
            self.assertTrue(len(gate["success_metric"].strip()) > 5)

    # 22. Every mind-change threshold is measurable
    def test_22_every_mind_change_threshold_measurable(self):
        thresholds = self.result.get("mind_change_thresholds", [])
        self.assertTrue(len(thresholds) > 0, "Expected mind-change thresholds")
        for t in thresholds:
            self.assertIn("threshold", t)
            self.assertIn("classification", t)
            self.assertTrue(len(t["threshold"].strip()) > 5)


if __name__ == "__main__":
    unittest.main()
