"""
BoardRoomAI — Canonical Result, Provenance & Evidence Ledger Model
Single Source of Truth for Track B Venture Sessions and Track A Compatibility.
"""

import os
import time
import hashlib
from typing import Dict, Any, List, Optional
from decimal import Decimal
from services.dataset_provenance import (
    PROVENANCE_REGISTRY,
    get_dataset_provenance_record,
    verify_all_datasets_integrity,
    calculate_sha256
)
from services.semantic_suitability import evaluate_evidence_suitability
from services.claim_validator import ClaimValidator

APP_VERSION = "2.6.0-TRUST-AUDIT"
ENGINE_VERSION = "DETERMINISTIC-V3.5"

def compute_dataset_hash(filepath: str) -> str:
    """Computes a SHA-256 hash prefix for audit integrity."""
    if not os.path.exists(filepath):
        return "UNAVAILABLE"
    try:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()[:12]
    except Exception:
        return "UNKNOWN"

def get_evidence_quality(specialist_reports: Dict[str, Any]) -> Dict[str, Any]:
    """
    CANONICAL EVIDENCE QUALITY CALCULATION.
    Shared identically across Streamlit Dashboard, PDF Report, and Decision Engine.
    Separates empirical dataset grounding from agent infrastructure execution errors.
    """
    agent_ids = [
        "MARKET_VALIDATOR",
        "COMPETITIVE_SCOUT",
        "REGULATORY_NAVIGATOR",
        "LAUNCH_OPERATIONS",
        "VENTURE_RISK",
        "CAPITAL_STRATEGIST"
    ]
    
    total = len(agent_ids)
    verified = 0
    unavailable = 0
    errors = 0
    
    for aid in agent_ids:
        rep = specialist_reports.get(aid, {})
        status = rep.get("status", "")
        is_ver = rep.get("data_verified", False)
        analysis_str = str(rep.get("analysis", ""))
        
        if status == "error" or "[EXECUTION ERROR]" in analysis_str or "[API FAILURE]" in analysis_str:
            errors += 1
            if is_ver:
                verified += 1
            else:
                unavailable += 1
        elif is_ver:
            verified += 1
        else:
            unavailable += 1
            
    coverage_percent = int((verified / total) * 100) if total > 0 else 0
    
    return {
        "specialists_total": total,
        "verified": verified,
        "unavailable": unavailable,
        "errors": errors,
        "coverage_percent": coverage_percent,
        "is_complete": (verified == total and errors == 0),
        "status_label": f"{verified}/{total} DATASET-BACKED ({coverage_percent}%)"
    }

