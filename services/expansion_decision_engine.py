"""
BoardRoomAI — Deterministic Decision Engine for Corporate Expansion (Track A)
Evaluates 9 corporate expansion policy rules against user inputs, empirical datasets, and specialist findings.
Produces deterministic, reproducible decisions:
- ENTER MARKET
- ENTER WITH CONDITIONS
- DEFER / VALIDATE
- DO NOT ENTER
"""

import re
from typing import Dict, Any, List, Optional
from config import parse_budget_numeric, format_budget_display

def evaluate_expansion_decision(
    company: str,
    target_market: str,
    budget: Any,
    timeline: str,
    question: str,
    specialist_reports: Dict[str, Any],
    evidence_quality: Dict[str, Any],
    blockers: List[Dict[str, Any]],
    vote_distribution: Dict[str, int],
    business_model: Optional[str] = ""
) -> Dict[str, Any]:
    """
    Authoritative deterministic evaluation for Corporate Expansion.
    Evaluates 9 domain-specific corporate expansion policy rules.
    """
    rules = []
    
    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    # Text corpus for domain keywords
    text_corpus = f"{company} {target_market} {question} {timeline} {business_model}".lower()
    for rep in specialist_reports.values():
        text_corpus += " " + str(rep.get("analysis", "")).lower()
        
    is_risky = any(k in text_corpus for k in ["risky", "crypto", "volatile", "dangerous", "unstable", "war", "sanction"])
    is_hardware = any(k in text_corpus for k in ["hardware", "device", "smart home", "manufacturing", "inventory", "physical", "electronics", "iot sensor", "tooling", "assembly"])
    is_manufacturing = any(k in text_corpus for k in ["manufacturing", "factory", "tooling", "assembly", "mass production", "large-scale manufacturing"])
    is_short_timeline = any(k in str(timeline).lower() for k in ["6 month", "6m", "3 month", "3m", "90 day", "180 day"]) or ("6" in str(timeline) and "month" in str(timeline).lower())
    
    # Extract specialist signals
    res = specialist_reports.get("RESEARCHER", {})
    res_rec = str(res.get("recommendation", "MAYBE")).upper()
    res_ver = res.get("data_verified", False)

    comp = specialist_reports.get("COMPETITOR", {})
    comp_rec = str(comp.get("recommendation", "MAYBE")).upper()
    comp_ver = comp.get("data_verified", False)

    leg = specialist_reports.get("LEGAL", {})
    leg_rec = str(leg.get("recommendation", "MAYBE")).upper()
    leg_ver = leg.get("data_verified", False)

    ops = specialist_reports.get("OPERATIONS", {})
    ops_rec = str(ops.get("recommendation", "MAYBE")).upper()
    ops_ver = ops.get("data_verified", False)

    risk = specialist_reports.get("RISK", {})
    risk_rec = str(risk.get("recommendation", "MAYBE")).upper()
    risk_ver = risk.get("data_verified", False)

    cfo = specialist_reports.get("CFO", {})
    cfo_rec = str(cfo.get("recommendation", "MAYBE")).upper()
    cfo_ver = cfo.get("data_verified", False)

    # Filter critical business blockers
    crit_blockers = [b for b in blockers if b.get("severity") == "CRITICAL" and not any(k in str(b.get("title", "")).lower() for k in ["execution error", "execution failure", "api failure"])]
    high_blockers = [b for b in blockers if b.get("severity") == "HIGH" and not any(k in str(b.get("title", "")).lower() for k in ["execution error", "execution failure", "api failure"])]

    # -------------------------------------------------------------
    # RULE-001: Market Attractiveness & Demand Viability
    # -------------------------------------------------------------
    if res_rec in ["NO", "REJECT"]:
        r1_status = "FAIL"
        r1_detail = f"Market research identified insufficient demand or unfavorable customer readiness in {target_market} for {company}."
    elif res_rec in ["YES", "ENTER"]:
        r1_status = "PASS"
        r1_detail = f"Validated market opportunity, addressable TAM, and favorable customer demand curve for {company} in {target_market}."
    else:
        r1_status = "CONDITIONAL"
        r1_detail = f"Moderate market demand in {target_market}; customer adoption milestones required during pilot rollout."

    rules.append({
        "rule_id": "RULE-001",
        "category": "Market Attractiveness",
        "threshold": "TAM and demand curve must demonstrate sustainable expansion volume",
        "inputs": {"market": target_market, "vote": res_rec, "verified": res_ver},
        "actual_value": f"Researcher Vote={res_rec}, Verified={res_ver}",
        "result": r1_status,
        "status": r1_status,
        "evidence_ids": ["EVID-001"],
        "reason": r1_detail,
        "rationale": r1_detail,
        "impact_on_decision": "Demand gate; failure blocks unassisted market expansion."
    })

    # -------------------------------------------------------------
    # RULE-002: Competitive Position & Moat
    # -------------------------------------------------------------
    if comp_rec in ["NO", "REJECT"]:
        r2_status = "FAIL"
        r2_detail = f"Severe incumbent concentration or insurmountable competitive barriers in {target_market} for {company}."
    elif comp_rec in ["YES", "ENTER"]:
        r2_status = "PASS"
        r2_detail = f"{company} demonstrates defensible differentiation and agile positioning against incumbents in {target_market}."
    else:
        r2_status = "CONDITIONAL"
        r2_detail = f"Incumbents hold established market share in {target_market}; requires targeted niche positioning."

    rules.append({
        "rule_id": "RULE-002",
        "category": "Competitive Position",
        "threshold": "Defensible differentiation and viable moat against regional incumbents",
        "inputs": {"market": target_market, "vote": comp_rec, "verified": comp_ver},
        "actual_value": f"Competitive Intel Vote={comp_rec}, Verified={comp_ver}",
        "result": r2_status,
        "status": r2_status,
        "evidence_ids": ["EVID-002"],
        "reason": r2_detail,
        "rationale": r2_detail,
        "impact_on_decision": "Competitive feasibility gate; conditional requires niche focus."
    })

    # -------------------------------------------------------------
    # RULE-003: Regulatory Clearance & Sovereign Compliance
    # -------------------------------------------------------------
    if leg_rec in ["NO", "REJECT"]:
        r3_status = "FAIL"
        r3_detail = f"Prohibitive foreign regulatory barriers, strict licensing caps, or statutory compliance risks in {target_market}."
    elif leg_rec in ["YES", "ENTER"]:
        r3_status = "PASS"
        r3_detail = f"Favorable Ease of Doing Business rankings and predictable commercial incorporation framework in {target_market}."
    else:
        r3_status = "CONDITIONAL"
        r3_detail = f"Regulatory filings and localized compliance audits required prior to commercial launch in {target_market}."

    rules.append({
        "rule_id": "RULE-003",
        "category": "Regulatory Clearance",
        "threshold": "Foreign compliance, entity formation, and statutory clearance within roadmap",
        "inputs": {"market": target_market, "vote": leg_rec, "verified": leg_ver},
        "actual_value": f"Legal Counsel Vote={leg_rec}, Verified={leg_ver}",
        "result": r3_status,
        "status": r3_status,
        "evidence_ids": ["EVID-003"],
        "reason": r3_detail,
        "rationale": r3_detail,
        "impact_on_decision": "Legal gate; failure blocks market entry."
    })

    # -------------------------------------------------------------
    # RULE-004: Operational & Supply Chain Feasibility
    # -------------------------------------------------------------
    if ops_rec in ["NO", "REJECT"] or (is_manufacturing and is_short_timeline and budget_usd <= 200_000):
        r4_status = "FAIL"
        r4_detail = f"Operational logistics, supply chain setup, or staffing cannot be delivered within {timeline} on {budget_display}."
    elif ops_rec in ["YES", "ENTER"]:
        r4_status = "PASS"
        r4_detail = f"Logistics Performance Index and regional infrastructure support {company}'s expansion across {timeline}."
    else:
        r4_status = "CONDITIONAL"
        r4_detail = f"Operational rollout in {target_market} requires localized 3PL distribution and talent integration."

    rules.append({
        "rule_id": "RULE-004",
        "category": "Operational Feasibility",
        "threshold": "Logistics, supply chain, and execution capability support expansion timeline",
        "inputs": {"market": target_market, "vote": ops_rec, "timeline": timeline},
        "actual_value": f"COO Vote={ops_rec}, Timeline={timeline}",
        "result": r4_status,
        "status": r4_status,
        "evidence_ids": ["EVID-004"],
        "reason": r4_detail,
        "rationale": r4_detail,
        "impact_on_decision": "Operations gate; conditional requires 3PL partnership."
    })

    # -------------------------------------------------------------
    # RULE-005: Sovereign & Macroeconomic Risk
    # -------------------------------------------------------------
    if risk_rec in ["NO", "REJECT"] or is_risky:
        r5_status = "FAIL"
        r5_detail = f"Elevated country fragility, currency volatility, or geopolitical exposure in {target_market} exceed risk envelope."
    elif risk_rec in ["YES", "ENTER"]:
        r5_status = "PASS"
        r5_detail = f"Sovereign fragility and macroeconomic indicators fall within stable, acceptable risk parameters for {company}."
    else:
        r5_status = "CONDITIONAL"
        r5_detail = f"Moderate macroeconomic exposure; requires tranche-based capital deployment and currency hedging."

    rules.append({
        "rule_id": "RULE-005",
        "category": "Sovereign Risk",
        "threshold": "Macroeconomic, currency, and geopolitical risk within manageable envelope",
        "inputs": {"market": target_market, "vote": risk_rec, "is_risky": is_risky},
        "actual_value": f"CRO Vote={risk_rec}, Sovereign Risk Check",
        "result": r5_status,
        "status": r5_status,
        "evidence_ids": ["EVID-005"],
        "reason": r5_detail,
        "rationale": r5_detail,
        "impact_on_decision": "Risk protection gate; failure triggers DO NOT ENTER."
    })

    # -------------------------------------------------------------
    # RULE-006: Capital Feasibility & Budget Sizing
    # -------------------------------------------------------------
    if is_hardware and budget_usd <= 150_000:
        r6_status = "FAIL"
        r6_detail = f"Proposed capital allocation ({budget_display}) is critically deficient for hardware manufacturing and physical expansion in {target_market}."
    elif cfo_rec in ["NO", "REJECT"]:
        r6_status = "FAIL"
        r6_detail = f"Capital allocation of {budget_display} does not support expansion runway and payback milestones."
    elif cfo_rec in ["YES", "ENTER"]:
        r6_status = "PASS"
        r6_detail = f"Budget of {budget_display} is properly calibrated to fund {company}'s expansion roadmap across {timeline}."
    else:
        r6_status = "CONDITIONAL"
        r6_detail = f"Capital allocation of {budget_display} is viable with strict milestone-based burn governance."

    rules.append({
        "rule_id": "RULE-006",
        "category": "Capital Feasibility",
        "threshold": "Proposed budget must adequately fund operational runway and reach break-even",
        "inputs": {"budget_usd": budget_usd, "vote": cfo_rec, "timeline": timeline},
        "actual_value": f"Budget={budget_display}, CFO Vote={cfo_rec}",
        "result": r6_status,
        "status": r6_status,
        "evidence_ids": ["EVID-006"],
        "reason": r6_detail,
        "rationale": r6_detail,
        "impact_on_decision": "Capital solvency gate; failure triggers DO NOT ENTER."
    })

    # -------------------------------------------------------------
    # RULE-007: Timeline Feasibility
    # -------------------------------------------------------------
    if is_hardware and is_short_timeline:
        r7_status = "FAIL"
        r7_detail = f"{timeline} is severely compressed for hardware prototyping, certifications, tooling, and distribution rollout."
    elif is_short_timeline and budget_usd > 10_000_000:
        r7_status = "CONDITIONAL"
        r7_detail = f"{timeline} target timeline requires expedited milestone gating."
    else:
        r7_status = "PASS"
        r7_detail = f"Execution roadmap is realistic and achievable within {timeline}."

    rules.append({
        "rule_id": "RULE-007",
        "category": "Timeline Feasibility",
        "threshold": "Timeline must accommodate licensing, operational ramp-up, and commercial launch",
        "inputs": {"timeline": timeline, "is_hardware": is_hardware},
        "actual_value": f"Timeline={timeline}",
        "result": r7_status,
        "status": r7_status,
        "evidence_ids": ["EVID-004"],
        "reason": r7_detail,
        "rationale": r7_detail,
        "impact_on_decision": "Timeline realism gate; failure blocks immediate entry."
    })

    # -------------------------------------------------------------
    # RULE-008: Critical Business Blockers
    # -------------------------------------------------------------
    if len(crit_blockers) == 0:
        r8_status = "PASS"
        r8_detail = f"0 Critical Blockers detected ({len(high_blockers)} high-priority conditions active)."
    else:
        r8_status = "FAIL"
        r8_detail = f"{len(crit_blockers)} Unresolved Critical Blocker(s) prevent immediate market entry."

    rules.append({
        "rule_id": "RULE-008",
        "category": "Critical Blockers",
        "threshold": "0 Critical Business Blockers required for unconditioned expansion",
        "inputs": {"critical_count": len(crit_blockers), "high_count": len(high_blockers)},
        "actual_value": f"Critical={len(crit_blockers)}, High={len(high_blockers)}",
        "result": r8_status,
        "status": r8_status,
        "evidence_ids": [b.get("evidence_reference", "EVID-001") for b in crit_blockers] or ["EVID-001"],
        "reason": r8_detail,
        "rationale": r8_detail,
        "impact_on_decision": "Fiduciary gate; >0 critical blockers prevents ENTER MARKET."
    })

    # -------------------------------------------------------------
    # RULE-009: Evidence Grounding Coverage
    # -------------------------------------------------------------
    cov_pct = evidence_quality.get("coverage_percent", 0)
    ver_count = evidence_quality.get("verified_dimensions", evidence_quality.get("verified", 0))
    req_dims = evidence_quality.get("required_dimensions", 7)
    
    if cov_pct >= 66 and ver_count >= 4:
        r9_status = "PASS"
        r9_detail = f"{ver_count}/{req_dims} evidence dimensions verified against empirical datasets ({cov_pct}% coverage)."
    elif cov_pct >= 33 or ver_count >= 2:
        r9_status = "CONDITIONAL"
        r9_detail = f"{ver_count}/{req_dims} evidence dimensions empirically verified ({cov_pct}% coverage); supplemental field validation required."
    else:
        r9_status = "CONDITIONAL"
        r9_detail = f"Empirical data unavailable ({ver_count}/{req_dims} verified, {cov_pct}% coverage) — conclusion is model-inferred and requires validation."

    rules.append({
        "rule_id": "RULE-009",
        "category": "Evidence Coverage",
        "threshold": ">= 66% Dataset-Backed Grounding across required evidence dimensions",
        "inputs": {"coverage_percent": cov_pct, "verified_count": ver_count, "required_dimensions": req_dims},
        "actual_value": f"Coverage={cov_pct}%, Verified={ver_count}/{req_dims}",
        "result": r9_status,
        "status": r9_status,
        "evidence_ids": ["EVID-001", "EVID-002", "EVID-003", "EVID-004", "EVID-005", "EVID-006"],
        "reason": r9_detail,
        "rationale": r9_detail,
        "impact_on_decision": "Data integrity threshold; insufficient empirical coverage prevents unconditioned entry."
    })

    # -------------------------------------------------------------
    # FINAL DETERMINISTIC DECISION AGGREGATION
    # -------------------------------------------------------------
    passed_count = sum(1 for r in rules if r["status"] == "PASS")
    fail_count = sum(1 for r in rules if r["status"] == "FAIL")
    cond_count = sum(1 for r in rules if r["status"] == "CONDITIONAL")
    
    no_votes = vote_distribution.get("NO", 0)
    yes_votes = vote_distribution.get("YES", 0)
    
    mandatory_failed_rules = [r for r in rules if r["rule_id"] in ["RULE-001", "RULE-003", "RULE-005", "RULE-006"] and r["status"] == "FAIL"]
    
    # 1. DO NOT ENTER:
    # Triggered by mandatory rule failure, >= 2 NO votes, or capital/sovereign blocker
    if len(mandatory_failed_rules) > 0 or no_votes >= 2 or len(crit_blockers) >= 2 or (r6_status == "FAIL" and r7_status == "FAIL"):
        decision = "DO NOT ENTER"
        failed_names = ", ".join([r["category"] for r in mandatory_failed_rules]) if mandatory_failed_rules else "mandatory feasibility gates"
        rationale = (
            f"The deterministic policy engine rejected expansion for {company} into {target_market}. "
            f"Mandatory constraints failed ({fail_count} failed rule(s): {failed_names}). "
            f"Capital allocation of {budget_display} or regulatory/sovereign risks present fatal execution friction."
        )
    # 2. ENTER MARKET:
    # 0 Blockers, 0 Failed rules, <= 2 conditional, high board consensus (>= 4 YES, 0 NO), AND verified empirical coverage (>= 50% coverage, >= 3 verified dimensions)
    elif len(crit_blockers) == 0 and fail_count == 0 and cond_count <= 2 and yes_votes >= 4 and no_votes == 0 and cov_pct >= 50 and ver_count >= 3:
        decision = "ENTER MARKET"
        rationale = (
            f"Deterministic policy engine green-lights market expansion for {company} into {target_market}: "
            f"0 critical blockers, {passed_count}/9 policy rules satisfied, validated empirical grounding ({cov_pct}% coverage), "
            f"and strong executive consensus ({yes_votes} YES, 0 NO)."
        )
    # 3. ENTER WITH CONDITIONS:
    # Viable expansion thesis with 1-3 conditional operational or regulatory gates, OR requiring empirical validation due to limited/unverified dataset coverage
    elif fail_count == 0 and no_votes <= 1:
        decision = "ENTER WITH CONDITIONS"
        if cov_pct < 50 or ver_count < 3:
            rationale = (
                f"Deterministic policy engine approves expansion with conditional validation safeguards for {company} in {target_market}. "
                f"Strategic executive consensus is favorable ({yes_votes} YES, {no_votes} NO), but empirical dataset coverage is limited ({ver_count}/{req_dims} verified, {cov_pct}% coverage). "
                f"Commercial rollout is contingent upon satisfying {cond_count} milestone gate(s) and completing primary field validation."
            )
        else:
            rationale = (
                f"Deterministic policy engine approves expansion with conditional safeguards for {company} in {target_market}. "
                f"{passed_count}/9 rules passed with {cond_count} conditional milestone gates (licensing, 3PL setup, or capital gating)."
            )
    # 4. DEFER / VALIDATE:
    # Substantial uncertainty or data gaps
    else:
        decision = "DEFER / VALIDATE"
        rationale = (
            f"Deterministic policy engine advises deferring market expansion for {company} into {target_market}. "
            f"Requires pilot customer validation and regulatory clearance before committing {budget_display}."
        )
        
    return {
        "decision": decision,
        "policy_rationale": rationale,
        "rule_evaluations": rules,
        "rules_passed_count": passed_count,
        "rules_failed_count": fail_count,
        "rules_conditional_count": cond_count,
        "total_rules": len(rules),
        "can_reproduce_without_llm": True
    }
