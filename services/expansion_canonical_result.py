"""
BoardRoomAI — Canonical Result Builder for Corporate Expansion (Track A)
Constructs the complete, single-source-of-truth BoardRoomResult for Track A.
"""

import time
from typing import Dict, Any, List, Optional
from config import parse_budget_numeric, format_budget_display

def get_expansion_evidence_quality(specialist_reports: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates empirical evidence quality across the required 7 Track A executive dimensions."""
    agent_ids = ["RESEARCHER", "COMPETITOR", "LEGAL", "OPERATIONS", "RISK", "CFO"]
    verified = sum(1 for aid in agent_ids if specialist_reports.get(aid, {}).get("data_verified", False))
    required_dimensions = 7 # 1: TAM/Demand, 2: Competition, 3: Regulatory, 4: Logistics, 5: Sovereign Risk, 6: Capital Runway, 7: Timeline
    verified_dimensions = verified # Matches verified dataset-backed domains
    coverage_percent = int(round((verified_dimensions / required_dimensions) * 100))
    
    if coverage_percent >= 66:
        data_status = "EMPIRICALLY GROUNDED"
        status_badge = "✓ EMPIRICALLY GROUNDED"
        status_color = "#00FF88"
    elif coverage_percent >= 33:
        data_status = "PARTIALLY VERIFIED"
        status_badge = "⚠ PARTIALLY VERIFIED"
        status_color = "#FFB800"
    elif verified_dimensions > 0:
        data_status = "MODEL-INFERRED / LIMITED DATA"
        status_badge = "⚠ MODEL-INFERRED / LIMITED DATA"
        status_color = "#FF9F43"
    else:
        data_status = "VALIDATION REQUIRED"
        status_badge = "⚠ VALIDATION REQUIRED"
        status_color = "#FFB800"
        
    return {
        "specialists_total": len(agent_ids),
        "required_dimensions": required_dimensions,
        "verified_dimensions": verified_dimensions,
        "verified": verified_dimensions,
        "unavailable": len(agent_ids) - verified,
        "errors": 0,
        "coverage_percent": coverage_percent,
        "is_complete": (verified_dimensions >= 5),
        "data_status": data_status,
        "status_badge": status_badge,
        "status_color": status_color,
        "status_label": f"{verified_dimensions}/{required_dimensions} DIMENSIONS VERIFIED ({coverage_percent}%)"
    }

def build_expansion_evidence_ledger(
    company: str,
    target_market: str,
    budget_usd: float,
    timeline: str,
    specialist_reports: Dict[str, Any],
    grounding_facts: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Constructs the canonical Traceable Evidence Ledger with EVID-001... IDs for Track A."""
    ledger = []
    evid_idx = 1
    
    # 1. Market Research Data
    res = specialist_reports.get("RESEARCHER", {})
    res_ver = res.get("data_verified", False)
    facts_res = grounding_facts.get("Research Data", {}) if grounding_facts else {}
    startups = facts_res.get("Startups Tracked", "N/A")
    tot_fund = facts_res.get("Total Funding (USD)", "N/A")
    
    if res_ver and startups != "N/A":
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Market Researcher",
            "domain": "Ecosystem Demand & Volume",
            "claim": f"Ecosystem dataset indicates {startups} active sector enterprises with ${tot_fund} in aggregate funding.",
            "source_dataset": "research_data.csv",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Startups Tracked, Total Funding (USD)",
            "raw_value": f"{startups}, {tot_fund}",
            "normalized_value": f"{startups} enterprises / ${tot_fund}",
            "unit": "Count / USD",
            "calculation": "Direct tabular lookup of regional enterprise density.",
            "interpretation": f"Provides macro context on market liquidity and consumer tech adoption for {company}.",
            "what_it_measures": "Ecosystem enterprise count and capital scale.",
            "what_it_supports": f"Supports demand depth and customer readiness in {target_market}.",
            "what_it_cannot_support": f"Does not guarantee exact revenue for {company}.",
            "evidence_relevance": "CONTEXTUAL",
            "verification_status": "DATASET-BACKED",
            "evidence_type": "FACT"
        })
    else:
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Market Researcher",
            "domain": "Market Opportunity",
            "claim": f"Market size and TAM estimate for {company} in {target_market} based on industry benchmarks.",
            "source_dataset": "Industry Benchmark Model",
            "source_row_identifier": f"Market == '{target_market}'",
            "source_column": "TAM Estimate",
            "raw_value": "Model Inference",
            "normalized_value": "Contextual Estimate",
            "unit": "USD Estimate",
            "calculation": "Bottom-up market sizing synthesis.",
            "interpretation": f"Estimates addressable market scale for {company}.",
            "what_it_measures": "Addressable opportunity size.",
            "what_it_supports": f"Validates expansion rationale for {company}.",
            "what_it_cannot_support": "Empirical transaction history.",
            "evidence_relevance": "INDIRECT",
            "verification_status": "MODEL INFERENCE",
            "evidence_type": "MODEL-INFERENCE"
        })
    evid_idx += 1

    # 2. Competitive Intelligence Data
    comp = specialist_reports.get("COMPETITOR", {})
    comp_ver = comp.get("data_verified", False)
    facts_comp = grounding_facts.get("Competition Data", {}) if grounding_facts else {}
    top_comp = facts_comp.get("Top Company", "N/A")
    top_mcap = facts_comp.get("Top Company Market Cap (USD)", "N/A")
    comps_cnt = facts_comp.get("Companies Tracked", "N/A")
    
    if comp_ver and top_comp != "N/A":
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Competitive Intelligence",
            "domain": "Corporate Landscape Benchmark",
            "claim": f"Regional public enterprise dataset tracks {comps_cnt} major corporate entities (sovereign market-cap leader: {top_comp} at {top_mcap}).",
            "source_dataset": "competition_data.csv",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Top Company, Top Company Market Cap (USD)",
            "raw_value": f"{top_comp}, {top_mcap}",
            "normalized_value": f"{top_comp} ({top_mcap})",
            "unit": "USD Valuation",
            "calculation": "Ranked market capitalization of top regional public corporations.",
            "interpretation": "Provides regional corporate capital scale context; distinct from domain-specific direct rivals.",
            "what_it_measures": "Sovereign enterprise capitalization.",
            "what_it_supports": "Evaluates macroeconomic corporate concentration.",
            "what_it_cannot_support": f"Does NOT claim {top_comp} is a direct competitor in niche markets unless active in that sector.",
            "evidence_relevance": "CONTEXTUAL",
            "verification_status": "DATASET-BACKED",
            "evidence_type": "FACT"
        })
    else:
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Competitive Intelligence",
            "domain": "Competitive Differentiation",
            "claim": f"Competitive positioning analysis for {company} against regional incumbents in {target_market}.",
            "source_dataset": "Domain Competitor Synthesis",
            "source_row_identifier": f"Sector == '{target_market}'",
            "source_column": "Competitive Analysis",
            "raw_value": "Qualitative Assessment",
            "normalized_value": "Defensible Niche",
            "unit": "Qualitative",
            "calculation": "Strategic positioning audit.",
            "interpretation": f"Evaluates {company}'s value proposition and entry wedge.",
            "what_it_measures": "Product differentiation & barriers to entry.",
            "what_it_supports": f"Defensible positioning for {company}.",
            "what_it_cannot_support": "Exact competitor revenue splits.",
            "evidence_relevance": "DIRECT",
            "verification_status": "MODEL INFERENCE",
            "evidence_type": "MODEL-INFERENCE"
        })
    evid_idx += 1

    # 3. Regulatory / Legal Data
    leg = specialist_reports.get("LEGAL", {})
    leg_ver = leg.get("data_verified", False)
    facts_leg = grounding_facts.get("Legal Data", {}) if grounding_facts else {}
    ease_score = facts_leg.get("Ease of Doing Business Score", "N/A")
    days_start = facts_leg.get("Days to Start Business", "N/A")
    enforce_score = facts_leg.get("Enforcing Contracts Score", "N/A")
    
    if leg_ver and ease_score != "N/A":
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "General Counsel",
            "domain": "Ease of Doing Business & Compliance",
            "claim": f"World Bank Ease of Doing Business score is {ease_score}/100 with contract enforcement at {enforce_score}/100 (~{days_start} days incorporation).",
            "source_dataset": "legal_data.csv",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Ease of Doing Business Score, Enforcing Contracts Score",
            "raw_value": f"{ease_score}, {enforce_score}, {days_start}",
            "normalized_value": f"{ease_score}/100 Ease, {days_start} days",
            "unit": "Index (0-100) / Days",
            "calculation": "Standardized World Bank regulatory indicator extract.",
            "interpretation": f"Establishes statutory predictability and incorporation timeline for {company}.",
            "what_it_measures": "Administrative and legal friction.",
            "what_it_supports": "Confirms legal feasibility of entity formation.",
            "what_it_cannot_support": "Specialized sector licenses (e.g. medical, financial).",
            "evidence_relevance": "DIRECT",
            "verification_status": "DATASET-BACKED",
            "evidence_type": "FACT"
        })
    else:
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "General Counsel",
            "domain": "Regulatory Compliance",
            "claim": f"Foreign entity registration and statutory filing roadmap for {company} in {target_market}.",
            "source_dataset": "Legal Compliance Guidelines",
            "source_row_identifier": f"Jurisdiction == '{target_market}'",
            "source_column": "Compliance Pathway",
            "raw_value": "Standard Entity Formation",
            "normalized_value": "Navigable Compliance",
            "unit": "Qualitative",
            "calculation": "Legal framework audit.",
            "interpretation": f"Compliance protocols required for {company}.",
            "what_it_measures": "Entity registration steps.",
            "what_it_supports": "Identifies mandatory foreign filing prerequisites.",
            "what_it_cannot_support": "Automated government permit approval.",
            "evidence_relevance": "DIRECT",
            "verification_status": "MODEL INFERENCE",
            "evidence_type": "MODEL-INFERENCE"
        })
    evid_idx += 1

    # 4. Logistics Operations Data
    ops = specialist_reports.get("OPERATIONS", {})
    ops_ver = ops.get("data_verified", False)
    facts_log = grounding_facts.get("Market Data", {}) if grounding_facts else {}
    lpi_val = facts_log.get("Logistics Performance Score (2023)", "N/A")
    
    if ops_ver and lpi_val != "N/A":
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Chief Operating Officer",
            "domain": "Logistics & Physical/Digital Infrastructure",
            "claim": f"World Bank Logistics Performance Index rates regional infrastructure at {lpi_val}/5.0 for freight and customs efficiency.",
            "source_dataset": "market_data.csv",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Logistics Performance Score (2023)",
            "raw_value": str(lpi_val),
            "normalized_value": f"{lpi_val}/5.0",
            "unit": "Index Score (1.0 - 5.0)",
            "calculation": "Direct extract of World Bank LPI 2023 infrastructure score.",
            "interpretation": f"Confirms transport and fulfillment channel readiness for {company}.",
            "what_it_measures": "Logistics and trade facilitation quality.",
            "what_it_supports": f"Operational execution across the {timeline} roadmap.",
            "what_it_cannot_support": "Private warehouse rental rates.",
            "evidence_relevance": "DIRECT",
            "verification_status": "DATASET-BACKED",
            "evidence_type": "FACT"
        })
    else:
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Chief Operating Officer",
            "domain": "Operational Logistics",
            "claim": f"Operational deployment model and distribution roadmap for {company} over {timeline}.",
            "source_dataset": "Operational Model Synthesis",
            "source_row_identifier": f"Territory == '{target_market}'",
            "source_column": "Operations Roadmap",
            "raw_value": "Staged 3PL Distribution",
            "normalized_value": "Feasible Operations",
            "unit": "Qualitative",
            "calculation": "Operational roadmap synthesis.",
            "interpretation": f"Logistics and staffing blueprint for {company}.",
            "what_it_measures": "Operational lead times.",
            "what_it_supports": "Confirms execution schedule.",
            "what_it_cannot_support": "Fixed vendor contracts.",
            "evidence_relevance": "DIRECT",
            "verification_status": "MODEL INFERENCE",
            "evidence_type": "MODEL-INFERENCE"
        })
    evid_idx += 1

    # 5. Risk Data
    risk = specialist_reports.get("RISK", {})
    risk_ver = risk.get("data_verified", False)
    facts_risk = grounding_facts.get("Risk Data", {}) if grounding_facts else {}
    frag_score = facts_risk.get("Fragility Score", facts_risk.get("Total", "N/A"))
    frag_rank = facts_risk.get("Rank", "N/A")
    
    if risk_ver and frag_score != "N/A":
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Chief Risk Officer",
            "domain": "Macroeconomic & Sovereign Stability",
            "claim": f"Fragile States Index rates territory at rank #{frag_rank} with composite fragility score {frag_score}/120.",
            "source_dataset": "risk_data.csv",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Fragility Score, Rank",
            "raw_value": f"{frag_score}, {frag_rank}",
            "normalized_value": f"{frag_score}/120 (Rank #{frag_rank})",
            "unit": "Score (0-120)",
            "calculation": "Direct extract of Fund for Peace FSI sovereign stability rating.",
            "interpretation": f"Demonstrates sovereign and institutional risk envelope for {company}'s capital deployment.",
            "what_it_measures": "Sovereign stability and political risk.",
            "what_it_supports": "Validates macro safety of capital commitment.",
            "what_it_cannot_support": "Micro-level competitive volatility.",
            "evidence_relevance": "DIRECT",
            "verification_status": "DATASET-BACKED",
            "evidence_type": "FACT"
        })
    else:
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Chief Risk Officer",
            "domain": "Macro Risk Assessment",
            "claim": f"Macroeconomic and currency risk evaluation for {company} in {target_market}.",
            "source_dataset": "Macro Risk Model",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Risk Profile",
            "raw_value": "Manageable Risk Envelope",
            "normalized_value": "Standard Macro Risk",
            "unit": "Qualitative",
            "calculation": "Sovereign risk synthesis.",
            "interpretation": f"Risk mitigation parameters for {company}.",
            "what_it_measures": "Macro exposure.",
            "what_it_supports": "Informs capital tranche pacing.",
            "what_it_cannot_support": "Unforeseen macro shocks.",
            "evidence_relevance": "DIRECT",
            "verification_status": "MODEL INFERENCE",
            "evidence_type": "MODEL-INFERENCE"
        })
    evid_idx += 1

    # 6. CFO Budget Calculation
    budget_display = format_budget_display(budget_usd)
    ledger.append({
        "evidence_id": f"EVID-{evid_idx:03d}",
        "specialist": "Chief Financial Officer",
        "domain": "Capital Allocation & Sizing",
        "claim": f"Proposed expansion capital of {budget_display} evaluated across {timeline} operational roadmap.",
        "source_dataset": "User Input (Proposed Budget) + Financial Modeling",
        "source_row_identifier": f"Company == '{company}'",
        "source_column": "Capital Allocation",
        "raw_value": str(budget_usd),
        "normalized_value": budget_display,
        "unit": "USD Capital",
        "calculation": f"Deterministic input ingestion: Budget = {budget_display}, Timeline = {timeline}",
        "calculation_formula": "expansion_capital = user_input_budget",
        "interpretation": f"Evaluates whether {budget_display} provides adequate runway and positive NPV for {company}.",
        "what_it_measures": "Capital sufficiency for expansion.",
        "what_it_supports": f"Authoritative financial modeling using exact user-proposed budget of {budget_display}.",
        "what_it_cannot_support": "Cannot substitute arbitrary external benchmarks without explicit labeling.",
        "evidence_relevance": "DIRECT",
        "verification_status": "DATASET-BACKED",
        "evidence_type": "CALCULATION"
    })
    
    return ledger

