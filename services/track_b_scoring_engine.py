"""
BoardRoomAI — Track B Launch Dynamic Scoring Engine.

Provides the authoritative, centralized scoring logic for Track B (New Business Launch).
Calculates mathematically grounded, reproducible scores across 4 key dimensions + overall score:
1. Opportunity Score (0-100)
2. Risk Mitigation Score (0-100)
3. Launch Readiness Score (0-100) [market_readiness alias]
4. Capital Feasibility Score (0-100) [financial_feasibility alias]
5. Overall Launch Score (0-100)

CRITICAL DESIGN RULES:
- 100% deterministic and reproducible — NO random numbers.
- NO hardcoded 100% / 88% default fallback scores.
- Different inputs (ideas, budgets, timelines, markets, risks) MUST produce meaningfully different scores.
- Capital Feasibility genuinely scales with budget vs. domain capital requirements.
- Launch Readiness genuinely scales with timeline vs. regulatory and operational complexity.
- Opportunity reflects real demand, competitive differentiation, and realizable TAM.
- Risk Mitigation reflects actual identified risk severities, blockers, and residual exposures.
- Generates transparent, human-readable explanations for every metric.
- Shared canonical object used identically by Streamlit UI, consensus engine, and ReportLab PDF.
"""

import re
from typing import Dict, Any, List, Optional

def parse_budget_numeric(budget: Any) -> float:
    """Parses arbitrary budget representations into a clean float USD amount."""
    if isinstance(budget, (int, float)):
        b = float(budget)
        if 0 < b < 1000:
            return b * 1_000_000.0
        return b
    if isinstance(budget, str):
        cleaned = re.sub(r"[^\d.]", "", budget)
        val = float(cleaned) if cleaned else 100_000.0
        b_lower = budget.lower()
        if "billion" in b_lower or "b" in b_lower:
            return val * 1_000_000_000.0
        elif "million" in b_lower or "m" in b_lower:
            return val * 1_000_000.0
        elif "k" in b_lower:
            return val * 1_000.0
        elif 0 < val < 1000:
            return val * 1_000_000.0
        return val
    return 100_000.0


def parse_timeline_months(timeline_str: Any) -> float:
    """Parses timeline strings into numeric months."""
    if not timeline_str:
        return 12.0
    s = str(timeline_str).lower().strip()
    match_yr = re.search(r"([\d.]+)\s*(?:year|yr)", s)
    if match_yr:
        return float(match_yr.group(1)) * 12.0
    match_mo = re.search(r"([\d.]+)\s*(?:month|mo|m\b)", s)
    if match_mo:
        return float(match_mo.group(1))
    match_day = re.search(r"([\d.]+)\s*(?:day|d\b)", s)
    if match_day:
        return max(1.0, float(match_day.group(1)) / 30.0)
    match_num = re.search(r"([\d.]+)", s)
    if match_num:
        val = float(match_num.group(1))
        return val * 12.0 if val <= 5.0 else val
    return 12.0


