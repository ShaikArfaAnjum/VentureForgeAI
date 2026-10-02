"""
BoardRoomAI — Track B Orchestrator (New Business Launch)
Production-grade, audit-traceable multi-agent simulation engine.
Integrates Canonical BoardRoomResult, Evidence Ledger, Deterministic Decision Engine,
and Founder CEO Discrepancy Protection.
"""

import time
import os
import traceback
from typing import Dict, Any, List, Optional
from decimal import Decimal

from agents.market_validator_agent import validate_market
from agents.competitive_scout_agent import scout_competition
from agents.regulatory_navigator_agent import navigate_regulations
from agents.launch_operations_agent import evaluate_launch_operations
from agents.venture_risk_agent import assess_venture_risk
from agents.capital_strategist_agent import strategize_capital
from agents.founder_ceo_agent import decide_founder_ceo
from services.boardroom_orchestrator import run_boardroom_session
from services.data_service import get_data
from services.canonical_result import (
    APP_VERSION,
    ENGINE_VERSION,
    get_evidence_quality,
    build_evidence_ledger,
    build_risk_matrix,
    build_critical_blockers,
    build_validation_gates,
    build_executive_action_plan,
    classify_mind_change_thresholds,
    compute_deterministic_confidence,
    compute_deterministic_risk_mitigation,
    compute_dataset_hash
)
from services.deterministic_decision_engine import evaluate_deterministic_decision
from services.consistency_validator import validate_consistency
from services.dataset_provenance import get_dataset_provenance_record, verify_all_datasets_integrity
from services.claim_validator import ClaimValidator
from services.track_b_scoring_engine import calculate_launch_scores

# Definition of the 6 Track B specialist agents
TRACK_B_AGENTS = [
    {
        "id": "MARKET_VALIDATOR",
        "name": "Market Validator",
        "icon": "📊",
        "color": "#00D4FF", # Cyan
        "role": "Startup Ecosystem & Demand Validation",
        "function": validate_market,
        "dataset": "research_data.csv",
        "data_type": "Research Data"
    },
    {
        "id": "COMPETITIVE_SCOUT",
        "name": "Competitive Scout",
        "icon": "🔍",
        "color": "#FF6B6B", # Coral
        "role": "Market Cap & Incumbent Concentration",
        "function": scout_competition,
        "dataset": "competition_data.csv",
        "data_type": "Competition Data"
    },
    {
        "id": "REGULATORY_NAVIGATOR",
        "name": "Regulatory Navigator",
        "icon": "📜",
        "color": "#FFD700", # Gold
        "role": "Ease of Business & Legal Compliance",
        "function": navigate_regulations,
        "dataset": "legal_data.csv",
        "data_type": "Legal Data"
    },
    {
        "id": "LAUNCH_OPERATIONS",
        "name": "Launch Operations",
        "icon": "🚀",
        "color": "#00FF88", # Mint Green
        "role": "Logistics & Operational Infrastructure",
        "function": evaluate_launch_operations,
        "dataset": "market_data.csv",
        "data_type": "Market Data"
    },
    {
        "id": "VENTURE_RISK",
        "name": "Venture Risk",
        "icon": "🛡️",
        "color": "#FF8C00", # Dark Orange
        "role": "Sovereign Fragility & Risk Management",
        "function": assess_venture_risk,
        "dataset": "risk_data.csv",
        "data_type": "Risk Data"
    },
    {
        "id": "CAPITAL_STRATEGIST",
        "name": "Capital Strategist",
        "icon": "💎",
        "color": "#A855F7", # Purple
        "role": "Budget Calibration & VC Benchmark Analysis",
        "function": strategize_capital,
        "dataset": "research_data.csv",
        "data_type": "Research Data"
    }
]