def build_expansion_risk_matrix(
    target_market: str,
    specialist_reports: Dict[str, Any],
    grounding_facts: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Constructs the 7 explicit risk categories (RISK-001..RISK-007) for Corporate Expansion."""
    risks = []
    
    # 1. MACRO RISK
    risk = specialist_reports.get("RISK", {})
    facts_risk = grounding_facts.get("Risk Data", {}) if grounding_facts else {}
    frag_score = facts_risk.get("Fragility Score", facts_risk.get("Total", "N/A"))
    
    if risk.get("data_verified", False) and frag_score != "N/A":
        try:
            f_num = float(frag_score)
            macro_lvl = "LOW" if f_num < 50 else ("MEDIUM" if f_num < 80 else "HIGH")
            macro_desc = f"Fragile States Index rates {target_market} at {f_num:.1f}/120."
        except Exception:
            macro_lvl = "LOW"
            macro_desc = f"Sovereign risk in {target_market} is stable."
    else:
        macro_lvl = "LOW" if risk.get("recommendation") == "YES" else "MEDIUM"
        macro_desc = f"Macroeconomic stability in {target_market} evaluated within standard boundaries."
        
    risks.append({
        "risk_id": "RISK-001",
        "category": "MACRO RISK",
        "level": macro_lvl,
        "specialist": "Chief Risk Officer",
        "evidence_ref": "EVID-005",
        "rationale": macro_desc,
        "mitigation": "Structure milestone-based capital tranches to insulate against currency fluctuation."
    })
    
    # 2. REGULATORY RISK
    leg = specialist_reports.get("LEGAL", {})
    reg_rec = str(leg.get("recommendation", "MAYBE")).upper()
    reg_lvl = "LOW" if reg_rec == "YES" else ("MEDIUM" if reg_rec == "MAYBE" else "HIGH")
    risks.append({
        "risk_id": "RISK-002",
        "category": "REGULATORY RISK",
        "level": reg_lvl,
        "specialist": "General Counsel",
        "evidence_ref": "EVID-003",
        "rationale": leg.get("primary_concern") or f"Foreign compliance and regulatory filings in {target_market}.",
        "mitigation": "Retain specialized local corporate counsel to execute commercial registrations and licensing."
    })
    
    # 3. MARKET DEMAND RISK
    res = specialist_reports.get("RESEARCHER", {})
    res_rec = str(res.get("recommendation", "MAYBE")).upper()
    mkt_lvl = "LOW" if res_rec == "YES" else ("MEDIUM" if res_rec == "MAYBE" else "HIGH")
    risks.append({
        "risk_id": "RISK-003",
        "category": "MARKET DEMAND RISK",
        "level": mkt_lvl,
        "specialist": "Market Researcher",
        "evidence_ref": "EVID-001",
        "rationale": res.get("primary_concern") or f"Customer adoption velocity in {target_market}.",
        "mitigation": "Execute localized pilot customer marketing to validate conversion rates."
    })
    
    # 4. COMPETITIVE RISK
    comp = specialist_reports.get("COMPETITOR", {})
    comp_rec = str(comp.get("recommendation", "MAYBE")).upper()
    comp_lvl = "LOW" if comp_rec == "YES" else ("MEDIUM" if comp_rec == "MAYBE" else "HIGH")
    risks.append({
        "risk_id": "RISK-004",
        "category": "COMPETITIVE RISK",
        "level": comp_lvl,
        "specialist": "Competitive Intelligence",
        "evidence_ref": "EVID-002",
        "rationale": comp.get("primary_concern") or f"Incumbent response in {target_market}.",
        "mitigation": "Emphasize unique differentiation and target underserved customer segments."
    })
    
    # 5. DATA ACCESS RISK
    qual = get_expansion_evidence_quality(specialist_reports)
    cov = qual.get("coverage_percent", 100)
    data_lvl = "LOW" if cov >= 80 else ("MEDIUM" if cov >= 50 else "HIGH")
    risks.append({
        "risk_id": "RISK-005",
        "category": "DATA ACCESS RISK",
        "level": data_lvl,
        "specialist": "Data Audit Service",
        "evidence_ref": "EVID-001",
        "rationale": f"Empirical dataset coverage is {cov}% ({qual.get('verified', 0)}/6 domains verified).",
        "mitigation": "Supplement repository datasets with primary field due diligence where needed."
    })
    
    # 6. CAPITAL RISK
    cfo = specialist_reports.get("CFO", {})
    cfo_rec = str(cfo.get("recommendation", "MAYBE")).upper()
    cap_lvl = "LOW" if cfo_rec == "YES" else ("MEDIUM" if cfo_rec == "MAYBE" else "HIGH")
    risks.append({
        "risk_id": "RISK-006",
        "category": "CAPITAL RISK",
        "level": cap_lvl,
        "specialist": "Chief Financial Officer",
        "evidence_ref": "EVID-006",
        "rationale": cfo.get("primary_concern") or "Capital deployment pacing and payback break-even timing.",
        "mitigation": "Establish strict monthly burn ceilings and milestone-gated capital drawdowns."
    })
    
    # 7. OPERATIONAL RISK
    ops = specialist_reports.get("OPERATIONS", {})
    ops_rec = str(ops.get("recommendation", "MAYBE")).upper()
    op_lvl = "LOW" if ops_rec == "YES" else ("MEDIUM" if ops_rec == "MAYBE" else "HIGH")
    risks.append({
        "risk_id": "RISK-007",
        "category": "OPERATIONAL RISK",
        "level": op_lvl,
        "specialist": "Chief Operating Officer",
        "evidence_ref": "EVID-004",
        "rationale": ops.get("primary_concern") or f"Supply chain and distribution execution in {target_market}.",
        "mitigation": "Partner with established regional 3PL and distribution partners to streamline rollout."
    })
    
    return risks

def build_expansion_critical_blockers(specialist_reports: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extracts genuine business blockers (BLOCKER-001...) and high priority conditions (COND-001...) from Track A specialist findings."""
    items = []
    crit_idx = 1
    cond_idx = 1
    
    agents = [
        ("RESEARCHER", "Market Researcher", "EVID-001"),
        ("COMPETITOR", "Competitive Intelligence", "EVID-002"),
        ("LEGAL", "General Counsel", "EVID-003"),
        ("OPERATIONS", "Chief Operating Officer", "EVID-004"),
        ("RISK", "Chief Risk Officer", "EVID-005"),
        ("CFO", "Chief Financial Officer", "EVID-006")
    ]
    
    for aid, name, evid_ref in agents:
        rep = specialist_reports.get(aid, {})
        rec = str(rep.get("recommendation", "")).upper()
        concern = str(rep.get("primary_concern", "") or "")
        analysis = str(rep.get("analysis", "") or "")
        
        if rec in ["NO", "REJECT"]:
            items.append({
                "blocker_id": f"BLOCKER-{crit_idx:03d}",
                "id": f"BLOCKER-{crit_idx:03d}",
                "title": f"{name}: Critical Feasibility Constraint",
                "description": concern if len(concern) > 10 else f"{name} identified insurmountable expansion risks under current parameters.",
                "source_specialist": name,
                "source": name,
                "evidence_reference": evid_ref,
                "severity": "CRITICAL",
                "status": "OPEN",
                "resolution_condition": rep.get("mind_change_threshold", "Resolve specialist constraint prior to capital deployment.")
            })
            crit_idx += 1
        elif (rec in ["MAYBE", "DELAY ENTRY"] or len(concern) > 15) and not any(k in concern.lower() for k in ["none", "n/a", "no blocker"]):
            desc = concern if len(concern) > 10 else (analysis[:120] if len(analysis) > 10 else f"{name} requires milestone validation.")
            items.append({
                "blocker_id": f"COND-{cond_idx:03d}",
                "id": f"COND-{cond_idx:03d}",
                "title": f"{name}: High-Priority Condition & Risk",
                "description": desc,
                "source_specialist": name,
                "source": name,
                "evidence_reference": evid_ref,
                "severity": "HIGH",
                "status": "OPEN",
                "resolution_condition": rep.get("mind_change_threshold", "Validate assumption and de-risk operational workflow.")
            })
            cond_idx += 1
            
    return items

def build_expansion_action_plan(
    company: str,
    target_market: str,
    timeline: str,
    blockers: List[Dict[str, Any]],
    decision: str
) -> List[str]:
    """Generates 4-phase executive expansion action plan."""
    if "DO NOT" in decision or "REJECT" in decision:
        return [
            f"1. Halt capital expenditure for expansion into {target_market} until fundamental constraints are resolved.",
            f"2. Re-evaluate capital sizing and product scope to bridge the identified budget/operational deficit.",
            f"3. Conduct primary discovery interviews to reassess customer demand and competitive defensibility.",
            f"4. Re-convene executive board with updated parameters and risk mitigations."
        ]
    elif "CONDITIONS" in decision or "DELAY" in decision:
        return [
            f"1. Phase 1 (Weeks 1-4): Retain local counsel in {target_market} to initiate compliance and entity filings.",
            f"2. Phase 2 (Months 2-3): Secure regional 3PL partnerships and execute controlled pilot customer rollout.",
            f"3. Phase 3 (Months 4-6): Review pilot unit economics, customer acquisition cost, and gross margins.",
            f"4. Phase 4 (Full Expansion): Unlock Phase-2 capital tranche upon satisfying milestone validation gates."
        ]
    else:
        return [
            f"1. Phase 1: Formalize entity registration, foreign commercial filings, and corporate banking in {target_market}.",
            f"2. Phase 2: Deploy initial go-to-market channels, marketing campaigns, and regional partner integrations.",
            f"3. Phase 3: Scale customer acquisition and monitor unit economics against projected break-even targets.",
            f"4. Phase 4: Achieve operational profitability within the targeted {timeline} roadmap."
        ]

def build_expansion_decision_trace(
    company: str,
    target_market: str,
    budget_usd: float,
    timeline: str,
    question: str,
    specialist_reports: Dict[str, Any],
    deterministic_eval: Dict[str, Any],
    ceo_report: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Constructs the traceable audit trail for Track A Corporate Expansion."""
    budget_display = format_budget_display(budget_usd)
    
    stages = [
        {
            "stage_id": "STAGE-1",
            "stage_name": "EXPANSION_INPUT_CAPTURE",
            "title": "Corporate Expansion Parameters",
            "description": f"Captured expansion parameters for {company} entering {target_market} with {budget_display} over {timeline}.",
            "status": "COMPLETED",
            "inputs": {
                "company": company,
                "target_market": target_market,
                "budget_usd": budget_usd,
                "budget_display": budget_display,
                "timeline": timeline,
                "question": question
            }
        },
        {
            "stage_id": "STAGE-2",
            "stage_name": "DATA_GROUNDING",
            "title": "Empirical Dataset Grounding",
            "description": f"Queried local empirical datasets (research, competition, legal, logistics, risk, financial) for {target_market}.",
            "status": "COMPLETED",
            "inputs": {"target_market": target_market}
        },
        {
            "stage_id": "STAGE-3",
            "stage_name": "SPECIALIST_VOTES",
            "title": "C-Suite Executive Deliberation",
            "description": "Collected structured assessments from Market Researcher, Competitive Intel, General Counsel, COO, CRO, and CFO.",
            "status": "COMPLETED",
            "specialist_votes": {aid: rep.get("recommendation", "MAYBE") for aid, rep in specialist_reports.items()}
        },
        {
            "stage_id": "STAGE-4",
            "stage_name": "DETERMINISTIC_EXPANSION_RULES",
            "title": "Deterministic Policy Engine Evaluation",
            "description": f"Evaluated 9 corporate expansion policy rules. Passed: {deterministic_eval.get('rules_passed_count', 0)}/9.",
            "status": "COMPLETED",
            "verdict": deterministic_eval.get("decision", "ENTER MARKET"),
            "rationale": deterministic_eval.get("policy_rationale", "")
        },
        {
            "stage_id": "STAGE-5",
            "stage_name": "CEO_SYNTHESIS",
            "title": "Corporate CEO Executive Synthesis",
            "description": "Synthesized executive board feedback into master strategic rationale.",
            "status": "COMPLETED",
            "ceo_verdict": ceo_report.get("recommendation", "ENTER MARKET"),
            "rationale": ceo_report.get("analysis", "")
        }
    ]
    return stages

def build_expansion_canonical_result(
    company: str,
    market: str,
    budget: Any,
    timeline: str,
    question: str,
    specialist_reports: Dict[str, Any],
    ceo_report: Dict[str, Any],
    deterministic_eval: Dict[str, Any],
    transcript: List[Dict[str, Any]],
    grounding_facts: Optional[Dict[str, Any]] = None,
    business_model: Optional[str] = ""
) -> Dict[str, Any]:
    """
    Builds the authoritative canonical result object for Track A Corporate Expansion.
    Guarantees that every metric and card draws from this single object.
    """
    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    # 1. Authoritative Decision & Confidence
    final_decision = deterministic_eval.get("decision", ceo_report.get("recommendation", "ENTER MARKET"))
    ceo_rec = ceo_report.get("recommendation", final_decision)
    
    # Vote counts
    votes = [rep.get("recommendation", "MAYBE") for rep in specialist_reports.values()]
    yes_c = votes.count("YES") + votes.count("ENTER") + votes.count("ENTER MARKET")
    no_c = votes.count("NO") + votes.count("REJECT") + votes.count("REJECT EXPANSION")
    maybe_c = len(votes) - yes_c - no_c
    
    # Evidence Quality
    evidence_quality = get_expansion_evidence_quality(specialist_reports)
    
    # Evidence Ledger & Risk Matrix
    evidence_ledger = build_expansion_evidence_ledger(company, market, budget_usd, timeline, specialist_reports, grounding_facts)
    risk_matrix = build_expansion_risk_matrix(market, specialist_reports, grounding_facts)
    critical_blockers = build_expansion_critical_blockers(specialist_reports)
    validation_roadmap = build_expansion_action_plan(company, market, timeline, critical_blockers, final_decision)
    decision_trace = build_expansion_decision_trace(company, market, budget_usd, timeline, question, specialist_reports, deterministic_eval, ceo_report)
    
    # Consensus Scores
    # Opportunity score
    res_conf = specialist_reports.get("RESEARCHER", {}).get("confidence", 80)
    comp_conf = specialist_reports.get("COMPETITOR", {}).get("confidence", 75)
    opp_score = int(round((res_conf * 0.55) + (comp_conf * 0.45)))
    if no_c >= 2:
        opp_score = max(20, opp_score - 30)
        
    # Risk Mitigation Score
    base_mit = 90
    crit_count = sum(1 for b in critical_blockers if b.get("severity") == "CRITICAL")
    high_count = sum(1 for b in critical_blockers if b.get("severity") == "HIGH")
    failed_rules_c = deterministic_eval.get("rules_failed_count", 0)
    risk_mit_score = max(15, min(95, base_mit - (crit_count * 20) - (high_count * 10) - (failed_rules_c * 8) - (no_c * 12)))
    
    # Market Readiness
    leg_conf = specialist_reports.get("LEGAL", {}).get("confidence", 80)
    ops_conf = specialist_reports.get("OPERATIONS", {}).get("confidence", 80)
    mkt_readiness = int(round((leg_conf * 0.5) + (ops_conf * 0.5)))
    if any(rep.get("recommendation") in ["NO", "REJECT"] for rep in [specialist_reports.get("LEGAL", {}), specialist_reports.get("OPERATIONS", {})]):
        mkt_readiness = max(25, mkt_readiness - 35)
        
    # Financial Feasibility
    cfo_conf = specialist_reports.get("CFO", {}).get("confidence", 85)
    cfo_rec = specialist_reports.get("CFO", {}).get("recommendation", "YES")
    fin_score = cfo_conf if cfo_rec in ["YES", "ENTER"] else (40 if cfo_rec in ["NO", "REJECT"] else 65)
    
    consensus_metrics = {
        "opportunity_score": opp_score,
        "risk_mitigation_score": risk_mit_score,
        "market_readiness": mkt_readiness,
        "financial_feasibility": fin_score
    }
    
    # Deterministic Confidence
    if "DO NOT" in final_decision or "REJECT" in final_decision:
        calc_conf = max(80, min(95, 75 + (no_c * 5) + (failed_rules_c * 4)))
    else:
        calc_conf = max(40, min(95, int(round((opp_score * 0.3) + (risk_mit_score * 0.3) + (mkt_readiness * 0.2) + (fin_score * 0.2)))))
        
    # Discrepancies check between CEO LLM and deterministic decision
    discrepancies = []
    if ("ENTER" in final_decision and "ENTER" not in ceo_rec) or ("DO NOT" in final_decision and "ENTER" in ceo_rec):
        discrepancies.append({
            "agent": "Corporate CEO",
            "claim": f"CEO recommended '{ceo_rec}', but deterministic policy engine authoritatively issued '{final_decision}'.",
            "resolution": "Authoritative deterministic expansion policy rules override advisory LLM verdict."
        })
        
    # Mind Change Thresholds
    mind_change_thresholds = []
    for aid, name in [
        ("RESEARCHER", "Market Researcher"),
        ("COMPETITOR", "Competitive Intelligence"),
        ("LEGAL", "General Counsel"),
        ("OPERATIONS", "Chief Operating Officer"),
        ("RISK", "Chief Risk Officer"),
        ("CFO", "Chief Financial Officer")
    ]:
        mct = specialist_reports.get(aid, {}).get("mind_change_threshold")
        if mct and mct != "N/A":
            mind_change_thresholds.append({
                "source": name,
                "threshold": mct,
                "classification": "DETERMINISTIC POLICY" if "burn" in mct.lower() or "budget" in mct.lower() else "VALIDATION GATE"
            })

    # Build Structured Decision Explanation Dictionary
    policy_rat = deterministic_eval.get("policy_rationale", ceo_report.get("analysis", ""))
    
    positives = []
    for r in deterministic_eval.get("rule_evaluations", []):
        if r.get("status") == "PASS":
            positives.append(f"{r.get('category', r.get('rule_id'))}: {r.get('reason', r.get('threshold', ''))}")
    if not positives:
        for ev in evidence_ledger:
            if ev.get("verification_status") == "DATASET-BACKED":
                positives.append(ev.get("claim", ""))
    if not positives:
        positives.append(f"Strategic executive consensus supports market entry for {company} into {market}.")

    negatives = []
    for r in deterministic_eval.get("rule_evaluations", []):
        if r.get("status") in ["FAIL", "CONDITIONAL"]:
            negatives.append(f"{r.get('category', r.get('rule_id'))}: {r.get('reason', '')}")
    for blk in critical_blockers:
        negatives.append(f"{blk.get('source')}: {blk.get('description')}")
    if not negatives:
        negatives.append(f"Requires localized compliance filings and operational distribution setup in {market}.")

    # Extract top risk including CRO finding
    if risk_matrix:
        high_risks = [r for r in risk_matrix if r.get("level") == "HIGH"]
        top_r = high_risks[0] if high_risks else risk_matrix[0]
        top_risk = f"{top_r.get('category', 'Risk')}: {top_r.get('rationale', '')} (Mitigation: {top_r.get('mitigation', 'Active monitoring')})"
    else:
        top_risk = f"Macroeconomic and operational execution risk in {market}."
    
    cap_text = f"Proposed budget of {budget_display} evaluated over {timeline} timeline."
    cfo_rep = specialist_reports.get("CFO", {})
    if cfo_rep.get("key_finding"):
        cap_text += f" CFO Audit: {cfo_rep.get('key_finding')}"

    ver_dims = evidence_quality.get("verified_dimensions", 0)
    req_dims = evidence_quality.get("required_dimensions", 7)
    cov_pct = evidence_quality.get("coverage_percent", 0)
    d_stat = evidence_quality.get("data_status", "VALIDATION REQUIRED")

    if ver_dims == 0:
        qual_text = f"Data Status: {d_stat} (0/{req_dims} empirical dimensions verified, {cov_pct}% coverage). Empirical datasets unavailable for this market — conclusion is model-inferred and requires validation."
    else:
        qual_text = f"Data Status: {d_stat} ({ver_dims}/{req_dims} empirical dimensions verified, {cov_pct}% coverage)."

    structured_decision_explanation = {
        "final_decision": final_decision,
        "confidence": calc_conf,
        "rationale": policy_rat,
        "key_reasons": positives[:3],
        "strongest_positive_evidence": positives[:3],
        "strongest_negative_evidence": negatives[:3],
        "most_important_risk": top_risk,
        "capital_consideration": cap_text,
        "data_quality_consideration": qual_text,
        "recommendation": f"Executive Recommendation: {final_decision}"
    }

    evidence_summary = {
        "required_dimensions": req_dims,
        "verified_dimensions": ver_dims,
        "coverage_percent": cov_pct,
        "evidence_records": len(evidence_ledger),
        "data_status": d_stat,
        "status_badge": evidence_quality.get("status_badge", "⚠ VALIDATION REQUIRED"),
        "status_color": evidence_quality.get("status_color", "#FFB800")
    }

    result = {
        # Core Canonical Identity
        "track": "expansion",
        "mode": "expansion",
        "company": company,
        "company_name": company,
        "market": market,
        "target_market": market,
        "target_country": market,
        "budget": budget_usd,
        "capital_budget": budget_usd,
        "budget_display": budget_display,
        "timeline": timeline,
        "question": question,
        "strategic_question": question,
        "strategic_board_question": question,
        "business_model": business_model,
        "target_customer": business_model,
        "timestamp": time.time(),
        
        # Verdict & Confidence
        "final_decision": final_decision,
        "final_recommendation": final_decision,
        "decision": final_decision,
        "confidence": calc_conf,
        "data_verified": cov_pct >= 50 and ver_dims >= 3,
        "data_status": d_stat,
        "status": "success",
        
        # Reports & Transcripts
        "specialist_reports": specialist_reports,
        "board_reports": specialist_reports,
        "transcript": transcript,
        
        # Decision Intelligence & Rules
        "deterministic_eval": deterministic_eval,
        "rule_evaluations": deterministic_eval.get("rule_evaluations", []),
        "decision_explanation": structured_decision_explanation,
        "evidence_quality": evidence_quality,
        "evidence_summary": evidence_summary,
        "evidence_ledger": evidence_ledger,
        "risk_matrix": risk_matrix,
        "critical_blockers": critical_blockers,
        "high_priority_conditions": [b for b in critical_blockers if b.get("severity") == "HIGH"],
        "validation_roadmap": validation_roadmap,
        "action_plan": validation_roadmap,
        "mind_change_thresholds": mind_change_thresholds,
        "decision_trace": decision_trace,
        "discrepancies": discrepancies,
        
        # Metrics & Consensus
        "consensus_metrics": consensus_metrics,
        "opportunity_score": opp_score,
        "risk_mitigation_score": risk_mit_score,
        "market_readiness": mkt_readiness,
        "financial_feasibility": fin_score,
        
        # Agreement Analysis
        "agreement_analysis": {
            "agreement_index": int(round((max(yes_c, no_c, maybe_c) / max(1, len(votes))) * 100)),
            "yes_count": yes_c,
            "no_count": no_c,
            "maybe_count": maybe_c,
            "total_votes": len(votes)
        },
        "disagreements": {
            "primary_split": f"{yes_c} YES vs {no_c} NO vs {maybe_c} MAYBE",
            "dissenting_agents": [aid for aid, rep in specialist_reports.items() if rep.get("recommendation") in ["NO", "REJECT"]]
        },
        
        # CEO Output
        "ceo_decision": final_decision,
        "ceo_confidence": calc_conf,
        "ceo_rationale": ceo_report.get("analysis", deterministic_eval.get("policy_rationale", ""))
    }
    
    return result