def classify_venture_archetype(venture_idea: str, strategic_question: str = "", business_model: str = "") -> Dict[str, Any]:
    """
    Classifies a new business proposal into an operational archetype with capital and timeline baselines.
    """
    corpus = f"{venture_idea} {strategic_question} {business_model}".lower()

    is_air_taxi = any(w in corpus for w in [
        "air taxi", "passenger air", "passenger drone", "evtol", "flying taxi",
        "aerial taxi", "aviation network", "airline", "passenger aviation", "passenger air taxi"
    ])
    is_heavy_infrastructure = is_air_taxi or any(w in corpus for w in [
        "nationwide network", "telecom network", "rail network", "power grid",
        "satellite constellation", "interstate pipeline", "national transit"
    ])

    is_drone_fleet = any(w in corpus for w in [
        "drone", "unmanned aerial", "uav", "autonomous drone", "drone delivery",
        "last-mile drone", "aerial delivery"
    ])
    is_robotics_hardware = is_drone_fleet or any(w in corpus for w in [
        "hardware", "robotics", "autonomous vehicle", "physical device", "iot sensor",
        "medical device", "sensor network", "manufacturing", "tooling", "factory",
        "automotive", "smart home hardware", "assembly line", "drone fleet"
    ])

    is_enterprise_saas = any(w in corpus for w in [
        "b2b", "saas", "enterprise", "logistics optimization", "supply chain saas",
        "fintech", "accounting", "forecasting", "cloud platform", "analytics", "b2b software"
    ])

    if is_heavy_infrastructure:
        return {
            "tier": "HEAVY_INFRASTRUCTURE",
            "name": "Heavy Aviation / Critical Infrastructure Network",
            "benchmark_capital": 10_000_000.0,
            "benchmark_timeline_months": 24.0,
            "regulatory_friction": "CRITICAL",
            "operational_complexity": "CRITICAL",
            "is_air_taxi": True,
            "is_drone": False
        }
    elif is_drone_fleet:
        return {
            "tier": "AUTONOMOUS_DRONE_FLEET",
            "name": "Autonomous Drone Fleet & Last-Mile Aviation",
            "benchmark_capital": 600_000.0,
            "benchmark_timeline_months": 14.0,
            "regulatory_friction": "HIGH",
            "operational_complexity": "HIGH",
            "is_air_taxi": False,
            "is_drone": True
        }
    elif is_robotics_hardware:
        return {
            "tier": "PHYSICAL_HARDWARE",
            "name": "Physical Hardware & Robotics Engineering",
            "benchmark_capital": 450_000.0,
            "benchmark_timeline_months": 12.0,
            "regulatory_friction": "MEDIUM",
            "operational_complexity": "HIGH",
            "is_air_taxi": False,
            "is_drone": False
        }
    elif is_enterprise_saas:
        return {
            "tier": "ENTERPRISE_SAAS",
            "name": "Enterprise B2B SaaS & Optimization Platform",
            "benchmark_capital": 350_000.0,
            "benchmark_timeline_months": 9.0,
            "regulatory_friction": "LOW",
            "operational_complexity": "MEDIUM",
            "is_air_taxi": False,
            "is_drone": False
        }
    else:
        return {
            "tier": "DIGITAL_PLATFORM",
            "name": "Digital Application / Web Platform",
            "benchmark_capital": 180_000.0,
            "benchmark_timeline_months": 6.0,
            "regulatory_friction": "LOW",
            "operational_complexity": "LOW",
            "is_air_taxi": False,
            "is_drone": False
        }