def build_evidence_ledger(target_market: str, capital_budget: Any, timeline: str, specialist_reports: Dict[str, Any], grounding_facts: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Constructs the Canonical Traceable Evidence Ledger with stable EVID-xxx IDs.
    Separates FACT (Dataset-backed), CALCULATION, MODEL-INFERENCE, ASSUMPTION, and VALIDATION GATE.
    Ensures local datasets are labeled DATASET-BACKED (not falsely claimed as independently provenance verified).
    Integrates semantic suitability mapping to prevent data misuse.
    """
    ledger = []
    evid_idx = 1
    
    # 1. Market Data (Research Data / Startups)
    mv_rep = specialist_reports.get("MARKET_VALIDATOR", {})
    mv_ver = mv_rep.get("data_verified", False)
    facts_res = grounding_facts.get("Research Data", {}) if grounding_facts else {}
    startups = facts_res.get("Startups Tracked", "N/A")
    tot_fund = facts_res.get("Total Funding (USD)", "N/A")
    avg_fund = facts_res.get("Average Funding per Startup (USD)", "N/A")
    
    prov_res = get_dataset_provenance_record("research_data.csv")
    suit_res = evaluate_evidence_suitability("research_data.csv", "Startup Ecosystem", "Active startup ecosystem tracks early-stage ventures")

    if mv_ver and startups != "N/A":
        # Raw & Normalized values
        raw_startups = str(startups)
        raw_tot_fund = str(tot_fund)
        
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Market Validator",
            "domain": "Startup Ecosystem",
            "claim": f"Active startup ecosystem tracks {startups} early-stage ventures with ${tot_fund} in cumulative venture capital.",
            "source_dataset": "research_data.csv",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Startups Tracked, Total Funding (USD)",
            "raw_value": f"{raw_startups}, {raw_tot_fund}",
            "normalized_value": f"{startups} startups / ${tot_fund}",
            "unit": "Count / USD",
            "calculation": "Direct tabular query of country startup count and total disclosed capital.",
            "calculation_formula": None,
            "calculation_inputs": {"Country": target_market, "Startups Tracked": raw_startups, "Total Funding": raw_tot_fund},
            "interpretation": suit_res["what_it_supports"],
            "what_it_measures": suit_res["what_it_measures"],
            "what_it_supports": suit_res["what_it_supports"],
            "what_it_cannot_support": suit_res["what_it_cannot_support"],
            "evidence_relevance": suit_res["evidence_relevance"],
            "source_date": prov_res.get("publication_date", "2024-01-15"),
            "dataset_version": prov_res.get("dataset_hash", "UNKNOWN"),
            "provenance_status": prov_res.get("provenance_status", "DATASET-BACKED"),
            "source_tier": prov_res.get("source_tier", "TIER 3"),
            "freshness_category": prov_res.get("freshness_category", "RECENT"),
            "confidence": 90,
            "supporting_rule_ids": ["RULE-001"],
            "supporting_agent": "Market Validator",
            "assumptions": "Assumes disclosed venture rounds represent national startup investment scale.",
            "limitations": suit_res["what_it_cannot_support"],
            "verification_status": "DATASET-BACKED",
            "evidence_type": "FACT"
        })
        evid_idx += 1
    else:
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Market Validator",
            "domain": "Startup Ecosystem",
            "claim": f"Ecosystem venture data for {target_market} is not present in local research datasets.",
            "source_dataset": "research_data.csv",
            "source_row_identifier": "N/A (Missing Record)",
            "source_column": "N/A",
            "raw_value": "NULL",
            "normalized_value": "UNAVAILABLE",
            "unit": "N/A",
            "calculation": "Lookup returned zero matching rows.",
            "calculation_formula": None,
            "calculation_inputs": {"Country": target_market},
            "interpretation": "Country data unavailable; requires primary research.",
            "what_it_measures": "Unverified",
            "what_it_supports": "None",
            "what_it_cannot_support": "Any market validation assertion.",
            "evidence_relevance": "NOT-SUITABLE",
            "source_date": "UNKNOWN",
            "dataset_version": "N/A",
            "provenance_status": "DATA-GAP",
            "source_tier": "TIER 4",
            "freshness_category": "UNKNOWN",
            "confidence": 0,
            "supporting_rule_ids": ["RULE-001", "RULE-008"],
            "supporting_agent": "Market Validator",
            "assumptions": "Unverified market.",
            "limitations": "Missing empirical record.",
            "verification_status": "UNAVAILABLE",
            "evidence_type": "MISSING"
        })
        evid_idx += 1

    # 2. Competitive Data
    cs_rep = specialist_reports.get("COMPETITIVE_SCOUT", {})
    cs_ver = cs_rep.get("data_verified", False)
    facts_comp = grounding_facts.get("Competition Data", {}) if grounding_facts else {}
    top_comp = facts_comp.get("Top Company", "N/A")
    top_mcap = facts_comp.get("Top Company Market Cap (USD)", "N/A")
    comps_cnt = facts_comp.get("Companies Tracked", "N/A")
    
    prov_comp = get_dataset_provenance_record("competition_data.csv")
    suit_comp = evaluate_evidence_suitability("competition_data.csv", "Incumbent Concentration", "Market incumbent concentration tracks public entities")

    if cs_ver and top_comp != "N/A":
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Competitive Scout",
            "domain": "Incumbent Concentration",
            "claim": f"Market incumbent concentration tracks {comps_cnt} public entities, led by {top_comp} ({top_mcap}).",
            "source_dataset": "competition_data.csv",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Top Company, Top Company Market Cap (USD)",
            "raw_value": f"{top_comp}, {top_mcap}",
            "normalized_value": f"{top_comp} ({top_mcap})",
            "unit": "USD Valuation",
            "calculation": "Ranked sorting of market capitalization among public domestic enterprises.",
            "calculation_formula": None,
            "calculation_inputs": {"Country": target_market, "Top Company": top_comp, "Market Cap": top_mcap},
            "interpretation": suit_comp["what_it_supports"],
            "what_it_measures": suit_comp["what_it_measures"],
            "what_it_supports": suit_comp["what_it_supports"],
            "what_it_cannot_support": suit_comp["what_it_cannot_support"],
            "evidence_relevance": suit_comp["evidence_relevance"],
            "source_date": prov_comp.get("publication_date", "2024-01-10"),
            "dataset_version": prov_comp.get("dataset_hash", "UNKNOWN"),
            "provenance_status": prov_comp.get("provenance_status", "DATASET-BACKED"),
            "source_tier": prov_comp.get("source_tier", "TIER 3"),
            "freshness_category": prov_comp.get("freshness_category", "RECENT"),
            "confidence": 85,
            "supporting_rule_ids": ["RULE-002"],
            "supporting_agent": "Competitive Scout",
            "assumptions": "Public equity market scale provides context for corporate incumbent capital concentration.",
            "limitations": suit_comp["what_it_cannot_support"],
            "verification_status": "DATASET-BACKED",
            "evidence_type": "FACT"
        })
        evid_idx += 1
    else:
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Competitive Scout",
            "domain": "Incumbent Concentration",
            "claim": f"Competitor registry data for {target_market} is unavailable on disk.",
            "source_dataset": "competition_data.csv",
            "source_row_identifier": "N/A",
            "source_column": "N/A",
            "raw_value": "NULL",
            "normalized_value": "UNAVAILABLE",
            "unit": "N/A",
            "calculation": "Lookup returned zero matching rows.",
            "calculation_formula": None,
            "calculation_inputs": {"Country": target_market},
            "interpretation": "Competitor landscape unverified.",
            "what_it_measures": "Unverified",
            "what_it_supports": "None",
            "what_it_cannot_support": "Any competitive positioning claim.",
            "evidence_relevance": "NOT-SUITABLE",
            "source_date": "UNKNOWN",
            "dataset_version": "N/A",
            "provenance_status": "DATA-GAP",
            "source_tier": "TIER 4",
            "freshness_category": "UNKNOWN",
            "confidence": 0,
            "supporting_rule_ids": ["RULE-002", "RULE-008"],
            "supporting_agent": "Competitive Scout",
            "assumptions": "Unverified competition.",
            "limitations": "Missing empirical record.",
            "verification_status": "UNAVAILABLE",
            "evidence_type": "MISSING"
        })
        evid_idx += 1

    # 3. Regulatory Data
    rn_rep = specialist_reports.get("REGULATORY_NAVIGATOR", {})
    rn_ver = rn_rep.get("data_verified", False)
    facts_leg = grounding_facts.get("Legal Data", {}) if grounding_facts else {}
    ease_score = facts_leg.get("Ease of Doing Business Score", "N/A")
    start_score = facts_leg.get("Starting a Business Score", "N/A")
    days_start = facts_leg.get("Days to Start Business", "N/A")
    
    prov_leg = get_dataset_provenance_record("legal_data.csv")
    suit_leg = evaluate_evidence_suitability("legal_data.csv", "Ease of Business & Incorporation", "Commercial incorporation score and registration timeline")

    if rn_ver and start_score != "N/A":
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Regulatory Navigator",
            "domain": "Ease of Business & Incorporation",
            "claim": f"Commercial incorporation score is {start_score}/100 with an average registration timeline of {days_start} days (Overall Ease of Doing Business: {ease_score}/100).",
            "source_dataset": "legal_data.csv",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Starting a Business Score, Days to Start Business",
            "raw_value": f"{start_score}, {days_start}, {ease_score}",
            "normalized_value": f"{start_score}/100, {days_start} days",
            "unit": "Index (0-100) / Days",
            "calculation": "Direct extract of standardized World Bank incorporation indicator score and days to incorporate.",
            "calculation_formula": None,
            "calculation_inputs": {"Country": target_market, "Starting a Business Score": start_score, "Days": days_start},
            "interpretation": suit_leg["what_it_supports"],
            "what_it_measures": suit_leg["what_it_measures"],
            "what_it_supports": suit_leg["what_it_supports"],
            "what_it_cannot_support": suit_leg["what_it_cannot_support"],
            "evidence_relevance": suit_leg["evidence_relevance"],
            "source_date": prov_leg.get("publication_date", "2020-05-01"),
            "dataset_version": prov_leg.get("dataset_hash", "UNKNOWN"),
            "provenance_status": prov_leg.get("provenance_status", "DATASET-BACKED (WORLD BANK HISTORICAL)"),
            "source_tier": prov_leg.get("source_tier", "TIER 1"),
            "freshness_category": prov_leg.get("freshness_category", "AGING"),
            "confidence": 95,
            "supporting_rule_ids": ["RULE-003"],
            "supporting_agent": "Regulatory Navigator",
            "assumptions": "Standard corporate entity formation reflects general administrative overhead.",
            "limitations": suit_leg["what_it_cannot_support"],
            "verification_status": "DATASET-BACKED",
            "evidence_type": "FACT"
        })
        evid_idx += 1
    else:
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Regulatory Navigator",
            "domain": "Ease of Business & Incorporation",
            "claim": f"Commercial incorporation rankings unverified for {target_market}.",
            "source_dataset": "legal_data.csv",
            "source_row_identifier": "N/A",
            "source_column": "N/A",
            "raw_value": "NULL",
            "normalized_value": "UNAVAILABLE",
            "unit": "N/A",
            "calculation": "Lookup returned zero matching rows.",
            "calculation_formula": None,
            "calculation_inputs": {"Country": target_market},
            "interpretation": "Regulatory benchmarks unverified.",
            "what_it_measures": "Unverified",
            "what_it_supports": "None",
            "what_it_cannot_support": "Any regulatory clearance claim.",
            "evidence_relevance": "NOT-SUITABLE",
            "source_date": "UNKNOWN",
            "dataset_version": "N/A",
            "provenance_status": "DATA-GAP",
            "source_tier": "TIER 4",
            "freshness_category": "UNKNOWN",
            "confidence": 0,
            "supporting_rule_ids": ["RULE-003", "RULE-008"],
            "supporting_agent": "Regulatory Navigator",
            "assumptions": "Unverified legal environment.",
            "limitations": "Missing empirical record.",
            "verification_status": "UNAVAILABLE",
            "evidence_type": "MISSING"
        })
        evid_idx += 1

    # 4. Logistics Operations Data
    lo_rep = specialist_reports.get("LAUNCH_OPERATIONS", {})
    lo_ver = lo_rep.get("data_verified", False)
    facts_log = grounding_facts.get("Market Data", {}) if grounding_facts else {}
    lpi_val = facts_log.get("Logistics Performance Score (2023)", facts_log.get("Logistics Performance Score", "N/A"))
    
    prov_mkt = get_dataset_provenance_record("market_data.csv")
    suit_mkt = evaluate_evidence_suitability("market_data.csv", "Logistics & Physical/Digital Rails", "Logistics Performance Score")

    if lo_ver and lpi_val != "N/A":
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Launch Operations",
            "domain": "Logistics & Physical/Digital Rails",
            "claim": f"World Bank Logistics Performance Index evaluates {target_market} at {lpi_val}/5.0 for trade and transport efficiency.",
            "source_dataset": "market_data.csv",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Logistics Performance Score (2023)",
            "raw_value": str(lpi_val),
            "normalized_value": f"{lpi_val}/5.0",
            "unit": "Index Score (1.0 - 5.0)",
            "calculation": "Direct lookup of sovereign LPI 2023 transport and freight infrastructure score.",
            "calculation_formula": None,
            "calculation_inputs": {"Country": target_market, "LPI Score": lpi_val},
            "interpretation": suit_mkt["what_it_supports"],
            "what_it_measures": suit_mkt["what_it_measures"],
            "what_it_supports": suit_mkt["what_it_supports"],
            "what_it_cannot_support": suit_mkt["what_it_cannot_support"],
            "evidence_relevance": suit_mkt["evidence_relevance"],
            "source_date": prov_mkt.get("publication_date", "2023-04-21"),
            "dataset_version": prov_mkt.get("dataset_hash", "UNKNOWN"),
            "provenance_status": prov_mkt.get("provenance_status", "DATASET-BACKED (WORLD BANK LPI 2023)"),
            "source_tier": prov_mkt.get("source_tier", "TIER 1"),
            "freshness_category": prov_mkt.get("freshness_category", "CURRENT"),
            "confidence": 95,
            "supporting_rule_ids": ["RULE-004"],
            "supporting_agent": "Launch Operations",
            "assumptions": "High logistics performance score indicates reliable digital and freight connectivity.",
            "limitations": suit_mkt["what_it_cannot_support"],
            "verification_status": "DATASET-BACKED",
            "evidence_type": "FACT"
        })
        evid_idx += 1
    else:
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Launch Operations",
            "domain": "Logistics & Infrastructure",
            "claim": f"Logistics Performance Score is unverified for {target_market}.",
            "source_dataset": "market_data.csv",
            "source_row_identifier": "N/A",
            "source_column": "N/A",
            "raw_value": "NULL",
            "normalized_value": "UNAVAILABLE",
            "unit": "N/A",
            "calculation": "Lookup returned zero matching rows.",
            "calculation_formula": None,
            "calculation_inputs": {"Country": target_market},
            "interpretation": "Logistics infrastructure unverified.",
            "what_it_measures": "Unverified",
            "what_it_supports": "None",
            "what_it_cannot_support": "Any operational feasibility assertion.",
            "evidence_relevance": "NOT-SUITABLE",
            "source_date": "UNKNOWN",
            "dataset_version": "N/A",
            "provenance_status": "DATA-GAP",
            "source_tier": "TIER 4",
            "freshness_category": "UNKNOWN",
            "confidence": 0,
            "supporting_rule_ids": ["RULE-004", "RULE-008"],
            "supporting_agent": "Launch Operations",
            "assumptions": "Unverified logistics infrastructure.",
            "limitations": "Missing empirical record.",
            "verification_status": "UNAVAILABLE",
            "evidence_type": "MISSING"
        })
        evid_idx += 1

    # 5. Venture / Macro Risk Data
    vr_rep = specialist_reports.get("VENTURE_RISK", {})
    vr_ver = vr_rep.get("data_verified", False)
    facts_risk = grounding_facts.get("Risk Data", {}) if grounding_facts else {}
    frag_score = facts_risk.get("Fragility Score", facts_risk.get("Total", "N/A"))
    frag_rank = facts_risk.get("Rank", "N/A")
    econ_press = facts_risk.get("E1: Economy", "N/A")
    
    prov_risk = get_dataset_provenance_record("risk_data.csv")
    suit_risk = evaluate_evidence_suitability("risk_data.csv", "Macroeconomic & Sovereign Stability", "Fragile States Index")

    if vr_ver and frag_score != "N/A":
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Venture Risk",
            "domain": "Macroeconomic & Sovereign Stability",
            "claim": f"Fragile States Index rates {target_market} at rank #{frag_rank} with fragility score {frag_score}/120 (Economic pressure: {econ_press}/10).",
            "source_dataset": "risk_data.csv",
            "source_row_identifier": f"Country == '{target_market}'",
            "source_column": "Fragility Score, Rank, E1: Economy",
            "raw_value": f"{frag_score}, {frag_rank}, {econ_press}",
            "normalized_value": f"{frag_score}/120 (Rank #{frag_rank})",
            "unit": "Fragility Score (0-120)",
            "calculation": "Direct extract of Fund for Peace FSI 2023 composite fragility score and rank.",
            "calculation_formula": None,
            "calculation_inputs": {"Country": target_market, "Score": frag_score, "Rank": frag_rank},
            "interpretation": suit_risk["what_it_supports"],
            "what_it_measures": suit_risk["what_it_measures"],
            "what_it_supports": suit_risk["what_it_supports"],
            "what_it_cannot_support": suit_risk["what_it_cannot_support"],
            "evidence_relevance": suit_risk["evidence_relevance"],
            "source_date": prov_risk.get("publication_date", "2023-06-15"),
            "dataset_version": prov_risk.get("dataset_hash", "UNKNOWN"),
            "provenance_status": prov_risk.get("provenance_status", "DATASET-BACKED (FUND FOR PEACE FSI 2023)"),
            "source_tier": prov_risk.get("source_tier", "TIER 2"),
            "freshness_category": prov_risk.get("freshness_category", "RECENT"),
            "confidence": 95,
            "supporting_rule_ids": ["RULE-005"],
            "supporting_agent": "Venture Risk",
            "assumptions": "Composite sovereign fragility index reflects macroeconomic stability risk.",
            "limitations": suit_risk["what_it_cannot_support"],
            "verification_status": "DATASET-BACKED",
            "evidence_type": "FACT"
        })
        evid_idx += 1
    else:
        ledger.append({
            "evidence_id": f"EVID-{evid_idx:03d}",
            "specialist": "Venture Risk",
            "domain": "Macroeconomic & Sovereign Stability",
            "claim": f"Sovereign fragility index unverified for {target_market}.",
            "source_dataset": "risk_data.csv",
            "source_row_identifier": "N/A",
            "source_column": "N/A",
            "raw_value": "NULL",
            "normalized_value": "UNAVAILABLE",
            "unit": "N/A",
            "calculation": "Lookup returned zero matching rows.",
            "calculation_formula": None,
            "calculation_inputs": {"Country": target_market},
            "interpretation": "Sovereign stability unverified.",
            "what_it_measures": "Unverified",
            "what_it_supports": "None",
            "what_it_cannot_support": "Any sovereign risk assertion.",
            "evidence_relevance": "NOT-SUITABLE",
            "source_date": "UNKNOWN",
            "dataset_version": "N/A",
            "provenance_status": "DATA-GAP",
            "source_tier": "TIER 4",
            "freshness_category": "UNKNOWN",
            "confidence": 0,
            "supporting_rule_ids": ["RULE-005", "RULE-008"],
            "supporting_agent": "Venture Risk",
            "assumptions": "Unverified macro risk.",
            "limitations": "Missing empirical record.",
            "verification_status": "UNAVAILABLE",
            "evidence_type": "MISSING"
        })
        evid_idx += 1

    # 6. Capital Feasibility & Mathematical Calculations
    cap_rep = specialist_reports.get("CAPITAL_STRATEGIST", {})
    cap_ver = cap_rep.get("data_verified", False)
    
    try:
        b_val = float(capital_budget) if capital_budget is not None else 0.0
    except Exception:
        b_val = 0.0

    if cap_ver and avg_fund != "N/A":
        try:
            clean_avg_str = str(avg_fund).replace("$", "").replace(",", "").replace("Million", "").replace("M", "").strip()
            # Handle Million conversion
            avg_num = float(clean_avg_str) * 1000000.0 if "Million" in str(avg_fund) or "M" in str(avg_fund) else float(clean_avg_str)
            ratio_pct = (b_val / avg_num) * 100.0 if avg_num > 0 else 0.0
            calc_text = f"Launch budget of ${b_val:,.0f} represents {ratio_pct:.2f}% of average startup venture round (${avg_num:,.0f} USD)."
            
            ledger.append({
                "evidence_id": f"EVID-{evid_idx:03d}",
                "specialist": "Capital Strategist",
                "domain": "Capital Benchmark Ratio",
                "claim": calc_text,
                "source_dataset": "research_data.csv (Average Funding) + User Input",
                "source_row_identifier": f"Country == '{target_market}'",
                "source_column": "Average Funding per Startup (USD)",
                "raw_value": f"Budget: {b_val}, Benchmark: {avg_num}",
                "normalized_value": f"{ratio_pct:.2f}% of ecosystem average",
                "unit": "Percentage Ratio",
                "calculation": f"Deterministic mathematical ratio: ({b_val:,.0f} / {avg_num:,.0f}) * 100 = {ratio_pct:.2f}%",
                "calculation_formula": "budget_ratio = (proposed_budget / ecosystem_average_funding) * 100",
                "calculation_inputs": {"proposed_budget": b_val, "ecosystem_average_funding": avg_num},
                "interpretation": "Contextual benchmark indicating proposed capital relative to observed startup rounds in this market.",
                "what_it_measures": "Capital sizing ratio relative to national startup funding rounds.",
                "what_it_supports": "Evaluates whether the venture is operating with a lean or capital-intensive budget relative to local rounds.",
                "what_it_cannot_support": "Does NOT prove the venture cannot succeed with a leaner capital allocation.",
                "evidence_relevance": "INDIRECT",
                "source_date": "Current Execution",
                "dataset_version": prov_res.get("dataset_hash", "UNKNOWN"),
                "provenance_status": "DETERMINISTIC-CALCULATION",
                "source_tier": "TIER 3",
                "freshness_category": "CURRENT",
                "confidence": 95,
                "supporting_rule_ids": ["RULE-006"],
                "supporting_agent": "Capital Strategist",
                "assumptions": "Venture can operate in a lean capital mode if unit economics allow.",
                "limitations": "Macro average includes late-stage rounds which skew the benchmark upward.",
                "verification_status": "DATASET-BACKED",
                "evidence_type": "CALCULATION"
            })
            evid_idx += 1
        except Exception:
            pass

    # 7. Model Inferences & Assumptions from Specialist Agents
    for aid, name in [
        ("MARKET_VALIDATOR", "Market Validator"),
        ("COMPETITIVE_SCOUT", "Competitive Scout"),
        ("REGULATORY_NAVIGATOR", "Regulatory Navigator"),
        ("LAUNCH_OPERATIONS", "Launch Operations"),
        ("VENTURE_RISK", "Venture Risk"),
        ("CAPITAL_STRATEGIST", "Capital Strategist")
    ]:
        rep = specialist_reports.get(aid, {})
        concern = rep.get("primary_concern")
        if concern and len(concern) > 10 and concern != "N/A":
            ledger.append({
                "evidence_id": f"EVID-{evid_idx:03d}",
                "specialist": name,
                "domain": "Venture Friction / Risk Factor",
                "claim": concern,
                "source_dataset": "Specialist Domain Reasoning",
                "source_row_identifier": "LLM Specialist Node Output",
                "source_column": "primary_concern",
                "raw_value": concern,
                "normalized_value": "Model Inference",
                "unit": "Qualitative Assessment",
                "calculation": "Synthesized domain inference based on venture parameters and market characteristics.",
                "calculation_formula": None,
                "calculation_inputs": {"Agent": name, "Field": "primary_concern"},
                "interpretation": f"Qualitative risk advisory identified by {name}.",
                "what_it_measures": "Specialist qualitative domain friction.",
                "what_it_supports": "Highlights potential operational, competitive, or capital friction to mitigate.",
                "what_it_cannot_support": "Empirical historical proof of failure.",
                "evidence_relevance": "INDIRECT",
                "source_date": "Current Execution",
                "dataset_version": "N/A",
                "provenance_status": "MODEL-INFERENCE",
                "source_tier": "TIER 4",
                "freshness_category": "CURRENT",
                "confidence": 75,
                "supporting_rule_ids": ["RULE-007"],
                "supporting_agent": name,
                "assumptions": "Subject to empirical validation through targeted customer discovery.",
                "limitations": "Qualitative hypothesis requiring primary validation.",
                "verification_status": "MODEL INFERENCE",
                "evidence_type": "MODEL-INFERENCE"
            })
            evid_idx += 1

    return ledger

def build_risk_matrix(target_market: str, specialist_reports: Dict[str, Any], grounding_facts: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Constructs the 7 explicit risk categories with RISK-001... IDs, explicit Low/Medium/High/Unknown ratings,
    and dataset-backed justification.
    """
    risks = []
    
    # 1. MACRO RISK
    vr = specialist_reports.get("VENTURE_RISK", {})
    facts_risk = grounding_facts.get("Risk Data", {}) if grounding_facts else {}
    frag_score = facts_risk.get("Fragility Score", facts_risk.get("Total", "N/A"))
    
    if not vr.get("data_verified", False) or frag_score == "N/A":
        macro_level = "UNKNOWN"
        macro_rationale = f"Sovereign fragility dataset missing for {target_market}; macro stability cannot be empirically verified."
    else:
        try:
            f_num = float(frag_score)
            macro_level = "LOW" if f_num < 45.0 else ("MEDIUM" if f_num < 75.0 else "HIGH")
            macro_rationale = f"Fragile States Index rates {target_market} at {f_num:.1f}/120."
        except Exception:
            macro_level = "UNKNOWN"
            macro_rationale = f"Invalid fragility format for {target_market}."
            
    risks.append({
        "risk_id": "RISK-001",
        "category": "MACRO RISK",
        "level": macro_level,
        "specialist": "Venture Risk",
        "evidence_ref": "EVID-005",
        "rationale": macro_rationale,
        "mitigation": "Hold capital reserves in stable international currency tranches; monitor sovereign stability."
    })
    
    # 2. REGULATORY RISK
    rn = specialist_reports.get("REGULATORY_NAVIGATOR", {})
    facts_leg = grounding_facts.get("Legal Data", {}) if grounding_facts else {}
    start_score = facts_leg.get("Starting a Business Score", "N/A")
    
    if not rn.get("data_verified", False) or start_score == "N/A":
        reg_level = "UNKNOWN"
        reg_rationale = f"Commercial incorporation rankings unavailable for {target_market}."
    else:
        try:
            s_num = float(start_score)
            reg_level = "LOW" if s_num >= 80.0 else ("MEDIUM" if s_num >= 60.0 else "HIGH")
            reg_rationale = f"Starting a Business Score: {s_num:.1f}/100."
        except Exception:
            reg_level = "UNKNOWN"
            reg_rationale = f"Unparsed regulatory metrics for {target_market}."
            
    risks.append({
        "risk_id": "RISK-002",
        "category": "REGULATORY RISK",
        "level": reg_level,
        "specialist": "Regulatory Navigator",
        "evidence_ref": "EVID-003",
        "rationale": reg_rationale,
        "mitigation": "Engage local counsel for incorporation and data sovereignty clearance prior to launch."
    })
    
    # 3. MARKET VALIDATION RISK
    mv = specialist_reports.get("MARKET_VALIDATOR", {})
    mv_rec = str(mv.get("recommendation", "MAYBE")).upper()
    mv_ver = mv.get("data_verified", False)
    
    if not mv_ver:
        mkt_level = "UNKNOWN"
        mkt_rationale = f"Startup ecosystem dataset unavailable for {target_market}."
    elif mv_rec == "YES":
        mkt_level = "LOW"
        mkt_rationale = "Active startup ecosystem and venture liquidity documented."
    elif mv_rec == "NO":
        mkt_level = "HIGH"
        mkt_rationale = mv.get("primary_concern") or "Significant ecosystem headwinds identified."
    else:
        mkt_level = "MEDIUM"
        mkt_rationale = mv.get("primary_concern") or "Demand validation requires primary customer pilot surveys."
        
    risks.append({
        "risk_id": "RISK-003",
        "category": "MARKET VALIDATION RISK",
        "level": mkt_level,
        "specialist": "Market Validator",
        "evidence_ref": "EVID-001",
        "rationale": mkt_rationale,
        "mitigation": "Conduct 20+ qualitative discovery interviews and obtain 3 signed letters of intent."
    })
    
    # 4. COMPETITIVE RISK
    cs = specialist_reports.get("COMPETITIVE_SCOUT", {})
    cs_rec = str(cs.get("recommendation", "MAYBE")).upper()
    cs_ver = cs.get("data_verified", False)
    
    if not cs_ver:
        comp_level = "UNKNOWN"
        comp_rationale = f"Competitor dataset unavailable for {target_market}."
    elif cs_rec == "YES":
        comp_level = "LOW"
        comp_rationale = "Differentiated positioning path viable."
    elif cs_rec == "NO":
        comp_level = "HIGH"
        comp_rationale = cs.get("primary_concern") or "Heavy incumbent market concentration."
    else:
        comp_level = "MEDIUM"
        comp_rationale = cs.get("primary_concern") or "Incumbent market entrenchment and pricing power."
        
    risks.append({
        "risk_id": "RISK-004",
        "category": "COMPETITIVE RISK",
        "level": comp_level,
        "specialist": "Competitive Scout",
        "evidence_ref": "EVID-002",
        "rationale": comp_rationale,
        "mitigation": "Focus on high-velocity underserved vertical niches; avoid direct feature parity battles."
    })
    
    # 5. DATA ACCESS RISK
    missing_count = sum(1 for r in [vr, rn, mv, cs] if not r.get("data_verified", False))
    if missing_count >= 2:
        data_level = "HIGH"
        data_rationale = f"Significant data gaps: {missing_count} domain(s) unverified."
    elif missing_count == 1:
        data_level = "MEDIUM"
        data_rationale = "Partial data availability; 1 domain unverified."
    else:
        data_level = "LOW"
        data_rationale = "Complete dataset coverage across all core operational domains."
        
    risks.append({
        "risk_id": "RISK-005",
        "category": "DATA ACCESS RISK",
        "level": data_level,
        "specialist": "Data Audit Service",
        "evidence_ref": "EVID-001",
        "rationale": data_rationale,
        "mitigation": "Perform localized primary field research to fill remaining empirical data gaps."
    })
    
    # 6. CAPITAL RISK
    cap = specialist_reports.get("CAPITAL_STRATEGIST", {})
    cap_rec = str(cap.get("recommendation", "MAYBE")).upper()
    cap_ver = cap.get("data_verified", False)
    
    if not cap_ver:
        cap_level = "UNKNOWN"
        cap_rationale = f"Funding benchmark dataset missing for {target_market}."
    elif cap_rec == "YES":
        cap_level = "LOW"
        cap_rationale = "Budget aligned with local venture formation benchmarks."
    elif cap_rec == "NO":
        cap_level = "HIGH"
        cap_rationale = cap.get("primary_concern") or "Severe capital under-sizing identified."
    else:
        cap_level = "MEDIUM"
        cap_rationale = cap.get("primary_concern") or "Capital sizing requires strict burn-rate governance."
        
    risks.append({
        "risk_id": "RISK-006",
        "category": "CAPITAL RISK",
        "level": cap_level,
        "specialist": "Capital Strategist",
        "evidence_ref": "EVID-006",
        "rationale": cap_rationale,
        "mitigation": "Enforce strict monthly burn rate ceiling; stage capital release on milestone achievement."
    })
    
    # 7. OPERATIONAL RISK
    lo = specialist_reports.get("LAUNCH_OPERATIONS", {})
    lo_ver = lo.get("data_verified", False)
    facts_log = grounding_facts.get("Market Data", {}) if grounding_facts else {}
    lpi_val = facts_log.get("Logistics Performance Score (2023)", facts_log.get("Logistics Performance Score", "N/A"))
    
    if not lo_ver or lpi_val == "N/A":
        op_level = "UNKNOWN"
        op_rationale = f"Logistics and supply chain metrics unavailable for {target_market}."
    else:
        try:
            l_num = float(lpi_val)
            op_level = "LOW" if l_num >= 3.2 else ("MEDIUM" if l_num >= 2.5 else "HIGH")
            op_rationale = f"Logistics Performance Score: {l_num:.1f}/5.0."
        except Exception:
            op_level = "UNKNOWN"
            op_rationale = f"Unparsed logistics score for {target_market}."
            
    risks.append({
        "risk_id": "RISK-007",
        "category": "OPERATIONAL RISK",
        "level": op_level,
        "specialist": "Launch Operations",
        "evidence_ref": "EVID-004",
        "rationale": op_rationale,
        "mitigation": "Utilize cloud-native infrastructure and regional 3PL partners to avoid fixed operational overhead."
    })
    
    return risks

def build_critical_blockers(specialist_reports: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Constructs structured Critical Blockers with BLOCKER-001... IDs.
    Links each blocker to evidence references, source specialists, and clear resolution conditions.
    Decouples infrastructure errors from business blockers.
    """
    blockers = []
    idx = 1
    
    agent_names = [
        ("MARKET_VALIDATOR", "Market Validator", "EVID-001"),
        ("COMPETITIVE_SCOUT", "Competitive Scout", "EVID-002"),
        ("REGULATORY_NAVIGATOR", "Regulatory Navigator", "EVID-003"),
        ("LAUNCH_OPERATIONS", "Launch Operations", "EVID-004"),
        ("VENTURE_RISK", "Venture Risk", "EVID-005"),
        ("CAPITAL_STRATEGIST", "Capital Strategist", "EVID-006")
    ]
    
    for aid, name, evid_ref in agent_names:
        rep = specialist_reports.get(aid, {})
        status = rep.get("status", "")
        rec = str(rep.get("recommendation", "")).upper()
        concern = str(rep.get("primary_concern", "") or "")
        analysis = str(rep.get("analysis", "") or "")
        is_ver = rep.get("data_verified", False)
        
        # 1. Execution error (CRITICAL)
        if status == "error":
            blockers.append({
                "blocker_id": f"BLOCKER-{idx:03d}",
                "id": f"BLOCKER-{idx:03d}",
                "title": f"{name} Execution Failure",
                "description": f"Agent node encountered an execution error: {rep.get('error_message', 'API/Model execution failure')}",
                "source_specialist": name,
                "source": name,
                "evidence_reference": evid_ref,
                "severity": "CRITICAL",
                "status": "OPEN",
                "resolution_condition": "Resolve API connectivity / execution exception and re-run specialist node."
            })
            idx += 1
            continue

        # If there's an infrastructure/API failure tag in concern without business concern, skip adding it as a business blocker
        if "[API FAILURE]" in concern or "[EXECUTION ERROR]" in concern:
            continue
            
        # 2. Explicit NO vote (CRITICAL business blocker)
        if rec in ["NO", "DO NOT LAUNCH", "REJECT"]:
            b_desc = concern if len(concern) > 10 else f"{name} identified insurmountable launch risks under current parameters."
            blocker_item = {
                "blocker_id": f"BLOCKER-{idx:03d}",
                "id": f"BLOCKER-{idx:03d}",
                "title": f"{name}: Critical Feasibility Constraint",
                "description": b_desc,
                "source_specialist": name,
                "source": name,
                "evidence_reference": evid_ref,
                "severity": "CRITICAL",
                "status": "OPEN",
                "resolution_condition": rep.get("mind_change_threshold", "Meet specialist validation criteria and resolve capital/operational constraints."),
                "mitigation_action": rep.get("mind_change_threshold", "Resolve constraint before commitment."),
                "recommendation": rep.get("recommendation", "NO")
            }
            blockers.append(blocker_item)
            idx += 1
        elif rec in ["MAYBE", "VALIDATE FIRST"] and len(concern) > 15 and not any(tag in concern for tag in ["[API FAILURE]", "[EXECUTION ERROR]"]):
            # Material concern (HIGH)
            blocker_item = {
                "blocker_id": f"BLOCKER-{idx:03d}",
                "id": f"BLOCKER-{idx:03d}",
                "title": f"{name}: Strategic & Operational Risk",
                "description": concern,
                "source_specialist": name,
                "source": name,
                "evidence_reference": evid_ref,
                "severity": "HIGH",
                "status": "OPEN",
                "resolution_condition": rep.get("mind_change_threshold", "Validate assumption through MVP test and de-risk operations."),
                "mitigation_action": rep.get("mind_change_threshold", "Validate assumption through MVP test."),
                "recommendation": rep.get("recommendation", "MAYBE")
            }
            blockers.append(blocker_item)
            idx += 1
        elif not is_ver and status == "data_unavailable":
            # Missing dataset advisory (MEDIUM)
            blocker_item = {
                "blocker_id": f"BLOCKER-{idx:03d}",
                "id": f"BLOCKER-{idx:03d}",
                "title": f"Empirical Data Gap: {name}",
                "description": f"No verified local repository data found for {name}'s domain.",
                "source_specialist": name,
                "source": name,
                "evidence_reference": evid_ref,
                "severity": "MEDIUM",
                "status": "OPEN",
                "resolution_condition": "Ingest verified empirical dataset for target market or conduct primary due diligence.",
                "mitigation_action": "Conduct primary due diligence.",
                "recommendation": rec or "MAYBE"
            }
            blockers.append(blocker_item)
            idx += 1

    return blockers

def build_validation_gates(target_market: str, capital_budget: Any, blockers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Constructs concrete Validation Gates with GATE-001... IDs.
    """
    gates = []
    idx = 1
    
    gates.append({
        "gate_id": f"GATE-{idx:03d}",
        "title": "Customer Problem Validation",
        "condition": f"Conduct 30 structured customer discovery interviews in {target_market} confirming urgent willingness to adopt.",
        "success_metric": ">= 70% positive intent rating and >= 3 LOIs / pilot agreements signed",
        "category": "PROPOSED VALIDATION GATE",
        "status": "PENDING"
    })
    idx += 1
    
    gates.append({
        "gate_id": f"GATE-{idx:03d}",
        "title": "Legal & Incorporation Clearance",
        "condition": f"Obtain formal memorandum from licensed corporate counsel in {target_market} confirming entity structure and regulatory compliance.",
        "success_metric": "Clean legal sign-off with zero fatal regulatory barriers",
        "category": "PROPOSED VALIDATION GATE",
        "status": "PENDING"
    })
    idx += 1
    
    gates.append({
        "gate_id": f"GATE-{idx:03d}",
        "title": "Unit Economic & Runway Stress Test",
        "condition": f"Calibrate bottom-up financial model proving >= 18 months of operating runway under proposed budget.",
        "success_metric": "CAC/LTV ratio > 3.0x with verified margin assumptions",
        "category": "DETERMINISTIC POLICY",
        "status": "PENDING"
    })
    idx += 1
    
    return gates

def build_executive_action_plan(blockers: List[Dict[str, Any]], gates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates high-priority executive action steps directly derived from blockers and validation gates.
    """
    actions = []
    
    # Priority 1: Address Critical Blockers
    crit_blockers = [b for b in blockers if b.get("severity") == "CRITICAL"]
    for b in crit_blockers[:2]:
        actions.append({
            "priority": "P1 - CRITICAL",
            "action": f"Resolve {b.get('title')}",
            "reason": b.get("description"),
            "source_ref": b.get("blocker_id"),
            "success_condition": b.get("resolution_condition"),
            "timeframe": "Weeks 1-4",
            "decision_impact": "Prerequisite to any capital disbursement"
        })
        
    # Priority 2: Execute Validation Gates
    for g in gates[:3]:
        actions.append({
            "priority": "P2 - VALIDATION",
            "action": g.get("title"),
            "reason": g.get("condition"),
            "source_ref": g.get("gate_id"),
            "success_condition": g.get("success_metric"),
            "timeframe": "Months 1-3",
            "decision_impact": "Unlocks Phase-2 MVP development"
        })
        
    # Priority 3: Address High / Medium Blockers
    other_blockers = [b for b in blockers if b.get("severity") in ["HIGH", "MEDIUM"]]
    for b in other_blockers[:2]:
        actions.append({
            "priority": "P3 - OPTIMIZATION",
            "action": f"Mitigate {b.get('title')}",
            "reason": b.get("description"),
            "source_ref": b.get("blocker_id"),
            "success_condition": b.get("resolution_condition"),
            "timeframe": "Months 3-6",
            "decision_impact": "Reduces operational friction"
        })
        
    return actions

def classify_mind_change_thresholds(specialist_reports: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts mind-change thresholds and classifies them into explicit taxonomies:
    - EMPIRICAL SOURCE
    - DETERMINISTIC POLICY
    - PROPOSED VALIDATION GATE
    - MODEL SUGGESTION
    """
    agent_info = [
        ("MARKET_VALIDATOR", "Market Validator", "📊"),
        ("COMPETITIVE_SCOUT", "Competitive Scout", "🔍"),
        ("REGULATORY_NAVIGATOR", "Regulatory Navigator", "📜"),
        ("LAUNCH_OPERATIONS", "Launch Operations", "🚀"),
        ("VENTURE_RISK", "Venture Risk", "🛡️"),
        ("CAPITAL_STRATEGIST", "Capital Strategist", "💎")
    ]
    
    thresholds = []
    idx = 1
    
    for aid, name, icon in agent_info:
        rep = specialist_reports.get(aid, {})
        mct = rep.get("mind_change_threshold")
        if mct and mct != "N/A":
            mct_lower = mct.lower()
            if "loi" in mct_lower or "customer" in mct_lower or "signups" in mct_lower or "interview" in mct_lower:
                tax = "PROPOSED VALIDATION GATE"
            elif "burn rate" in mct_lower or "runway" in mct_lower or "sla" in mct_lower:
                tax = "DETERMINISTIC POLICY"
            elif "dataset" in mct_lower or "decline in" in mct_lower or "rank" in mct_lower:
                tax = "EMPIRICALLY GROUNDED THRESHOLD"
            else:
                tax = "MODEL SUGGESTION"
                
            thresholds.append({
                "id": f"MCT-{idx:03d}",
                "source": name,
                "icon": icon,
                "threshold": mct,
                "classification": tax
            })
            idx += 1
            
    return thresholds

def compute_deterministic_confidence(
    evidence_quality: Dict[str, Any],
    vote_distribution: Dict[str, int],
    blockers: List[Dict[str, Any]],
    rules_passed: int,
    total_rules: int,
    final_recommendation: str = ""
) -> Dict[str, Any]:
    """
    TRANSPARENT MATHEMATICAL CONFIDENCE FORMULA.
    Measures certainty in the engine's verdict (whether PROCEED or DO NOT LAUNCH).
    """
    # 1. Evidence coverage (0 - 100)
    cov_score = float(evidence_quality.get("coverage_percent", 0))
    
    # 2. Specialist agreement (0 - 100)
    yes_c = vote_distribution.get("YES", 0)
    maybe_c = vote_distribution.get("MAYBE", 0)
    no_c = vote_distribution.get("NO", 0)
    tot_votes = max(1, yes_c + maybe_c + no_c)
    
    is_do_not_launch = "DO NOT LAUNCH" in final_recommendation.upper() or "NO" in final_recommendation.upper() or no_c >= 2
    
    if is_do_not_launch:
        agreement_score = ((no_c * 100.0) + (maybe_c * 60.0) + (yes_c * 10.0)) / tot_votes
        failed_rules = total_rules - rules_passed
        rule_decisiveness = (failed_rules / max(1, total_rules)) * 100.0 if failed_rules > 0 else 75.0
        base_confidence = (cov_score * 0.35) + (agreement_score * 0.40) + (rule_decisiveness * 0.25)
        final_conf = max(75, min(95, int(round(base_confidence))))
        penalties = 0.0
    else:
        agreement_score = ((yes_c * 100.0) + (maybe_c * 50.0) + (no_c * 0.0)) / tot_votes
        rule_score = (rules_passed / max(1, total_rules)) * 100.0
        base_confidence = (cov_score * 0.35) + (agreement_score * 0.35) + (rule_score * 0.30)
        
        crit_count = sum(1 for b in blockers if b.get("severity") == "CRITICAL")
        high_count = sum(1 for b in blockers if b.get("severity") == "HIGH")
        penalties = (crit_count * 10.0) + (high_count * 5.0)
        final_conf = max(15, min(98, int(round(base_confidence - penalties))))
    
    return {
        "final_confidence": final_conf,
        "evidence_coverage_component": round(cov_score * 0.35, 1),
        "specialist_agreement_component": round(agreement_score * (0.40 if is_do_not_launch else 0.35), 1),
        "rule_satisfaction_component": round((rule_decisiveness if is_do_not_launch else rule_score) * (0.25 if is_do_not_launch else 0.30), 1),
        "blocker_penalty": round(penalties, 1),
        "formula": "Confidence = (0.35 * EvidenceCoverage) + (AgreementComponent) + (RuleComponent) - BlockerPenalties",
        "confidence_semantics_explanation": "Confidence in the BoardRoomAI decision given evidence coverage, specialist agreement, and deterministic rule satisfaction (not a predictive probability of future business success)."
    }


def compute_deterministic_risk_mitigation(
    risk_matrix: List[Dict[str, Any]],
    blockers: List[Dict[str, Any]],
    validation_gates: List[Dict[str, Any]],
    rule_evaluations: List[Dict[str, Any]],
    evidence_quality: Dict[str, Any],
    specialist_reports: Optional[Dict[str, Any]] = None,
    capital_budget: Any = None,
    target_market: str = ""
) -> Dict[str, Any]:
    """
    CANONICAL DETERMINISTIC RISK MITIGATION CALCULATION.
    Shared identically across Streamlit Dashboard, PDF Report, and Decision Engine.
    
    Measures: How effectively identified risks, blockers, and validation gates are mitigated
    under the proposed venture plan based on empirical evidence.
    
    Formula Components:
    - Base Mitigation: 100
    - Risk Matrix Residual Penalties (evaluated per category: LOW=0, MEDIUM=-6, HIGH=-14 to -20, UNKNOWN=-9)
    - Blocker Penalties (CRITICAL=-15, HIGH=-8, MEDIUM=-3)
    - Validation Gate Penalties (PENDING=-3 each)
    - Policy Rule Penalties (FAIL=-8 each, CONDITIONAL=-2.5 each)
    - Evidence Quality Adjustment (Coverage gap penalty + error penalty)
    
    Returns structured breakdown, drivers, itemized penalties, and arithmetic audit trace.
    """
    base_score = 100.0
    penalties = []
    drivers = []
    category_breakdown = {}
    
    # 1. Evaluate Risk Matrix Categories (7 Categories)
    cat_order = [
        "MACRO RISK",
        "REGULATORY RISK",
        "MARKET VALIDATION RISK",
        "COMPETITIVE RISK",
        "OPERATIONAL RISK",
        "CAPITAL RISK",
        "DATA ACCESS RISK"
    ]
    
    # Normalize risk matrix lookup
    risk_by_cat = {}
    for r in (risk_matrix or []):
        cat_key = r.get("category", "").upper().strip()
        risk_by_cat[cat_key] = r
        
    for cat_name in cat_order:
        r_item = risk_by_cat.get(cat_name)
        if not r_item:
            for k, v in risk_by_cat.items():
                if cat_name in k or k in cat_name:
                    r_item = v
                    break
                    
        lvl = (r_item.get("level") if r_item else "UNKNOWN").upper()
        rid = r_item.get("risk_id", "RISK-000") if r_item else "RISK-GEN"
        rationale = r_item.get("rationale", "No empirical risk rationale available.") if r_item else "Unverified risk domain."
        mitigation = r_item.get("mitigation", "Implement standard risk governance controls.") if r_item else "Conduct primary due diligence."
        
        if lvl == "LOW":
            cat_score = 92
            cat_status = "CONTROLLED"
            drivers.append({
                "status": "PASS",
                "icon": "✓",
                "category": cat_name.title(),
                "text": f"{cat_name.title()}: Controls substantially addressed ({rationale})"
            })
        elif lvl == "MEDIUM":
            cat_score = 65
            cat_status = "MODERATE RISK"
            penalties.append({
                "source_id": rid,
                "domain": cat_name.title(),
                "reason": f"Medium risk level: {rationale}",
                "penalty": -6.0
            })
            drivers.append({
                "status": "WARN",
                "icon": "⚠",
                "category": cat_name.title(),
                "text": f"{cat_name.title()}: Requires operational oversight and monitoring ({rationale})"
            })
        elif lvl == "HIGH":
            has_mit = bool(mitigation and len(mitigation) > 15 and mitigation != "N/A")
            p_val = 14.0 if has_mit else 20.0
            cat_score = 35 if has_mit else 20
            cat_status = "ELEVATED RISK"
            penalties.append({
                "source_id": rid,
                "domain": cat_name.title(),
                "reason": f"High risk level: {rationale}",
                "penalty": -p_val
            })
            drivers.append({
                "status": "FAIL",
                "icon": "✕",
                "category": cat_name.title(),
                "text": f"{cat_name.title()}: Severe exposure identified ({rationale})"
            })
        else: # UNKNOWN / DATA GAP
            cat_score = 40
            cat_status = "UNVERIFIED DATA GAP"
            penalties.append({
                "source_id": rid,
                "domain": cat_name.title(),
                "reason": f"Missing/unverified dataset for {cat_name.title()}",
                "penalty": -9.0
            })
            drivers.append({
                "status": "WARN",
                "icon": "⚠",
                "category": cat_name.title(),
                "text": f"{cat_name.title()}: Empirical dataset unavailable; unverified exposure"
            })
            
        category_breakdown[cat_name.title()] = {
            "risk_id": rid,
            "level": lvl,
            "mitigation_score": cat_score,
            "status": cat_status,
            "rationale": rationale,
            "mitigation": mitigation
        }

    # 2. Critical Blockers Penalties
    for b in (blockers or []):
        bid = b.get("blocker_id", "BLOCKER-000")
        sev = b.get("severity", "MEDIUM").upper()
        title = b.get("title", "Blocker")
        desc = b.get("description", "")
        
        if sev == "CRITICAL":
            penalties.append({
                "source_id": bid,
                "domain": "Critical Blocker",
                "reason": f"CRITICAL blocker: {title} ({desc[:80]}...)" if len(desc) > 80 else f"CRITICAL blocker: {title} ({desc})",
                "penalty": -15.0
            })
            drivers.append({
                "status": "FAIL",
                "icon": "✕",
                "category": "Blocker",
                "text": f"Critical Blocker: {title}"
            })
        elif sev == "HIGH":
            penalties.append({
                "source_id": bid,
                "domain": "High Advisory Blocker",
                "reason": f"HIGH blocker: {title}",
                "penalty": -8.0
            })
            drivers.append({
                "status": "WARN",
                "icon": "⚠",
                "category": "Blocker",
                "text": f"High Priority Blocker: {title}"
            })
        elif sev == "MEDIUM":
            penalties.append({
                "source_id": bid,
                "domain": "Advisory Blocker",
                "reason": f"MEDIUM advisory: {title}",
                "penalty": -3.0
            })

    # 3. Validation Gates Penalties (Pending gates)
    pending_gates = [g for g in (validation_gates or []) if g.get("status") != "RESOLVED" and g.get("status") != "PASSED"]
    if pending_gates:
        p_gates = len(pending_gates) * 3.0
        penalties.append({
            "source_id": "GATES-PENDING",
            "domain": "Validation Gates",
            "reason": f"{len(pending_gates)} pending validation milestone(s) require resolution before rollout",
            "penalty": -p_gates
        })
        drivers.append({
            "status": "WARN",
            "icon": "⚠",
            "category": "Validation Gates",
            "text": f"{len(pending_gates)} validation milestone(s) pending customer and legal clearance"
        })

    # 4. Policy Rule Penalties (FAIL / CONDITIONAL rules)
    failed_rules = [r for r in (rule_evaluations or []) if r.get("status") == "FAIL" or r.get("result") == "FAIL"]
    cond_rules = [r for r in (rule_evaluations or []) if r.get("status") == "CONDITIONAL" or r.get("result") == "CONDITIONAL"]
    
    for r in failed_rules:
        rid = r.get("rule_id", "RULE-000")
        cat = r.get("category", "Policy Rule")
        penalties.append({
            "source_id": rid,
            "domain": "Policy Rule Failure",
            "reason": f"Failed deterministic rule {rid} ({cat}): {r.get('rationale', r.get('reason', ''))}",
            "penalty": -8.0
        })
        drivers.append({
            "status": "FAIL",
            "icon": "✕",
            "category": "Rule Evaluation",
            "text": f"Policy Rule {rid} Failed: {cat}"
        })
        
    for r in cond_rules:
        rid = r.get("rule_id", "RULE-000")
        cat = r.get("category", "Conditional Policy")
        penalties.append({
            "source_id": rid,
            "domain": "Conditional Policy Rule",
            "reason": f"Conditional rule {rid} ({cat}): {r.get('rationale', r.get('reason', ''))}",
            "penalty": -2.5
        })

    # 5. Evidence Quality Adjustment
    cov_pct = float(evidence_quality.get("coverage_percent", 0)) if evidence_quality else 0.0
    err_count = int(evidence_quality.get("errors", 0)) if evidence_quality else 0
    
    if err_count > 0:
        p_err = err_count * 15.0
        penalties.append({
            "source_id": "AGENT-ERRORS",
            "domain": "Agent Execution Error",
            "reason": f"{err_count} specialist agent execution error(s) detected",
            "penalty": -p_err
        })
        drivers.append({
            "status": "FAIL",
            "icon": "✕",
            "category": "System Integrity",
            "text": f"{err_count} agent execution failure(s) undermine risk certainty"
        })
        
    if cov_pct < 100.0:
        cov_penalty = round(0.12 * (100.0 - cov_pct), 1)
        penalties.append({
            "source_id": "EVID-COVERAGE-GAP",
            "domain": "Evidence Coverage Gap",
            "reason": f"{100.0 - cov_pct:.0f}% unverified dataset coverage creates information risk",
            "penalty": -cov_penalty
        })
        drivers.append({
            "status": "WARN",
            "icon": "⚠",
            "category": "Evidence Coverage",
            "text": f"Empirical coverage at {cov_pct:.0f}% ({evidence_quality.get('verified', 0)}/6 domains verified)"
        })
    else:
        drivers.append({
            "status": "PASS",
            "icon": "✓",
            "category": "Evidence Coverage",
            "text": "100% empirical dataset grounding across all specialist domains"
        })

    # 6. Aggregate Total Penalty and Clamped Score
    total_penalty = sum(abs(p["penalty"]) for p in penalties)
    raw_score = base_score - total_penalty
    final_score = max(5, min(98, int(round(raw_score))))
    
    # 7. Rating Label and Color
    if final_score >= 85:
        rating_label = "STRONG MITIGATION"
        rating_color = "#00FF88"
        status_desc = "Risk factors are substantially controlled with verified mitigations."
    elif final_score >= 70:
        rating_label = "SUBSTANTIAL MITIGATION"
        rating_color = "#00D4FF"
        status_desc = "Key risks managed; operational and market safeguards active."
    elif final_score >= 50:
        rating_label = "MODERATE MITIGATION"
        rating_color = "#FFB800"
        status_desc = "Moderate risk exposure; validation milestones required."
    elif final_score >= 30:
        rating_label = "ELEVATED RESIDUAL RISK"
        rating_color = "#FF8C00"
        status_desc = "Significant unmitigated risk factors require remediation."
    else:
        rating_label = "CRITICAL RISK DEFICIT"
        rating_color = "#FF6B6B"
        status_desc = "Critical unmitigated blockers and fatal risk exposure."

    # 8. Compile Traceable Audit Trail
    audit_steps = [f"Base Score = {base_score:.1f}"]
    for p in penalties:
        audit_steps.append(f"[{p['source_id']}] {p['domain']}: {p['penalty']:+.1f} pts ({p['reason']})")
    audit_steps.append(f"Raw Score = {raw_score:.1f}")
    audit_steps.append(f"Clamped Final Score = {final_score}% ({rating_label})")
    
    return {
        "risk_mitigation_score": final_score,
        "score": final_score,
        "rating_label": rating_label,
        "rating_color": rating_color,
        "status_description": status_desc,
        "base_score": int(base_score),
        "total_penalty": round(total_penalty, 1),
        "formula_version": "v2.0-CANONICAL-DETERMINISTIC",
        "formula": "Risk Mitigation = Clamp(100 - (RiskPenalties + BlockerPenalties + GatePenalties + RulePenalties + CoveragePenalties), 5, 98)",
        "category_breakdown": category_breakdown,
        "penalties": penalties,
        "drivers": drivers,
        "audit_steps": audit_steps,
        "is_deterministic": True,
        "cannot_be_overridden_by_llm": True,
        "semantics_explanation": "Measures how effectively identified venture risks, critical blockers, and validation gates are mitigated under the proposed venture plan based on empirical evidence (never a default 100%)."
    }
