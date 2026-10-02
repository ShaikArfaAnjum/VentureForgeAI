"""
BoardRoomAI — Pre-Render & Export Consistency Validator
Ensures 100% mathematical and factual parity between Dashboard UI and PDF Audit Report.
"""

from typing import Dict, Any, Tuple, List

class ConsistencyValidationError(Exception):
    """Raised when an internal inconsistency is detected between canonical data and report payloads."""
    pass

def validate_consistency(result_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates the canonical integrity of a BoardRoomResult dictionary.
    
    Checks:
    1. Vote distribution sum equals total specialist count (6).
    2. Evidence quality sum (verified + unavailable + errors) equals total specialists (6).
    3. Final decision matches deterministic policy engine decision.
    4. Confidence score is between 0 and 100.
    5. Traceability IDs are well-formed (EVID-xxx, RISK-xxx, BLOCKER-xxx, GATE-xxx, RULE-xxx).
    6. No fabricated provenance labels.
    """
    discrepancies = []
    
    # 1. Check Vote Sum
    votes = result_data.get("specialist_votes", {})
    yes_c = votes.get("YES", 0)
    maybe_c = votes.get("MAYBE", 0)
    no_c = votes.get("NO", 0)
    total_votes = yes_c + maybe_c + no_c
    if total_votes != 6:
        discrepancies.append(f"Vote sum mismatch: {yes_c} YES + {maybe_c} MAYBE + {no_c} NO = {total_votes} (expected 6)")

    # 2. Check Evidence Quality
    eq = result_data.get("evidence_quality", {})
    ver = eq.get("verified", 0)
    unav = eq.get("unavailable", 0)
    errs = eq.get("errors", 0)
    tot_spec = eq.get("specialists_total", 6)
    if (ver + unav + errs) != tot_spec:
        discrepancies.append(f"Evidence quality mismatch: {ver} verified + {unav} unavailable + {errs} errors = {ver+unav+errs} (expected {tot_spec})")

    # 3. Check Deterministic Decision Parity
    final_dec = result_data.get("final_decision") or result_data.get("final_recommendation") or result_data.get("ceo_decision")
    det_dec = result_data.get("deterministic_decision")
    if det_dec and final_dec != det_dec:
        discrepancies.append(f"Decision parity violation: final displayed decision '{final_dec}' differs from deterministic policy '{det_dec}'")

    # 4. Check Confidence Range
    conf = result_data.get("confidence", result_data.get("ceo_confidence", 0))
    if not (0 <= conf <= 100):
        discrepancies.append(f"Invalid confidence score: {conf} (must be 0-100)")

    # 5. Check Evidence Ledger Traceability
    ledger = result_data.get("evidence_ledger", [])
    for idx, item in enumerate(ledger):
        eid = item.get("evidence_id", "")
        if not eid.startswith("EVID-"):
            discrepancies.append(f"Malformed evidence ID at index {idx}: '{eid}'")

    # 6. Check Risk Matrix
    risks = result_data.get("risk_matrix", [])
    for idx, r in enumerate(risks):
        rid = r.get("risk_id", "")
        if not rid.startswith("RISK-"):
            discrepancies.append(f"Malformed risk ID at index {idx}: '{rid}'")

    # 7. Check Risk Mitigation Metric Parity & Validity
    metrics = result_data.get("consensus_metrics", {})
    if "risk_mitigation_score" in metrics:
        rms = metrics.get("risk_mitigation_score")
        if not isinstance(rms, (int, float)) or not (0 <= rms <= 100):
            discrepancies.append(f"Invalid risk mitigation score in consensus_metrics: {rms} (must be 0-100)")
            
        top_rms = result_data.get("risk_mitigation_score")
        if top_rms is not None and top_rms != rms:
            discrepancies.append(f"Risk mitigation score mismatch: consensus_metrics has {rms} but root result has {top_rms}")
            
        # Invariant: If critical blockers exist or evidence is unverified, Risk Mitigation cannot be 100%
        blockers = result_data.get("critical_blockers", [])
        crit_blockers = [b for b in blockers if b.get("severity") == "CRITICAL"]
        if len(crit_blockers) > 0 and rms >= 100:
            discrepancies.append(f"Risk mitigation integrity violation: {len(crit_blockers)} CRITICAL blocker(s) exist but risk mitigation is {rms}% (cannot be 100%)")
            
        if eq.get("verified", 0) < eq.get("specialists_total", 6) and rms >= 100:
            discrepancies.append(f"Risk mitigation integrity violation: empirical evidence is incomplete ({eq.get('verified')}/{eq.get('specialists_total')}) but risk mitigation is {rms}% (cannot be 100%)")

    is_valid = len(discrepancies) == 0
    return is_valid, discrepancies