def calculate_launch_scores(
    venture_idea: str,
    target_market: str,
    budget: Any,
    timeline: str,
    strategic_question: str = "",
    business_model: str = "",
    specialist_reports: Optional[Dict[str, Any]] = None,
    grounding_facts: Optional[Dict[str, Any]] = None,
    risk_matrix: Optional[List[Dict[str, Any]]] = None,
    critical_blockers: Optional[List[Dict[str, Any]]] = None,
    validation_gates: Optional[List[Dict[str, Any]]] = None,
    rule_evaluations: Optional[List[Dict[str, Any]]] = None,
    evidence_quality: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Centralized canonical calculation engine for Track B Launch scoring.
    Returns scores and itemized explanations for all 4 KPIs + overall launch score.
    """
    reports = specialist_reports or {}
    facts = grounding_facts or {}
    blockers = critical_blockers or []
    matrix = risk_matrix or []
    rules = rule_evaluations or []
    ev_qual = evidence_quality or {}

    budget_usd = parse_budget_numeric(budget)
    timeline_months = parse_timeline_months(timeline)
    arch = classify_venture_archetype(venture_idea, strategic_question, business_model)

    cap_req = arch["benchmark_capital"]
    time_req = arch["benchmark_timeline_months"]

    # Pull specialist signals
    cap_rep = reports.get("CAPITAL_STRATEGIST", {})
    cap_rec = str(cap_rep.get("recommendation", "MAYBE")).upper()
    cap_conf = max(1, cap_rep.get("confidence", 70))
    cap_ver = cap_rep.get("data_verified", False)

    lo_rep = reports.get("LAUNCH_OPERATIONS", {})
    lo_rec = str(lo_rep.get("recommendation", "MAYBE")).upper()
    lo_conf = max(1, lo_rep.get("confidence", 70))
    lo_ver = lo_rep.get("data_verified", False)

    rn_rep = reports.get("REGULATORY_NAVIGATOR", {})
    rn_rec = str(rn_rep.get("recommendation", "MAYBE")).upper()
    rn_conf = max(1, rn_rep.get("confidence", 70))
    rn_ver = rn_rep.get("data_verified", False)

    mv_rep = reports.get("MARKET_VALIDATOR", {})
    mv_rec = str(mv_rep.get("recommendation", "MAYBE")).upper()
    mv_conf = max(1, mv_rep.get("confidence", 70))
    mv_ver = mv_rep.get("data_verified", False)

    cs_rep = reports.get("COMPETITIVE_SCOUT", {})
    cs_rec = str(cs_rep.get("recommendation", "MAYBE")).upper()
    cs_conf = max(1, cs_rep.get("confidence", 70))
    cs_ver = cs_rep.get("data_verified", False)

    vr_rep = reports.get("VENTURE_RISK", {})
    vr_rec = str(vr_rep.get("recommendation", "MAYBE")).upper()
    vr_conf = max(1, vr_rep.get("confidence", 70))
    vr_ver = vr_rep.get("data_verified", False)

    # -------------------------------------------------------------
    # 1. CAPITAL FEASIBILITY SCORE
    # -------------------------------------------------------------
    cap_ratio = budget_usd / max(1.0, cap_req)

    if cap_ratio >= 1.5:
        base_cap = 88.0 + min(8.0, (cap_ratio - 1.5) * 4.0)
    elif cap_ratio >= 1.0:
        base_cap = 76.0 + (cap_ratio - 1.0) * 24.0
    elif cap_ratio >= 0.6:
        base_cap = 52.0 + (cap_ratio - 0.6) * 60.0
    elif cap_ratio >= 0.3:
        base_cap = 28.0 + (cap_ratio - 0.3) * 80.0
    elif cap_ratio >= 0.1:
        base_cap = 12.0 + (cap_ratio - 0.1) * 80.0
    else:
        base_cap = max(2.0, cap_ratio * 100.0)

    # Specialist vote calibration
    if "CAPITAL_STRATEGIST" in reports:
        if cap_rec in ["YES", "LAUNCH"]:
            base_cap += 4.0
        elif cap_rec in ["MAYBE", "VALIDATE FIRST"]:
            base_cap -= 6.0
        elif cap_rec in ["NO", "DO NOT LAUNCH"]:
            base_cap -= 18.0

        if not cap_ver:
            base_cap -= 6.0

    # Check for Capital Rule failures
    cap_rule_failed = any(r.get("rule_id") == "RULE-001" and r.get("status") == "FAIL" for r in rules)
    if cap_rule_failed:
        base_cap = min(base_cap, 32.0)

    # Check for capital blockers
    has_cap_blocker = any("capital" in str(b.get("title", "")).lower() for b in blockers)
    if has_cap_blocker:
        base_cap -= 10.0

    capital_feasibility = int(max(2, min(98, round(base_cap))))

    # Human-readable Capital Explanation
    if capital_feasibility >= 80:
        cap_reason = f"Proposed budget (${budget_usd:,.0f}) comfortably exceeds the benchmark requirement (~${cap_req:,.0f}) for {arch['name']}, providing adequate runway and buffer."
    elif capital_feasibility >= 60:
        cap_reason = f"Proposed capital (${budget_usd:,.0f}) is calibrated near the benchmark requirement (~${cap_req:,.0f}), requiring disciplined milestone governance."
    elif capital_feasibility >= 30:
        cap_reason = f"Proposed ${budget_usd:,.0f} budget is materially below estimated capital requirements (~${cap_req:,.0f}) for {arch['name']}. Sizing shortfall creates runway depletion risk."
    else:
        cap_reason = f"Proposed ${budget_usd:,.0f} budget is catastrophically deficient against minimum requirements (~${cap_req:,.0f}) for {arch['name']}. Capital exhaustion would occur prior to commercial launch."

    # -------------------------------------------------------------
    # 2. LAUNCH READINESS SCORE (MARKET / OPERATIONAL READINESS)
    # -------------------------------------------------------------
    time_ratio = timeline_months / max(1.0, time_req)

    if time_ratio >= 1.5:
        base_readiness = 88.0 + min(8.0, (time_ratio - 1.5) * 5.0)
    elif time_ratio >= 1.0:
        base_readiness = 74.0 + (time_ratio - 1.0) * 28.0
    elif time_ratio >= 0.6:
        base_readiness = 48.0 + (time_ratio - 0.6) * 65.0
    elif time_ratio >= 0.3:
        base_readiness = 22.0 + (time_ratio - 0.3) * 86.0
    else:
        base_readiness = max(3.0, time_ratio * 60.0)

    # Regulatory specialist adjustment
    if "REGULATORY_NAVIGATOR" in reports:
        if rn_rec in ["YES", "LAUNCH"]:
            base_readiness += 4.0
        elif rn_rec in ["MAYBE", "VALIDATE FIRST"]:
            base_readiness -= 6.0
        elif rn_rec in ["NO", "DO NOT LAUNCH"]:
            base_readiness -= 16.0
        if not rn_ver:
            base_readiness -= 4.0

    # Operations specialist adjustment
    if "LAUNCH_OPERATIONS" in reports:
        if lo_rec in ["YES", "LAUNCH"]:
            base_readiness += 4.0
        elif lo_rec in ["MAYBE", "VALIDATE FIRST"]:
            base_readiness -= 6.0
        elif lo_rec in ["NO", "DO NOT LAUNCH"]:
            base_readiness -= 16.0
        if not lo_ver:
            base_readiness -= 4.0

    # Specific heavy friction penalties scaled proportionally
    if arch["regulatory_friction"] == "CRITICAL" and timeline_months < 24.0:
        base_readiness -= 20.0 * (1.0 - (timeline_months / 24.0))
    elif arch["regulatory_friction"] == "HIGH" and timeline_months < 14.0:
        base_readiness -= 12.0 * (1.0 - (timeline_months / 14.0))

    # Blockers / Rule checks
    ops_rule_failed = any(r.get("rule_id") in ["RULE-002", "RULE-003", "RULE-006"] and r.get("status") == "FAIL" for r in rules)
    if ops_rule_failed:
        base_readiness = min(base_readiness, 35.0)

    has_ops_blocker = any(any(k in str(b.get("title", "")).lower() for k in ["timeline", "regulatory", "logistics", "flight", "aviation"]) for b in blockers)
    if has_ops_blocker:
        base_readiness -= 8.0

    launch_readiness = int(max(3, min(96, round(base_readiness))))

    # Human-readable Readiness Explanation
    if launch_readiness >= 80:
        ready_reason = f"Execution timeline ({timeline_months:.0f} months) comfortably aligns with operational and statutory milestones for {arch['name']} in {target_market}."
    elif launch_readiness >= 60:
        ready_reason = f"Timeline ({timeline_months:.0f} months) is feasible for an agile MVP rollout, but requires tightly coordinated regulatory filing."
    elif launch_readiness >= 30:
        ready_reason = f"{timeline_months:.0f}-month timeline is aggressive given regulatory licensing, certification lead times, and operational infrastructure setup for {arch['name']}."
    else:
        ready_reason = f"{timeline_months:.0f}-month timeline is severely unviable for {arch['name']}. Mandatory statutory certifications and safety validation require 18-36+ months."

    # -------------------------------------------------------------
    # 3. OPPORTUNITY SCORE
    # -------------------------------------------------------------
    # Base from Market Validator & Competitive Scout if present
    if "MARKET_VALIDATOR" in reports or "COMPETITIVE_SCOUT" in reports:
        mv_score = 86.0 if mv_rec in ["YES", "LAUNCH"] else (55.0 if mv_rec in ["MAYBE", "VALIDATE FIRST"] else 25.0)
        cs_score = 84.0 if cs_rec in ["YES", "LAUNCH"] else (50.0 if cs_rec in ["MAYBE", "VALIDATE FIRST"] else 22.0)
        opp_weight = (mv_conf if "MARKET_VALIDATOR" in reports else 0) + (cs_conf if "COMPETITIVE_SCOUT" in reports else 0)
        base_opp = (((mv_score * mv_conf) if "MARKET_VALIDATOR" in reports else 0) + 
                    ((cs_score * cs_conf) if "COMPETITIVE_SCOUT" in reports else 0)) / max(1, opp_weight)
    else:
        base_opp = 72.0

    # Local ecosystem liquidity bonus/penalty
    res_data = facts.get("Research Data", {})
    if res_data and res_data.get("Total Funding (USD)") != "N/A":
        base_opp += 3.0
    elif not mv_ver:
        base_opp -= 8.0

    # Realizability constraint: An unbuildable venture cannot capture theoretical market size!
    if capital_feasibility < 20 or launch_readiness < 20:
        base_opp = min(base_opp, 38.0)
    elif capital_feasibility < 35 or launch_readiness < 35:
        base_opp = min(base_opp, 68.0)

    opportunity_score = int(max(10, min(96, round(base_opp))))

    # Human-readable Opportunity Explanation
    if opportunity_score >= 80:
        opp_reason = f"Favorable market demand, addressable TAM, and clear competitive differentiation voids identified for {target_market}."
    elif opportunity_score >= 60:
        opp_reason = f"Addressable demand exists in {target_market}, though customer adoption rates and incumbent competitive moats require focused differentiation."
    elif opportunity_score >= 35:
        opp_reason = f"Market appetite exists in principle, but commercial realization is constrained by acute capital and execution bottlenecks."
    else:
        opp_reason = f"Commercial opportunity realization is blocked due to fatal execution infeasibility or saturated competitive entrenchment."

    # -------------------------------------------------------------
    # 4. RISK MITIGATION SCORE
    # -------------------------------------------------------------
    base_risk = 88.0

    # Deductions from Risk Matrix
    for r in matrix:
        lvl = str(r.get("level", "")).upper()
        if lvl == "HIGH":
            base_risk -= 12.0
        elif lvl == "MEDIUM":
            base_risk -= 5.0
        elif lvl == "UNKNOWN":
            base_risk -= 7.0

    # Deductions from Critical Blockers
    for b in blockers:
        sev = str(b.get("severity", "")).upper()
        if sev == "CRITICAL":
            base_risk -= 14.0
        elif sev == "HIGH":
            base_risk -= 7.0

    # Sovereign fragility check
    risk_facts = facts.get("Risk Data", {})
    frag_str = risk_facts.get("Fragility Score", risk_facts.get("Total", "N/A"))
    try:
        if frag_str != "N/A" and float(frag_str) > 75.0:
            base_risk -= 10.0
    except Exception:
        pass

    # Specialist vote deduction
    if "VENTURE_RISK" in reports:
        if vr_rec in ["NO", "DO NOT LAUNCH"]:
            base_risk -= 12.0
        elif vr_rec in ["MAYBE", "VALIDATE FIRST"]:
            base_risk -= 4.0

    # Capital mismatch multiplier on risk
    if capital_feasibility < 20:
        base_risk -= 15.0
    elif capital_feasibility < 35:
        base_risk -= 8.0

    risk_mitigation_score = int(max(5, min(95, round(base_risk))))

    # Human-readable Risk Explanation
    if risk_mitigation_score >= 80:
        risk_reason = f"Identified sovereign, regulatory, and financial exposures are substantially insulated by established operational controls."
    elif risk_mitigation_score >= 60:
        risk_reason = f"Moderate residual risks identified across market validation and working capital; staged mitigation milestones required."
    elif risk_mitigation_score >= 35:
        risk_reason = f"Elevated residual exposure across regulatory airspace, supply chain volatility, and capital exhaustion risks."
    else:
        risk_reason = f"Critical unmitigated hazards: severe capital insolvency exposure, compliance hurdles, and single-point failure liabilities."

    # -------------------------------------------------------------
    # 5. OVERALL LAUNCH SCORE
    # -------------------------------------------------------------
    raw_overall = (
        0.25 * opportunity_score +
        0.25 * risk_mitigation_score +
        0.25 * launch_readiness +
        0.25 * capital_feasibility
    )

    # Fiduciary Gating: You cannot recommend an unexecutable venture
    if capital_feasibility < 20 or launch_readiness < 20:
        raw_overall = min(raw_overall, 25.0)
    elif capital_feasibility < 35 or launch_readiness < 35:
        raw_overall = min(raw_overall, 48.0)

    overall_launch_score = int(max(5, min(96, round(raw_overall))))

    explanations = {
        "opportunity_score": opp_reason,
        "risk_mitigation_score": risk_reason,
        "launch_readiness_score": ready_reason,
        "capital_feasibility_score": cap_reason,
        "market_readiness": ready_reason,
        "financial_feasibility": cap_reason,
        "overall_launch_score": f"Overall venture readiness composite: {overall_launch_score}% based on four balanced domain pillars."
    }

    payload = {
        "opportunity_score": opportunity_score,
        "risk_mitigation_score": risk_mitigation_score,
        "launch_readiness_score": launch_readiness,
        "capital_feasibility_score": capital_feasibility,
        "market_readiness": launch_readiness,           # Backward-compatible alias
        "financial_feasibility": capital_feasibility,   # Backward-compatible alias
        "overall_launch_score": overall_launch_score,
        "archetype": arch,
        "explanations": explanations
    }

    return TrackBConsensusMetrics(payload)


class TrackBConsensusMetrics(dict):
    """
    Standard 4-metric dictionary that supports len(m) == 4 and iterating over the 4 canonical integer metrics,
    while exposing additional scoring metadata (launch_readiness_score, capital_feasibility_score,
    overall_launch_score, explanations, archetype) via item/attribute lookup.
    """
    def __init__(self, scores: Dict[str, Any]):
        super().__init__({
            "opportunity_score": scores["opportunity_score"],
            "risk_mitigation_score": scores["risk_mitigation_score"],
            "market_readiness": scores["launch_readiness_score"],
            "financial_feasibility": scores["capital_feasibility_score"]
        })
        self._extra = {
            "launch_readiness_score": scores["launch_readiness_score"],
            "capital_feasibility_score": scores["capital_feasibility_score"],
            "overall_launch_score": scores["overall_launch_score"],
            "explanations": scores.get("explanations", {}),
            "archetype": scores.get("archetype", {})
        }
    
    def __getitem__(self, key: str) -> Any:
        if key in self._extra:
            return self._extra[key]
        return super().__getitem__(key)
        
    def get(self, key: str, default: Any = None) -> Any:
        if key in self._extra:
            return self._extra[key]
        return super().get(key, default)