def calculate_track_b_consensus(
    specialist_reports: Dict[str, Any],
    risk_mitigation_data: Optional[Dict[str, Any]] = None,
    business_idea: str = "",
    target_market: str = "",
    capital_budget: Any = None,
    timeline: str = "",
    strategic_question: str = "",
    business_model: str = "",
    grounding_facts: Optional[Dict[str, Any]] = None,
    risk_matrix: Optional[List[Dict[str, Any]]] = None,
    critical_blockers: Optional[List[Dict[str, Any]]] = None,
    validation_gates: Optional[List[Dict[str, Any]]] = None,
    rule_evaluations: Optional[List[Dict[str, Any]]] = None,
    evidence_quality: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Authoritative calculation of Track B consensus metrics via calculate_launch_scores.
    Evaluates:
    - Opportunity Score: TAM capacity and competitive differentiation potential
    - Risk Mitigation Score: Deterministic risk coverage across matrix, blockers, and gates
    - Launch Readiness Score (market_readiness): Commercial registration, logistics rails, and lead times
    - Capital Feasibility Score (financial_feasibility): Budget sizing calibration relative to benchmarks and burn rate
    - Overall Launch Score: Balanced fiduciary composite
    """
    scores = calculate_launch_scores(
        venture_idea=business_idea,
        target_market=target_market,
        budget=capital_budget,
        timeline=timeline,
        strategic_question=strategic_question,
        business_model=business_model,
        specialist_reports=specialist_reports,
        grounding_facts=grounding_facts,
        risk_matrix=risk_matrix,
        critical_blockers=critical_blockers,
        validation_gates=validation_gates,
        rule_evaluations=rule_evaluations,
        evidence_quality=evidence_quality
    )

    if risk_mitigation_data and isinstance(risk_mitigation_data, dict) and "risk_mitigation_score" in risk_mitigation_data:
        det_risk = int(risk_mitigation_data["risk_mitigation_score"])
        scores["risk_mitigation_score"] = det_risk
        raw_overall = (
            0.25 * scores["opportunity_score"] +
            0.25 * det_risk +
            0.25 * scores["launch_readiness_score"] +
            0.25 * scores["capital_feasibility_score"]
        )
        if scores["capital_feasibility_score"] < 20 or scores["launch_readiness_score"] < 20:
            raw_overall = min(raw_overall, 25.0)
        elif scores["capital_feasibility_score"] < 35 or scores["launch_readiness_score"] < 35:
            raw_overall = min(raw_overall, 48.0)
        scores["overall_launch_score"] = int(max(5, min(96, round(raw_overall))))

    return scores

def analyze_board_agreement(specialist_reports: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes agreement/consensus breakdown across the 6 specialist reports.
    """
    yes_count = 0
    maybe_count = 0
    no_count = 0
    
    agent_ids = ["MARKET_VALIDATOR", "COMPETITIVE_SCOUT", "REGULATORY_NAVIGATOR", "LAUNCH_OPERATIONS", "VENTURE_RISK", "CAPITAL_STRATEGIST"]
    
    for aid in agent_ids:
        rep = specialist_reports.get(aid, {})
        rec = str(rep.get("recommendation", "MAYBE")).upper()
        if rec in ["YES", "LAUNCH", "ENTER", "ENTER MARKET"]:
            yes_count += 1
        elif rec in ["NO", "DO NOT LAUNCH", "REJECT", "REJECT EXPANSION"]:
            no_count += 1
        else:
            maybe_count += 1
            
    eq = get_evidence_quality(specialist_reports)
    
    return {
        "yes_count": yes_count,
        "maybe_count": maybe_count,
        "no_count": no_count,
        "verified_count": eq["verified"],
        "data_unavailable_count": eq["unavailable"],
        "error_count": eq["errors"],
        "total_specialists": len(agent_ids),
        "is_reliable": eq["is_complete"]
    }

def detect_board_disagreements(specialist_reports: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects concrete disagreements between specialist agents based on actual votes and concerns.
    """
    agent_names = {
        "MARKET_VALIDATOR": "Market Validator",
        "COMPETITIVE_SCOUT": "Competitive Scout",
        "REGULATORY_NAVIGATOR": "Regulatory Navigator",
        "LAUNCH_OPERATIONS": "Launch Operations",
        "VENTURE_RISK": "Venture Risk",
        "CAPITAL_STRATEGIST": "Capital Strategist"
    }
    
    agent_icons = {
        "MARKET_VALIDATOR": "📊",
        "COMPETITIVE_SCOUT": "🔍",
        "REGULATORY_NAVIGATOR": "📜",
        "LAUNCH_OPERATIONS": "🚀",
        "VENTURE_RISK": "🛡️",
        "CAPITAL_STRATEGIST": "💎"
    }
    
    yes_agents = []
    no_agents = []
    maybe_agents = []
    
    for aid, name in agent_names.items():
        rep = specialist_reports.get(aid, {})
        rec = str(rep.get("recommendation", "MAYBE")).upper()
        finding = rep.get("key_finding") or rep.get("strongest_evidence") or rep.get("analysis", "")
        concern = rep.get("primary_concern") or rep.get("analysis", "")
        
        agent_data = {
            "id": aid,
            "name": name,
            "icon": agent_icons.get(aid, "👤"),
            "recommendation": rec,
            "finding": finding,
            "concern": concern,
            "confidence": rep.get("confidence", 0)
        }
        
        if rec in ["YES", "LAUNCH", "ENTER", "ENTER MARKET"]:
            yes_agents.append(agent_data)
        elif rec in ["NO", "DO NOT LAUNCH", "REJECT", "REJECT EXPANSION"]:
            no_agents.append(agent_data)
        else:
            maybe_agents.append(agent_data)
            
    disagreements = []
    
    if yes_agents and no_agents:
        for y_agent in yes_agents:
            for n_agent in no_agents:
                disagreements.append({
                    "agent_a": y_agent["name"],
                    "icon_a": y_agent["icon"],
                    "rec_a": y_agent["recommendation"],
                    "point_a": y_agent["finding"],
                    "agent_b": n_agent["name"],
                    "icon_b": n_agent["icon"],
                    "rec_b": n_agent["recommendation"],
                    "point_b": n_agent["concern"]
                })
    elif yes_agents and maybe_agents and len(yes_agents) <= 4:
        for y_agent in yes_agents[:2]:
            for m_agent in maybe_agents[:2]:
                if m_agent["concern"] and m_agent["concern"] != y_agent["finding"]:
                    disagreements.append({
                        "agent_a": y_agent["name"],
                        "icon_a": y_agent["icon"],
                        "rec_a": y_agent["recommendation"],
                        "point_a": y_agent["finding"],
                        "agent_b": m_agent["name"],
                        "icon_b": m_agent["icon"],
                        "rec_b": m_agent["recommendation"],
                        "point_b": m_agent["concern"]
                    })
                    
    has_disagreement = len(disagreements) > 0
    return {
        "has_disagreement": has_disagreement,
        "disagreements": disagreements[:3],
        "aligned_message": "✓ SPECIALISTS ARE BROADLY ALIGNED" if not has_disagreement else None
    }

def run_track_b_session(
    business_idea: str,
    target_market: str,
    capital_budget: Any,
    timeline: str,
    strategic_question: str,
    progress_callback: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Executes the Track B (New Business Launch) boardroom session.
    
    Flow:
    1. Retrieve grounding data from DataService for all specialist domains.
    2. Sequentially run 6 specialist agents with empirical context.
    3. Construct Canonical Evidence Ledger (EVID-xxx), Risk Matrix (RISK-xxx), Blockers (BLOCKER-xxx), and Gates (GATE-xxx).
    4. Run Deterministic Decision Engine (RULE-001..RULE-008) to establish ground truth decision.
    5. Pass deterministic decision and structured context to Founder CEO for synthesis.
    6. Verify Founder CEO output against deterministic decision; record discrepancy if LLM differs and lock deterministic result.
    7. Compute mathematically grounded decision confidence.
    8. Compile and validate Canonical BoardRoomResult.
    """
    specialist_reports = {}
    transcript = []
    
    print(f"\n=======================================================")
    print(f"[TRACK B] INITIATING VENTURE BOARDROOM SIMULATION")
    print(f"[TRACK B] Idea: {business_idea} | Market: {target_market} | Budget: {capital_budget}")
    print(f"=======================================================")
    
    # 1. Retrieve grounding data for all domains to populate facts
    grounding_facts = {}
    for agent_info in TRACK_B_AGENTS:
        dtype = agent_info["data_type"]
        if dtype not in grounding_facts:
            res = get_data(dtype, Country=target_market)
            if res.get("status") == "success":
                grounding_facts[dtype] = res.get("data", {})
                
    # 2. Execute the 6 Specialist Agents in sequence
    for agent_info in TRACK_B_AGENTS:
        agent_id = agent_info["id"]
        agent_name = agent_info["name"]
        
        print(f"[TRACK B] Starting {agent_name}...")
        
        if progress_callback:
            progress_callback(agent_id, "THINKING", None, None)
            
        try:
            agent_fn = agent_info["function"]
            report = agent_fn(
                business_idea=business_idea,
                target_market=target_market,
                capital_budget=capital_budget,
                timeline=timeline,
                strategic_question=strategic_question
            )
            # Ensure status is explicitly populated
            if "status" not in report:
                is_ver = report.get("data_verified", False)
                if "[API FAILURE]" in report.get("analysis", "") or "[PARSING ERROR]" in report.get("analysis", ""):
                    report["status"] = "error"
                    report["error_message"] = report.get("analysis")
                elif is_ver:
                    report["status"] = "success"
                else:
                    report["status"] = "data_unavailable"
        except Exception as e:
            err_tb = traceback.format_exc()
            print(f"[TRACK B ERROR] Exception during {agent_name} execution: {e}\n{err_tb}")
            report = {
                "status": "error",
                "error_message": str(e),
                "analysis": f"[EXECUTION ERROR] {agent_name} encountered an unexpected error: {str(e)}",
                "recommendation": "MAYBE",
                "confidence": 0,
                "dialogue": f"Analysis failed due to an unexpected execution error in {agent_name}.",
                "data_verified": False,
                "mind_change_threshold": "Resolution of the execution failure is required."
            }
            
        specialist_reports[agent_id] = report
        
        rec = report.get("recommendation", "MAYBE")
        conf = report.get("confidence", 0)
        dv = report.get("data_verified", False)
        agent_status = report.get("status", "success" if dv else "data_unavailable")
        print(f"[TRACK B] {agent_name} completed: status={agent_status}, recommendation={rec}, confidence={conf}, data_verified={dv}")
        
        dialogue_msg = {
            "agent_id": agent_id,
            "name": agent_name,
            "icon": agent_info["icon"],
            "color": agent_info["color"],
            "role": agent_info["role"],
            "status": agent_status,
            "error_message": report.get("error_message"),
            "recommendation": rec,
            "confidence": conf,
            "dialogue": report.get("dialogue", ""),
            "analysis": report.get("analysis", ""),
            "data_verified": dv,
            "mind_change_threshold": report.get("mind_change_threshold", "N/A")
        }
        transcript.append(dialogue_msg)
        
        interim_consensus = calculate_track_b_consensus(
            specialist_reports=specialist_reports,
            business_idea=business_idea,
            target_market=target_market,
            capital_budget=capital_budget,
            timeline=timeline,
            strategic_question=strategic_question,
            grounding_facts=grounding_facts
        )
        
        if progress_callback:
            progress_callback(agent_id, "COMPLETED", dialogue_msg, interim_consensus)
            
        import sys
        if "unittest" not in sys.modules and not os.getenv("TESTING"):
            time.sleep(0.4)


    # 3. Canonical Evidence Quality & Consensus Computation
    evidence_quality = get_evidence_quality(specialist_reports)
    agreement_analysis = analyze_board_agreement(specialist_reports)
    disagreements = detect_board_disagreements(specialist_reports)
    
    vote_distribution = {
        "YES": agreement_analysis["yes_count"],
        "MAYBE": agreement_analysis["maybe_count"],
        "NO": agreement_analysis["no_count"]
    }
    
    # 4. Construct Structured Artifacts
    evidence_ledger = build_evidence_ledger(
        target_market=target_market,
        capital_budget=capital_budget,
        timeline=timeline,
        specialist_reports=specialist_reports,
        grounding_facts=grounding_facts
    )
    
    risk_matrix = build_risk_matrix(
        target_market=target_market,
        specialist_reports=specialist_reports,
        grounding_facts=grounding_facts
    )
    
    critical_blockers = build_critical_blockers(specialist_reports)
    validation_gates = build_validation_gates(target_market, capital_budget, critical_blockers)
    executive_action_plan = build_executive_action_plan(critical_blockers, validation_gates)
    mind_change_thresholds = classify_mind_change_thresholds(specialist_reports)
    
    # 5. Execute Deterministic Decision Engine
    deterministic_eval = evaluate_deterministic_decision(
        target_market=target_market,
        capital_budget=capital_budget,
        specialist_reports=specialist_reports,
        evidence_quality=evidence_quality,
        blockers=critical_blockers,
        vote_distribution=vote_distribution,
        business_idea=business_idea,
        timeline=timeline,
        strategic_question=strategic_question
    )
    
    deterministic_decision = deterministic_eval["decision"]
    deterministic_rationale = deterministic_eval["policy_rationale"]
    rule_evaluations = deterministic_eval["rule_evaluations"]
    rules_passed = deterministic_eval["rules_passed_count"]
    total_rules = deterministic_eval["total_rules"]
    
    # 5.1. Execute Canonical Deterministic Risk Mitigation Calculation
    risk_mitigation_data = compute_deterministic_risk_mitigation(
        risk_matrix=risk_matrix,
        blockers=critical_blockers,
        validation_gates=validation_gates,
        rule_evaluations=rule_evaluations,
        evidence_quality=evidence_quality,
        specialist_reports=specialist_reports,
        capital_budget=capital_budget,
        target_market=target_market
    )
    
    consensus_metrics = calculate_track_b_consensus(
        specialist_reports=specialist_reports,
        risk_mitigation_data=risk_mitigation_data,
        business_idea=business_idea,
        target_market=target_market,
        capital_budget=capital_budget,
        timeline=timeline,
        strategic_question=strategic_question,
        grounding_facts=grounding_facts,
        risk_matrix=risk_matrix,
        critical_blockers=critical_blockers,
        validation_gates=validation_gates,
        rule_evaluations=rule_evaluations,
        evidence_quality=evidence_quality
    )
    
    # 6. Execute Founder CEO Synthesis Agent
    print(f"[TRACK B] Starting Founder CEO...")
    if progress_callback:
        progress_callback("FOUNDER_CEO", "THINKING", None, None)
        
    try:
        founder_ceo_report = decide_founder_ceo(
            business_idea=business_idea,
            target_market=target_market,
            capital_budget=capital_budget,
            timeline=timeline,
            strategic_question=strategic_question,
            specialist_reports=specialist_reports
        )
    except Exception as e:
        err_tb = traceback.format_exc()
        print(f"[TRACK B ERROR] Exception during Founder CEO execution: {e}\n{err_tb}")
        founder_ceo_report = {
            "status": "error",
            "error_message": str(e),
            "analysis": f"[FOUNDER CEO ERROR] Founder CEO failed to synthesize decisions: {str(e)}",
            "recommendation": deterministic_decision,
            "confidence": 0,
            "dialogue": "The executive session could not synthesize a final decision due to a system error.",
            "data_verified": False,
            "validation_roadmap": [
                "1. Investigate and resolve the backend execution error.",
                "2. Re-run the Founder CEO synthesis session once resolved.",
                "3. Perform manual primary customer interviews independently."
            ]
        }
        
    if "status" not in founder_ceo_report:
        founder_ceo_report["status"] = "success" if evidence_quality["is_complete"] else "data_unavailable"
        
    raw_ceo_decision = str(founder_ceo_report.get("recommendation", deterministic_decision)).upper()
    
    # 7. FOUNDER CEO SAFETY & DISCREPANCY CHECK
    # Founder CEO LLM must NOT silently override the deterministic decision engine!
    discrepancies = []
    if raw_ceo_decision != deterministic_decision:
        disc_msg = (
            f"DISCREPANCY DETECTED: Founder CEO LLM recommended '{raw_ceo_decision}', "
            f"which contradicts the deterministic policy engine evaluation '{deterministic_decision}'. "
            f"Safety override engaged: preserving deterministic decision '{deterministic_decision}' as the authoritative final verdict."
        )
        print(f"[SAFETY OVERRIDE] {disc_msg}")
        discrepancies.append({
            "type": "DECISION_OVERRIDE_PREVENTED",
            "llm_recommendation": raw_ceo_decision,
            "deterministic_decision": deterministic_decision,
            "details": disc_msg
        })
        founder_ceo_report["recommendation"] = deterministic_decision
        
    final_decision = deterministic_decision
    specialist_reports["FOUNDER_CEO"] = founder_ceo_report
    
    # 8. Compute Mathematically Sound Confidence Score
    confidence_data = compute_deterministic_confidence(
        evidence_quality=evidence_quality,
        vote_distribution=vote_distribution,
        blockers=critical_blockers,
        rules_passed=rules_passed,
        total_rules=total_rules,
        final_recommendation=final_decision
    )
    final_confidence = confidence_data["final_confidence"]
    
    ceo_dialogue_msg = {
        "agent_id": "FOUNDER_CEO",
        "name": "Founder CEO",
        "icon": "👑",
        "color": "#FFD700",
        "role": "Venture Synthesis & Go/No-Go Decision",
        "status": founder_ceo_report.get("status", "success"),
        "error_message": founder_ceo_report.get("error_message"),
        "recommendation": final_decision,
        "confidence": final_confidence,
        "dialogue": founder_ceo_report.get("dialogue", ""),
        "analysis": founder_ceo_report.get("analysis", ""),
        "data_verified": evidence_quality["is_complete"],
        "validation_roadmap": founder_ceo_report.get("validation_roadmap", [])
    }
    transcript.append(ceo_dialogue_msg)
    
    if progress_callback:
        progress_callback("FOUNDER_CEO", "COMPLETED", ceo_dialogue_msg, consensus_metrics)
        
    # 9. Compile Decision Explanation Payload
    decision_explanation = {
        "final_decision": final_decision,
        "confidence": final_confidence,
        "policy_rationale": deterministic_rationale,
        "strongest_positive_evidence": [
            f"{a['name']}: {specialist_reports[a['id']].get('key_finding') or specialist_reports[a['id']].get('strongest_evidence', '')}"
            for a in TRACK_B_AGENTS if str(specialist_reports.get(a['id'], {}).get("recommendation", "")).upper() in ["YES", "LAUNCH"]
        ] or ["No unanimous positive signals detected."],
        "strongest_negative_evidence": [
            f"{a['name']}: {specialist_reports[a['id']].get('primary_concern', '')}"
            for a in TRACK_B_AGENTS if str(specialist_reports.get(a['id'], {}).get("recommendation", "")).upper() in ["NO", "DO NOT LAUNCH"]
        ] or ["No outright blocker votes from specialists."],
        "most_important_risk": risk_matrix[0]["rationale"] if risk_matrix else "Macro and operational stability require validation.",
        "capital_consideration": specialist_reports.get("CAPITAL_STRATEGIST", {}).get("analysis", "Budget alignment with venture benchmarks."),
        "data_quality_consideration": evidence_quality["status_label"]
    }
    
    # 10. Dataset Provenance Records & Integrity Check
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    dataset_checksums = {
        "research_data.csv": compute_dataset_hash(os.path.join(data_dir, "research_data.csv")),
        "competition_data.csv": compute_dataset_hash(os.path.join(data_dir, "competition_data.csv")),
        "legal_data.csv": compute_dataset_hash(os.path.join(data_dir, "legal_data.csv")),
        "market_data.csv": compute_dataset_hash(os.path.join(data_dir, "market_data.csv")),
        "risk_data.csv": compute_dataset_hash(os.path.join(data_dir, "risk_data.csv"))
    }
    
    dataset_provenance_records = {
        fn: get_dataset_provenance_record(fn, custom_data_dir=data_dir)
        for fn in ["research_data.csv", "competition_data.csv", "legal_data.csv", "market_data.csv", "risk_data.csv"]
    }
    
    # Run Claim Validation Audit across all claims in the session
    claim_validator = ClaimValidator(evidence_ledger)
    claim_validation_audit = claim_validator.validate_session_claims(specialist_reports, founder_ceo_report)
    
    audit_metadata = {
        "timestamp": time.time(),
        "app_version": APP_VERSION,
        "decision_engine_version": ENGINE_VERSION,
        "dataset_checksums": dataset_checksums,
        "dataset_provenance": dataset_provenance_records,
        "specialists_evaluated": 6,
        "deterministic_engine_reproducible": True,
        "target_country_verified": evidence_quality["verified"] > 0,
        "claim_traceability_percent": claim_validation_audit["claim_traceability_percent"],
        "dataset_coverage_percent": claim_validation_audit["dataset_coverage_percent"],
        "decision_critical_coverage_percent": claim_validation_audit["decision_critical_coverage_percent"]
    }
    
    # 11. Compile Canonical BoardRoomResult
    results = {
        "mode": "launch",
        "status": "error" if evidence_quality["errors"] > 0 else ("success" if evidence_quality["is_complete"] else "data_unavailable"),
        "business_idea": business_idea,
        "company": business_idea,
        "target_market": target_market,
        "market": target_market,
        "capital_budget": capital_budget,
        "budget": capital_budget,
        "timeline": timeline,
        "strategic_question": strategic_question,
        "question": strategic_question,
        "timestamp": audit_metadata["timestamp"],
        "specialist_reports": specialist_reports,
        "board_reports": specialist_reports,
        "transcript": transcript,
        "consensus_metrics": consensus_metrics,
        "opportunity_score": consensus_metrics.get("opportunity_score", 0),
        "risk_mitigation_score": consensus_metrics.get("risk_mitigation_score", risk_mitigation_data["risk_mitigation_score"]),
        "launch_readiness_score": consensus_metrics.get("launch_readiness_score", 0),
        "capital_feasibility_score": consensus_metrics.get("capital_feasibility_score", 0),
        "market_readiness": consensus_metrics.get("market_readiness", 0),
        "financial_feasibility": consensus_metrics.get("financial_feasibility", 0),
        "overall_launch_score": consensus_metrics.get("overall_launch_score", 0),
        "risk_mitigation_breakdown": risk_mitigation_data,
        "risk_mitigation_drivers": risk_mitigation_data.get("drivers", []),
        "risk_mitigation_audit": risk_mitigation_data.get("audit_steps", []),
        "founder_ceo_report": founder_ceo_report,
        "final_recommendation": final_decision,
        "final_decision": final_decision,
        "ceo_decision": final_decision,
        "deterministic_decision": deterministic_decision,
        "ceo_confidence": founder_ceo_report.get("confidence", final_confidence),
        "deterministic_confidence": final_confidence,
        "confidence": final_confidence,
        "confidence_breakdown": confidence_data,
        "confidence_semantics": confidence_data.get("confidence_semantics_explanation", "Confidence in the decision given evidence coverage, specialist agreement, and rule satisfaction (not a predictive success probability)."),
        "ceo_rationale": founder_ceo_report.get("analysis", deterministic_rationale),
        "validation_roadmap": founder_ceo_report.get("validation_roadmap", []),
        "data_verified": evidence_quality["is_complete"],
        "data_verified_overall": evidence_quality["is_complete"],
        "evidence_quality": evidence_quality,
        "dataset_coverage_percent": claim_validation_audit["dataset_coverage_percent"],
        "claim_traceability_percent": claim_validation_audit["claim_traceability_percent"],
        "decision_critical_coverage_percent": claim_validation_audit["decision_critical_coverage_percent"],
        "board_agreement": agreement_analysis,
        "agreement_analysis": agreement_analysis,
        "specialist_votes": vote_distribution,
        "evidence_ledger": evidence_ledger,
        "risk_matrix": risk_matrix,
        "critical_blockers": critical_blockers,
        "validation_gates": validation_gates,
        "executive_action_plan": executive_action_plan,
        "mind_change_thresholds": mind_change_thresholds,
        "disagreements": disagreements,
        "discrepancies": discrepancies,
        "decision_explanation": decision_explanation,
        "rule_evaluations": rule_evaluations,
        "deterministic_eval": deterministic_eval,
        "audit_metadata": audit_metadata,
        "dataset_provenance_records": dataset_provenance_records,
        "claim_validation_audit": claim_validation_audit,
        "claim_validation_summary": claim_validation_audit,
        "confidence_details": confidence_data,
        "reproducible_calculations": claim_validation_audit["reproducible_calculations"]
    }
    
    # Generate decision trace for auditability and step 8 compatibility
    results["decision_trace"] = compile_decision_trace(results)
    
    # 12. Run Pre-Render Consistency Validation
    is_valid, validation_errors = validate_consistency(results)
    if not is_valid:
        print(f"[TRACK B WARNING] Consistency validation flagged items: {validation_errors}")
        results["consistency_warnings"] = validation_errors
        
    print(f"[TRACK B] Simulation complete. Deterministic Final Decision: {final_decision} (Confidence: {final_confidence}%)\n")
    return results

def analyze_board_agreement(specialist_reports: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility helper to analyze board agreement."""
    yes_count = 0
    no_count = 0
    maybe_count = 0
    verified_count = 0
    data_unavailable_count = 0
    error_count = 0
    
    for rep in specialist_reports.values():
        rec = str(rep.get("recommendation", "")).upper()
        if rec in ["YES", "LAUNCH"]:
            yes_count += 1
        elif rec in ["NO", "DO NOT LAUNCH"]:
            no_count += 1
        else:
            maybe_count += 1
            
        status = rep.get("status", "success")
        is_ver = rep.get("data_verified", False)
        if status == "error":
            error_count += 1
        elif status == "data_unavailable" or not is_ver:
            data_unavailable_count += 1
        else:
            verified_count += 1
            
    is_reliable = (error_count == 0 and data_unavailable_count == 0)
    return {
        "yes_count": yes_count,
        "no_count": no_count,
        "maybe_count": maybe_count,
        "verified_count": verified_count,
        "data_unavailable_count": data_unavailable_count,
        "error_count": error_count,
        "is_reliable": is_reliable
    }

def detect_board_disagreements(specialist_reports: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility helper to detect pairwise specialist disagreements."""
    disagreements = []
    reps = list(specialist_reports.items())
    for i in range(len(reps)):
        k_a, rep_a = reps[i]
        rec_a = str(rep_a.get("recommendation", "")).upper()
        name_a = rep_a.get("name", k_a.replace("_", " ").title())
        for j in range(i + 1, len(reps)):
            k_b, rep_b = reps[j]
            rec_b = str(rep_b.get("recommendation", "")).upper()
            name_b = rep_b.get("name", k_b.replace("_", " ").title())
            if (rec_a == "YES" and rec_b == "NO") or (rec_a == "NO" and rec_b == "YES"):
                disagreements.append({
                    "agent_a": name_a,
                    "vote_a": rec_a,
                    "finding_a": rep_a.get("key_finding") or rep_a.get("strongest_evidence", ""),
                    "agent_b": name_b,
                    "vote_b": rec_b,
                    "concern_b": rep_b.get("primary_concern", ""),
                    "description": f"Direct conflict between {name_a} ({rec_a}) and {name_b} ({rec_b})."
                })
    has_disagreement = len(disagreements) > 0
    return {
        "has_disagreement": has_disagreement,
        "disagreements": disagreements,
        "aligned_message": "✓ SPECIALISTS ARE BROADLY ALIGNED" if not has_disagreement else "⚠ BOARD DISAGREEMENT DETECTED"
    }

def extract_critical_blockers(specialist_reports: Dict[str, Any], capital_budget: Any = 0, timeline: str = "", target_market: str = "") -> List[Dict[str, Any]]:
    """Compatibility helper to extract structured critical blockers."""
    return build_critical_blockers(specialist_reports)

def extract_mind_change_thresholds(specialist_reports: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compatibility helper to classify mind-change thresholds."""
    return classify_mind_change_thresholds(specialist_reports)

def generate_decision_explanation(final_recommendation: str, consensus_metrics: Any, agreement_analysis: Any, specialist_reports: Dict[str, Any], founder_ceo_report: Dict[str, Any], critical_blockers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compatibility helper to generate decision explanation."""
    return {
        "final_decision": final_recommendation,
        "confidence": founder_ceo_report.get("confidence", 0),
        "policy_rationale": founder_ceo_report.get("analysis", ""),
        "strongest_positive_evidence": [
            f"{a['name']}: {specialist_reports[a['id']].get('key_finding') or specialist_reports[a['id']].get('strongest_evidence', '')}"
            for a in TRACK_B_AGENTS if a['id'] in specialist_reports and str(specialist_reports[a['id']].get("recommendation", "")).upper() in ["YES", "LAUNCH"]
        ] or ["No unanimous positive signals detected."],
        "strongest_negative_evidence": [
            f"{a['name']}: {specialist_reports[a['id']].get('primary_concern', '')}"
            for a in TRACK_B_AGENTS if a['id'] in specialist_reports and str(specialist_reports[a['id']].get("recommendation", "")).upper() in ["NO", "DO NOT LAUNCH"]
        ] or ["No outright blocker votes from specialists."],
        "most_important_risk": "Execution risks and market validation gates must be resolved before proceeding.",
        "capital_consideration": specialist_reports.get("CAPITAL_STRATEGIST", {}).get("analysis", "Budget alignment with venture benchmarks."),
        "data_quality_consideration": "Dataset verified" if (agreement_analysis.get("verified_count", 0) == 6 if isinstance(agreement_analysis, dict) else False) else "Data gaps require validation"
    }

def compile_decision_trace(results: Dict[str, Any]) -> Dict[str, Any]:
    """Compile a 5-step traceable audit decision trace dictionary with dual-compatibility."""
    specialist_reports = results.get("specialist_reports", {})
    specialist_findings = []
    for aid, rep in specialist_reports.items():
        if aid == "FOUNDER_CEO":
            continue
        specialist_findings.append({
            "name": rep.get("name", aid.replace("_", " ").title()),
            "recommendation": rep.get("recommendation", "N/A"),
            "confidence": rep.get("confidence", 0),
            "data_verified": rep.get("data_verified", False),
            "key_finding": rep.get("key_finding") or rep.get("strongest_evidence") or rep.get("primary_concern", "")
        })
    
    votes = results.get("specialist_votes", {})
    if isinstance(votes, dict) and "yes_count" in votes:
        votes_dict = {"YES": votes.get("yes_count", 0), "MAYBE": votes.get("maybe_count", 0), "NO": votes.get("no_count", 0)}
    elif isinstance(votes, dict):
        votes_dict = votes
    else:
        votes_dict = {"YES": 0, "MAYBE": 0, "NO": 0}
        
    eq = results.get("evidence_quality", {})
    dq_dict = {
        "verified_specialists": eq.get("verified", 0),
        "total_specialists": eq.get("specialists_total", 6),
        "coverage_percent": eq.get("coverage_percent", 0),
        "errors": eq.get("errors", 0)
    }
    
    stages_list = [
        {
            "stage": "VENTURE_INPUT",
            "label": "Venture Parameters Ingested",
            "status": "PASS",
            "details": f"Market: {results.get('target_market')}, Budget: ${float(results.get('capital_budget', 0) or 0):,.0f}, Timeline: {results.get('timeline')}"
        },
        {
            "stage": "DATA_GROUNDING",
            "label": "Empirical Dataset Grounding",
            "status": "PASS" if eq.get("is_complete") else "CONDITIONAL",
            "details": f"{eq.get('verified', 0)}/{eq.get('specialists_total', 6)} datasets verified. Coverage: {eq.get('coverage_percent', 0)}%"
        },
        {
            "stage": "SPECIALIST_VOTES",
            "label": "Board Specialist Deliberation",
            "status": "PASS",
            "details": f"YES: {votes_dict.get('YES', 0)}, MAYBE: {votes_dict.get('MAYBE', 0)}, NO: {votes_dict.get('NO', 0)}"
        },
        {
            "stage": "DETERMINISTIC_RULES",
            "label": "Deterministic Policy Evaluation",
            "status": "PASS" if results.get("final_decision") in ["PROCEED", "LAUNCH"] else "REJECTED",
            "details": f"Policy Verdict: {results.get('final_decision', 'N/A')}"
        },
        {
            "stage": "FOUNDER_CEO_SYNTHESIS",
            "label": "Executive Synthesis & Audit Seal",
            "status": "PASS",
            "details": f"Final Decision: {results.get('final_decision')} (Deterministic Confidence: {results.get('confidence')}%)"
        }
    ]
    
    return {
        "user_input": {
            "business_idea": results.get("business_idea", ""),
            "target_market": results.get("target_market", ""),
            "capital_budget": results.get("capital_budget", 0),
            "timeline": results.get("timeline", ""),
            "strategic_question": results.get("strategic_question", "")
        },
        "data_quality": dq_dict,
        "specialist_findings": specialist_findings,
        "specialist_votes": votes_dict,
        "ceo_synthesis": {
            "decision": results.get("final_decision", ""),
            "confidence": results.get("confidence", 0),
            "rationale": results.get("policy_rationale") or results.get("ceo_rationale", "")
        },
        "stages": stages_list
    }

def run_strategic_session(mode: str, **kwargs) -> Dict[str, Any]:
    """
    Unified Strategic Decision Dispatcher:
    - mode == 'expansion': routes to Track A (run_boardroom_session)
    - mode == 'launch': routes to Track B (run_track_b_session)
    """
    if mode == "expansion":
        company = kwargs.get("company") or kwargs.get("company_name", "")
        market = kwargs.get("market") or kwargs.get("target_market", "")
        budget = kwargs.get("budget") or kwargs.get("capital_budget", 0)
        timeline = kwargs.get("timeline", "")
        question = kwargs.get("question") or kwargs.get("strategic_question", "")
        progress_callback = kwargs.get("progress_callback", None)
        return run_boardroom_session(
            company=company,
            market=market,
            budget=budget,
            timeline=timeline,
            question=question,
            progress_callback=progress_callback
        )
    elif mode == "launch":
        business_idea = kwargs.get("business_idea") or kwargs.get("company", "")
        target_market = kwargs.get("target_market") or kwargs.get("market", "")
        capital_budget = kwargs.get("capital_budget") or kwargs.get("budget", 0)
        timeline = kwargs.get("timeline", "")
        strategic_question = kwargs.get("strategic_question") or kwargs.get("question", "")
        progress_callback = kwargs.get("progress_callback", None)
        return run_track_b_session(
            business_idea=business_idea,
            target_market=target_market,
            capital_budget=capital_budget,
            timeline=timeline,
            strategic_question=strategic_question,
            progress_callback=progress_callback
        )
    else:
        raise ValueError(f"Invalid mode: '{mode}'. Must be 'expansion' or 'launch'.")
