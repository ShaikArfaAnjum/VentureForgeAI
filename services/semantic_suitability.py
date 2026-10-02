"""
BoardRoomAI - Semantic Evidence Suitability Layer
Evaluates whether a dataset/metric is semantically appropriate for a given venture claim.
Distinguishes DIRECT, INDIRECT, WEAK, and NOT-SUITABLE evidence to prevent semantic misuse.
"""
from typing import Dict, Any, List, Optional
from enum import Enum

class EvidenceRelevance(str, Enum):
    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"
    WEAK = "WEAK"
    NOT_SUITABLE = "NOT-SUITABLE"

SUITABILITY_RULES = {
    "research_data.csv": {
        "metric": "Startups Tracked & Venture Funding",
        "what_it_measures": "Observed macro startup activity and aggregate venture capital investment in the sovereign jurisdiction.",
        "what_it_supports": "Contextual indicator of national entrepreneurial activity and aggregate funding liquidity.",
        "what_it_cannot_support": "Direct proof of customer willingness to pay for a specific product, or proof that this specific venture requires the average funding amount.",
        "relevance_for_market_validation": "INDIRECT",
        "relevance_for_capital_calibration": "INDIRECT"
    },
    "competition_data.csv": {
        "metric": "Top Public Company Market Cap & Tracked Listed Entities",
        "what_it_measures": "Scale and capitalization of the largest publicly traded corporations headquartered in the country.",
        "what_it_supports": "Contextual measure of public equity market depth and institutional corporate presence.",
        "what_it_cannot_support": "Direct competitive market share, niche SaaS competitive intensity, or product feature parity.",
        "relevance_for_competition": "WEAK",
        "relevance_for_market_validation": "WEAK"
    },
    "legal_data.csv": {
        "metric": "Ease of Starting a Business / Doing Business Score",
        "what_it_measures": "General statutory incorporation friction, administrative procedures, and registration days for standard private liability companies.",
        "what_it_supports": "Baseline regulatory efficiency for standard commercial legal entity formation and incorporation timelines.",
        "what_it_cannot_support": "Sector-specific licenses, AI/data sovereignty compliance, or specialized regulatory approvals.",
        "relevance_for_legal_readiness": "INDIRECT",
        "relevance_for_operations": "INDIRECT"
    },
    "market_data.csv": {
        "metric": "Logistics Performance Index (LPI 2023)",
        "what_it_measures": "National supply chain transport efficiency, customs processing speed, trade infrastructure, and shipment tracking quality.",
        "what_it_supports": "Macro-level physical and digital supply chain operational environment and transportation infrastructure readiness.",
        "what_it_cannot_support": "Individual enterprise contract conversion rates or software product adoption willingness.",
        "relevance_for_operations": "DIRECT",
        "relevance_for_market_validation": "INDIRECT"
    },
    "risk_data.csv": {
        "metric": "Fragile States Index (FSI 2023)",
        "what_it_measures": "Sovereign macroeconomic pressure, state legitimacy, public service quality, and institutional stability.",
        "what_it_supports": "Macroeconomic sovereign risk, currency stability environment, and systemic institutional predictability.",
        "what_it_cannot_support": "Individual commercial venture financial success or micro-market product-market fit.",
        "relevance_for_risk": "DIRECT",
        "relevance_for_market_validation": "INDIRECT"
    }
}

def evaluate_evidence_suitability(dataset_name: str, domain: str, claim: str) -> Dict[str, Any]:
    """
    Evaluates semantic suitability of an evidence item.
    Returns relevance level (DIRECT, INDIRECT, WEAK, NOT-SUITABLE) with analytical boundary limits.
    """
    rule = SUITABILITY_RULES.get(dataset_name, {
        "metric": "Unregistered Metric",
        "what_it_measures": "General contextual data",
        "what_it_supports": "General context only",
        "what_it_cannot_support": "Specific commercial inferences",
        "relevance_for_general": "INDIRECT"
    })

    # Default relevance assignment based on domain
    domain_lower = domain.lower()
    if "logistics" in domain_lower or "operational" in domain_lower or "supply chain" in domain_lower:
        relevance = rule.get("relevance_for_operations", "INDIRECT")
    elif "risk" in domain_lower or "macro" in domain_lower or "sovereign" in domain_lower:
        relevance = rule.get("relevance_for_risk", "INDIRECT")
    elif "legal" in domain_lower or "regulatory" in domain_lower or "incorporation" in domain_lower:
        relevance = rule.get("relevance_for_legal_readiness", "INDIRECT")
    elif "competition" in domain_lower or "incumbent" in domain_lower:
        relevance = rule.get("relevance_for_competition", "WEAK")
    else:
        relevance = rule.get("relevance_for_market_validation", "INDIRECT")

    # Guard against invalid semantic extensions in claim text
    claim_lower = claim.lower()
    unsupported_claims_flagged = []
    
    if dataset_name == "research_data.csv":
        if any(term in claim_lower for term in ["must have", "proves we need", "guarantees customer demand"]):
            relevance = "NOT-SUITABLE"
            unsupported_claims_flagged.append("Dataset measures macro startup funding, not mandatory venture budget size.")
    elif dataset_name == "competition_data.csv":
        if any(term in claim_lower for term in ["proves high direct competition", "dominates the saas space"]):
            relevance = "NOT-SUITABLE"
            unsupported_claims_flagged.append("Public conglomerate market cap does not prove micro-SaaS niche crowdedness.")

    return {
        "dataset_name": dataset_name,
        "evidence_relevance": relevance,
        "what_it_measures": rule["what_it_measures"],
        "what_it_supports": rule["what_it_supports"],
        "what_it_cannot_support": rule["what_it_cannot_support"],
        "semantic_boundary_valid": (relevance in ["DIRECT", "INDIRECT", "WEAK"]),
        "unsupported_semantic_flags": unsupported_claims_flagged
    }

SEMANTIC_SUITABILITY_REGISTRY = SUITABILITY_RULES

def get_semantic_suitability(dataset_name: str) -> Dict[str, Any]:
    """Retrieves standard semantic suitability rules for a dataset."""
    return SUITABILITY_RULES.get(dataset_name, {
        "metric": "Unregistered Metric",
        "what_it_measures": "General contextual metric",
        "what_it_supports": "General contextual reference",
        "what_it_cannot_support": "Direct commercial conclusions"
    })

def evaluate_claim_suitability(claim: str, dataset_name: str, domain: str = "general") -> Dict[str, Any]:
    """Alias for evaluate_evidence_suitability with (claim, dataset_name, domain) signature."""
    res = evaluate_evidence_suitability(dataset_name, domain, claim)
    return {
        "relevance": res["evidence_relevance"],
        **res
    }

