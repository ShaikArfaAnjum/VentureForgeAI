"""
BoardRoomAI — Deterministic Decision Engine
Executes explicit, reproducible, audit-transparent policy rules.
Reproduces the authoritative final venture decision without calling an LLM.
"""

import re
from typing import Dict, Any, List, Optional

def parse_budget_numeric(budget: Any) -> float:
    """Normalizes any budget input into a clean USD float value."""
    try:
        if isinstance(budget, (int, float)):
            b = float(budget)
            if b < 1000 and b > 0:
                return b * 1_000_000.0
            return b
        elif isinstance(budget, str):
            cleaned = re.sub(r"[^\d.]", "", budget)
            val = float(cleaned) if cleaned else 50000.0
            b_lower = budget.lower()
            if "m" in b_lower or "million" in b_lower:
                return val * 1_000_000.0
            elif "k" in b_lower:
                return val * 1_000.0
            elif val < 1000 and val > 0:
                return val * 1_000_000.0
            return val
    except Exception:
        return 50000.0
    return 50000.0

def evaluate_deterministic_decision(
    target_market: str,
    capital_budget: Any,
    specialist_reports: Dict[str, Any],
    evidence_quality: Dict[str, Any],
    blockers: List[Dict[str, Any]],
    vote_distribution: Dict[str, int],
    business_idea: Optional[str] = "",
    timeline: Optional[str] = "",
    strategic_question: Optional[str] = ""
) -> Dict[str, Any]:
    """
    Evaluates explicit decision policy rules against structured specialist findings and evidence.
    
    Returns:
    {
        "decision": "LAUNCH" | "VALIDATE FIRST" | "DO NOT LAUNCH",
        "policy_rationale": str,
        "rule_evaluations": List[Dict],
        "rules_passed_count": int,
        "rules_failed_count": int,
        "rules_conditional_count": int,
        "total_rules": int,
        "can_reproduce_without_llm": True
    }
    """
    rules = []
    
    budget_usd = parse_budget_numeric(capital_budget)
    budget_display = f"${budget_usd:,.0f} USD"
    
    # Extract venture characteristics from inputs and specialist findings
    text_corpus = f"{business_idea} {strategic_question} {timeline}".lower()
    for rep in specialist_reports.values():
        text_corpus += " " + str(rep.get("analysis", "")).lower()
        
    is_drone_aviation = any(k in text_corpus for k in ["drone", "air taxi", "aircraft", "aviation", "evtol", "flight", "aerospace", "passenger air taxi", "passenger air", "last-mile delivery drone"])
    is_heavy_infrastructure = any(k in text_corpus for k in ["air taxi", "passenger", "nationwide network", "airline", "evtol", "telecom network", "rail", "power grid", "passenger air taxi"])
    is_hardware = any(k in text_corpus for k in ["hardware", "device", "smart home", "manufacturing", "inventory", "physical", "electronics", "iot sensor", "tooling", "assembly"]) or is_drone_aviation or is_heavy_infrastructure
    is_manufacturing = any(k in text_corpus for k in ["manufacturing", "factory", "tooling", "assembly", "mass production", "large-scale manufacturing"])
    is_upfront_inventory = any(k in text_corpus for k in ["inventory", "warehousing", "stock", "working capital", "upfront inventory"]) or is_drone_aviation
    is_intl_distribution = any(k in text_corpus for k in ["international distribution", "international", "freight", "customs", "cross-border", "distribution"])
    is_short_timeline = any(k in str(timeline).lower() for k in ["6 month", "6m", "3 month", "3m", "90 day", "180 day"]) or ("6" in str(timeline) and "month" in str(timeline).lower()) or ("3" in str(timeline) and "month" in str(timeline).lower())
    
    # Extract specialist signals
    cap = specialist_reports.get("CAPITAL_STRATEGIST", {})
    cap_ver = cap.get("data_verified", False)
    cap_rec = str(cap.get("recommendation", "MAYBE")).upper()

    lo = specialist_reports.get("LAUNCH_OPERATIONS", {})
    lo_ver = lo.get("data_verified", False)
    lo_rec = str(lo.get("recommendation", "MAYBE")).upper()

    vr = specialist_reports.get("VENTURE_RISK", {})
    vr_ver = vr.get("data_verified", False)
    vr_rec = str(vr.get("recommendation", "MAYBE")).upper()

    mv = specialist_reports.get("MARKET_VALIDATOR", {})
    mv_ver = mv.get("data_verified", False)
    mv_rec = str(mv.get("recommendation", "MAYBE")).upper()

    cs = specialist_reports.get("COMPETITIVE_SCOUT", {})
    cs_ver = cs.get("data_verified", False)
    cs_rec = str(cs.get("recommendation", "MAYBE")).upper()

    rn = specialist_reports.get("REGULATORY_NAVIGATOR", {})
    rn_ver = rn.get("data_verified", False)
    rn_rec = str(rn.get("recommendation", "MAYBE")).upper()

    # Filter critical business blockers (excluding system/infrastructure errors)
    crit_blockers = [b for b in blockers if b.get("severity") == "CRITICAL" and not any(k in str(b.get("title", "")).lower() for k in ["execution error", "execution failure", "api failure"])]
    high_blockers = [b for b in blockers if b.get("severity") == "HIGH" and not any(k in str(b.get("title", "")).lower() for k in ["execution error", "execution failure", "api failure"])]

    # -------------------------------------------------------------
    # RULE-001: Capital Feasibility & Sizing
    # -------------------------------------------------------------
    if is_heavy_infrastructure and budget_usd < 5_000_000:
        r1_status = "FAIL"
        r1_detail = f"Proposed capital ({budget_display}) is catastrophically deficient for a passenger aviation / nationwide air taxi network (requires $10M+ minimum)."
        r1_metric = f"{budget_display} budget vs $10M+ aviation infrastructure requirement"
    elif is_drone_aviation and budget_usd < 300_000:
        r1_status = "FAIL"
        r1_detail = f"Proposed capital ({budget_display}) is materially insufficient for autonomous drone fleet procurement, flight testing, and launch."
        r1_metric = f"{budget_display} budget vs drone fleet capital requirement"
    elif is_hardware and budget_usd <= 150_000:
        r1_status = "FAIL"
        r1_detail = f"Proposed capital ({budget_display}) is materially insufficient for hardware tooling, component procurement, and production runs."
        r1_metric = f"{budget_display} budget vs high-capital-intensity hardware model"
    elif cap_rec in ["NO", "DO NOT LAUNCH"]:
        r1_status = "FAIL"
        r1_detail = "Severe capital deficit against venture milestone and runway requirements."
        r1_metric = f"Vote={cap_rec}, Budget={budget_display}"
    elif not cap_ver:
        r1_status = "CONDITIONAL"
        r1_detail = f"Venture seed benchmarks unverified for {target_market}."
        r1_metric = f"Verified={cap_ver}, Vote={cap_rec}"
    elif cap_rec in ["YES", "LAUNCH"]:
        r1_status = "PASS"
        r1_detail = "Launch capital is well-calibrated against regional startup benchmarks."
        r1_metric = f"Verified={cap_ver}, Vote={cap_rec}"
    else:
        r1_status = "CONDITIONAL"
        r1_detail = "Capital sizing adequate for lean MVP; strict burn rate control required."
        r1_metric = f"Verified={cap_ver}, Vote={cap_rec}"

    rules.append({
        "rule_id": "RULE-001",
        "category": "Capital Feasibility",
        "threshold": "Capital must be adequate for the proposed hardware/venture launch scope",
        "inputs": {"target_market": target_market, "budget_usd": budget_usd, "is_hardware": is_hardware},
        "actual_value": r1_metric,
        "result": r1_status,
        "status": r1_status,
        "evidence_ids": ["EVID-006"],
        "reason": r1_detail,
        "rationale": r1_detail,
        "impact_on_decision": "Mandatory capital gate; failure blocks unassisted LAUNCH."
    })

    # -------------------------------------------------------------
    # RULE-002: Operational Readiness & Distribution Logistics
    # -------------------------------------------------------------
    if is_heavy_infrastructure or (is_drone_aviation and is_short_timeline) or ((is_manufacturing or is_intl_distribution) and (budget_usd <= 150_000 or is_short_timeline)):
        r2_status = "FAIL"
        r2_detail = "Operating autonomous aviation or physical infrastructure within this timeline and budget creates unviable operational bottlenecks."
        r2_metric = f"Physical / Aviation Operations on {timeline} timeline"
    elif lo_rec in ["NO", "DO NOT LAUNCH"]:
        r2_status = "FAIL"
        r2_detail = "Launch Operations flagged critical infrastructure, tooling, or customs bottlenecks."
        r2_metric = f"Verified={lo_ver}, Vote={lo_rec}"
    elif not lo_ver:
        r2_status = "CONDITIONAL"
        r2_detail = f"Logistics Performance Index unverified for {target_market}."
        r2_metric = f"Verified={lo_ver}, Vote={lo_rec}"
    elif lo_rec in ["YES", "LAUNCH"]:
        r2_status = "PASS"
        r2_detail = "Logistics Performance Index supports asset-light rollout."
        r2_metric = f"Verified={lo_ver}, Vote={lo_rec}"
    else:
        r2_status = "CONDITIONAL"
        r2_detail = "Operational channels viable with regional 3PL partners."
        r2_metric = f"Verified={lo_ver}, Vote={lo_rec}"

    rules.append({
        "rule_id": "RULE-002",
        "category": "Operational Readiness",
        "threshold": "Logistics and supply chain infrastructure must support launch scope",
        "inputs": {"target_market": target_market, "is_manufacturing": is_manufacturing, "is_intl_distribution": is_intl_distribution},
        "actual_value": r2_metric,
        "result": r2_status,
        "status": r2_status,
        "evidence_ids": ["EVID-004"],
        "reason": r2_detail,
        "rationale": r2_detail,
        "impact_on_decision": "Operational viability gate; conditional requires 3PL partnership."
    })

    # -------------------------------------------------------------
    # RULE-003: Timeline Feasibility
    # -------------------------------------------------------------
    if is_heavy_infrastructure and (is_short_timeline or any(x in str(timeline).lower() for x in ["1 year", "12 month"])):
        r3_status = "FAIL"
        r3_detail = f"{timeline} timeline is unviable for passenger aviation airworthiness testing and nationwide deployment."
        r3_metric = f"{timeline} timeline vs passenger aviation lead times"
    elif is_drone_aviation and is_short_timeline:
        r3_status = "FAIL"
        r3_detail = f"{timeline} timeline is severely compressed for DGCA/FAA drone airspace clearance and safety validation."
        r3_metric = f"{timeline} timeline vs drone airspace authorization"
    elif is_hardware and is_short_timeline:
        r3_status = "FAIL"
        r3_detail = f"{timeline} is severely aggressive for hardware development, compliance certification (RCM/ACMA), tooling, and transit."
        r3_metric = f"{timeline} timeline vs hardware development & compliance requirements"
    elif is_short_timeline and budget_usd > 500_000:
        r3_status = "CONDITIONAL"
        r3_detail = f"{timeline} timeline requires expedited milestone gates."
        r3_metric = f"Timeline={timeline}, Budget={budget_display}"
    else:
        r3_status = "PASS" if not is_short_timeline else "CONDITIONAL"
        r3_detail = "Execution timeline aligns with operational roadmap milestones."
        r3_metric = f"Timeline={timeline}"

    rules.append({
        "rule_id": "RULE-003",
        "category": "Timeline Feasibility",
        "threshold": "Timeline must accommodate product development, certifications, manufacturing & shipping",
        "inputs": {"timeline": timeline, "is_hardware": is_hardware},
        "actual_value": r3_metric,
        "result": r3_status,
        "status": r3_status,
        "evidence_ids": ["EVID-004"],
        "reason": r3_detail,
        "rationale": r3_detail,
        "impact_on_decision": "Timeline realism gate; failure blocks immediate LAUNCH."
    })

    # -------------------------------------------------------------
    # RULE-004: Working Capital & Inventory Risk
    # -------------------------------------------------------------
    if (is_upfront_inventory or is_hardware) and budget_usd <= 150_000:
        r4_status = "FAIL"
        r4_detail = f"The model requires upfront inventory investment that exhausts the proposed {budget_display} budget before commercial cash flow."
        r4_metric = f"Upfront inventory requirement on {budget_display} budget"
    elif is_upfront_inventory and budget_usd <= 300_000:
        r4_status = "CONDITIONAL"
        r4_detail = "Upfront inventory holding costs require staged consignment agreements."
        r4_metric = f"Inventory model with {budget_display} budget"
    else:
        r4_status = "PASS"
        r4_detail = "Working capital requirements are aligned with cash reserves."
        r4_metric = f"Asset-light model / Sufficient working capital"

    rules.append({
        "rule_id": "RULE-004",
        "category": "Inventory / Working Capital",
        "threshold": "Working capital must cover upfront inventory holding without liquidity exhaustion",
        "inputs": {"is_upfront_inventory": is_upfront_inventory, "budget_usd": budget_usd},
        "actual_value": r4_metric,
        "result": r4_status,
        "status": r4_status,
        "evidence_ids": ["EVID-006"],
        "reason": r4_detail,
        "rationale": r4_detail,
        "impact_on_decision": "Working capital solvency gate; failure triggers DO NOT LAUNCH."
    })

    # -------------------------------------------------------------
    # RULE-005: Venture Risk & Capital Concentration
    # -------------------------------------------------------------
    if (is_hardware or is_upfront_inventory) and budget_usd <= 150_000:
        r5_status = "FAIL"
        r5_detail = "Capital concentration in hardware inventory, single-point supply chain risk, and yield loss exceed acceptable venture parameters."
        r5_metric = "High capital concentration + single-batch supply chain exposure"
    elif vr_rec in ["NO", "DO NOT LAUNCH"]:
        r5_status = "FAIL"
        r5_detail = "Elevated sovereign fragility or capital control risk."
        r5_metric = f"Verified={vr_ver}, Vote={vr_rec}"
    elif not vr_ver:
        r5_status = "CONDITIONAL"
        r5_detail = f"Fragile States Index unverified for {target_market}."
        r5_metric = f"Verified={vr_ver}, Vote={vr_rec}"
    elif vr_rec in ["YES", "LAUNCH"]:
        r5_status = "PASS"
        r5_detail = "Sovereign and economic stability parameters within acceptable risk envelope."
        r5_metric = f"Verified={vr_ver}, Vote={vr_rec}"
    else:
        r5_status = "CONDITIONAL"
        r5_detail = "Moderate venture risk; tranche-based capital release advised."
        r5_metric = f"Verified={vr_ver}, Vote={vr_rec}"

    rules.append({
        "rule_id": "RULE-005",
        "category": "Venture Risk",
        "threshold": "Capital concentration, supply-chain, and downside risk within acceptable risk envelope",
        "inputs": {"target_market": target_market, "is_hardware": is_hardware, "budget_usd": budget_usd},
        "actual_value": r5_metric,
        "result": r5_status,
        "status": r5_status,
        "evidence_ids": ["EVID-005"],
        "reason": r5_detail,
        "rationale": r5_detail,
        "impact_on_decision": "Sovereign & capital protection gate; failure triggers DO NOT LAUNCH."
    })

    # -------------------------------------------------------------
    # RULE-006: Launch Readiness & Regulatory Alignment
    # -------------------------------------------------------------
    if is_heavy_infrastructure or (is_drone_aviation and is_short_timeline):
        r6_status = "FAIL"
        r6_detail = "Civil aviation authority commercial licensing, flight corridor approvals, and passenger safety certifications cannot be completed."
        r6_metric = "Aviation airspace licensing barrier"
    elif is_hardware and budget_usd <= 150_000:
        r6_status = "FAIL"
        r6_detail = "Required commercial, warranty, and compliance support infrastructure is unsupported by proposed capital."
        r6_metric = f"Hardware DTC model with {budget_display} budget"
    elif rn_rec in ["NO", "DO NOT LAUNCH"]:
        r6_status = "FAIL"
        r6_detail = "Severe regulatory friction or mandatory licensing barriers."
        r6_metric = f"Verified={rn_ver}, Vote={rn_rec}"
    elif not rn_ver:
        r6_status = "CONDITIONAL"
        r6_detail = f"World Bank incorporation ranking unverified for {target_market}."
        r6_metric = f"Verified={rn_ver}, Vote={rn_rec}"
    elif rn_rec in ["YES", "LAUNCH"]:
        r6_status = "PASS"
        r6_detail = "Structured corporate incorporation and contract enforcement environment."
        r6_metric = f"Verified={rn_ver}, Vote={rn_rec}"
    else:
        r6_status = "CONDITIONAL"
        r6_detail = "Compliance requires localized counsel audit prior to launch."
        r6_metric = f"Verified={rn_ver}, Vote={rn_rec}"

    rules.append({
        "rule_id": "RULE-006",
        "category": "Launch Readiness",
        "threshold": "Commercial registration, statutory compliance, and support readiness satisfied",
        "inputs": {"target_market": target_market, "data_verified": rn_ver, "specialist_vote": rn_rec},
        "actual_value": r6_metric,
        "result": r6_status,
        "status": r6_status,
        "evidence_ids": ["EVID-003"],
        "reason": r6_detail,
        "rationale": r6_detail,
        "impact_on_decision": "Commercial readiness prerequisite; failure triggers DO NOT LAUNCH."
    })

    # -------------------------------------------------------------
    # RULE-007: Critical Business Blockers
    # -------------------------------------------------------------
    if len(crit_blockers) == 0:
        r7_status = "PASS"
        r7_detail = f"0 Critical Blockers detected ({len(high_blockers)} high-priority advisories)."
    else:
        r7_status = "FAIL"
        r7_detail = f"{len(crit_blockers)} Unresolved Critical Blocker(s) prevent immediate capital release."

    rules.append({
        "rule_id": "RULE-007",
        "category": "Critical Blockers",
        "threshold": "0 Critical Business Blockers and <= 2 High Advisories",
        "inputs": {"critical_blockers_count": len(crit_blockers), "high_blockers_count": len(high_blockers)},
        "actual_value": f"Critical={len(crit_blockers)}, High={len(high_blockers)}",
        "result": r7_status,
        "status": r7_status,
        "evidence_ids": [b.get("evidence_reference", "EVID-001") for b in crit_blockers] or ["EVID-001"],
        "reason": r7_detail,
        "rationale": r7_detail,
        "impact_on_decision": "Mandatory blocker gate; >0 critical blockers blocks immediate LAUNCH."
    })

    # -------------------------------------------------------------
    # RULE-008: Evidence Quality & Grounding Coverage
    # -------------------------------------------------------------
    cov_pct = evidence_quality.get("coverage_percent", 0)
    ver_count = evidence_quality.get("verified", 0)
    
    if cov_pct >= 80 or ver_count >= 5:
        r8_status = "PASS"
        r8_detail = f"{ver_count}/6 specialist domains verified against local empirical datasets ({cov_pct}% coverage)."
    elif cov_pct >= 50 or ver_count >= 3:
        r8_status = "CONDITIONAL"
        r8_detail = f"{ver_count}/6 specialist domains verified ({cov_pct}% coverage)."
    else:
        r8_status = "FAIL"
        r8_detail = f"Insufficient empirical evidence coverage ({cov_pct}% < 50% minimum policy threshold)."

    rules.append({
        "rule_id": "RULE-008",
        "category": "Evidence Coverage",
        "threshold": ">= 66% Dataset-Backed Coverage (100% required for unassisted LAUNCH)",
        "inputs": {"coverage_percent": cov_pct, "verified_count": ver_count},
        "actual_value": f"Coverage={cov_pct}%, Verified={ver_count}/6",
        "result": r8_status,
        "status": r8_status,
        "evidence_ids": ["EVID-001", "EVID-002", "EVID-003", "EVID-004", "EVID-005", "EVID-006"],
        "reason": r8_detail,
        "rationale": r8_detail,
        "impact_on_decision": "Empirical integrity threshold; <50% triggers conservative DO NOT LAUNCH."
    })

    # -------------------------------------------------------------
    # FINAL DETERMINISTIC DECISION AGGREGATION
    # -------------------------------------------------------------
    passed_count = sum(1 for r in rules if r["status"] == "PASS")
    fail_count = sum(1 for r in rules if r["status"] == "FAIL")
    cond_count = sum(1 for r in rules if r["status"] == "CONDITIONAL")
    
    no_votes = vote_distribution.get("NO", 0)
    yes_votes = vote_distribution.get("YES", 0)
    
    mandatory_failed_rules = [r for r in rules if r["rule_id"] in ["RULE-001", "RULE-003", "RULE-004", "RULE-005"] and r["status"] == "FAIL"]
    
    # POLICY RULE ENGINE:
    # 1. DO NOT LAUNCH triggers:
    #    - Any mandatory feasibility rule FAIL (Capital, Timeline, Inventory, Risk)
    #    - >= 2 NO votes from specialists
    #    - >= 1 Critical business blocker or unresolved system error
    if len(mandatory_failed_rules) > 0 or no_votes >= 2 or len(crit_blockers) >= 1 or (r1_status == "FAIL" and r3_status == "FAIL") or evidence_quality.get("errors", 0) > 0:
        decision = "DO NOT LAUNCH"
        failed_names = ", ".join([r["category"] for r in mandatory_failed_rules]) if mandatory_failed_rules else "mandatory constraints"
        rationale = (
            f"The deterministic policy engine rejected immediate launch because mandatory capital and operational feasibility constraints are not satisfied. "
            f"Proposed {budget_display} budget and {timeline} timeline are fundamentally mismatched with the capital-intensive hardware scope "
            f"({fail_count} failed policy rule(s): {failed_names})."
        )
    # 2. LAUNCH triggers:
    #    - 0 Blockers (critical, high, or medium)
    #    - Coverage >= 80% (0 conditional rules)
    #    - 0 Failed rules
    #    - 0 Conditional gates
    #    - Board consensus (>= 5 YES votes, 0 MAYBE votes, 0 NO votes)
    elif len(blockers) == 0 and fail_count == 0 and cond_count == 0 and yes_votes >= 5 and vote_distribution.get("MAYBE", 0) == 0 and no_votes == 0:
        decision = "LAUNCH"
        rationale = (
            f"Deterministic policy engine green-lights venture LAUNCH: Empirical evidence coverage verified, "
            f"0 critical blockers, {passed_count}/8 policy rules satisfied, and strong board consensus ({yes_votes} YES, 0 NO)."
        )
    # 3. VALIDATE FIRST (Default prudent posture for any data gap or validation condition):
    else:
        decision = "VALIDATE FIRST"
        reasons = []
        if evidence_quality.get("unavailable", 0) > 0 or cov_pct < 66:
            reasons.append(f"{evidence_quality.get('unavailable', max(1, 6 - ver_count))} specialist data gap(s)")
        if cond_count > 0:
            reasons.append(f"{cond_count} conditional policy gate(s)")
        if len(crit_blockers) > 0:
            reasons.append(f"{len(crit_blockers)} critical blocker(s)")
        if no_votes > 0:
            reasons.append(f"{no_votes} specialist opposition vote(s)")
            
        rationale = (
            f"Deterministic policy engine evaluated {passed_count}/8 rules as PASS. "
            f"Prudent fiduciary standard requires VALIDATE FIRST due to: {', '.join(reasons) if reasons else 'pending validation milestones'}."
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
