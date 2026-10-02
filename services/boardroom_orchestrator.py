import time
from agents.researcher_agent import analyze_market
from agents.competitor_agent import analyze_competition
from agents.legal_agent import analyze_legal
from agents.operations_agent import analyze_operations
from agents.risk_agent import analyze_risk
from agents.cfo_agent import analyze_finance
from agents.ceo_agent import analyze_ceo
from services.consensus_engine import calculate_consensus
from services.data_service import get_data
from services.expansion_decision_engine import evaluate_expansion_decision
from services.expansion_canonical_result import (
    build_expansion_canonical_result,
    get_expansion_evidence_quality,
    build_expansion_critical_blockers
)
from config import parse_budget_numeric, format_budget_display

# List of the 6 core agents, their display names, colors, and executive roles
CORE_AGENTS = [
    {
        "id": "RESEARCHER",
        "name": "Market Researcher",
        "icon": "🔵",
        "color": "#00D4FF", # Cyan
        "function": analyze_market
    },
    {
        "id": "COMPETITOR",
        "name": "Competitive Intelligence",
        "icon": "🟡",
        "color": "#FFB800", # Gold
        "function": analyze_competition
    },
    {
        "id": "LEGAL",
        "name": "General Counsel",
        "icon": "⚖️",
        "color": "#9E9E9E", # Gray
        "function": analyze_legal
    },
    {
        "id": "OPERATIONS",
        "name": "Chief Operating Officer",
        "icon": "⚙️",
        "color": "#00FF88", # Green
        "function": analyze_operations
    },
    {
        "id": "RISK",
        "name": "Chief Risk Officer",
        "icon": "🔴",
        "color": "#FF6B6B", # Red
        "function": analyze_risk
    },
    {
        "id": "CFO",
        "name": "Chief Financial Officer",
        "icon": "💰",
        "color": "#FFD700", # Gold
        "function": analyze_finance
    }
]

def run_boardroom_session(company, market, budget, timeline, question, progress_callback=None, business_model=""):
    """
    Executes the full Track A Corporate Expansion boardroom session from inputs to deterministic decision.
    Runs each core agent, triggers the consensus engine, evaluates deterministic expansion rules,
    invokes CEO synthesis, and builds the single-source-of-truth canonical BoardRoomResult.
    """
    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    print(f"\n[TRACK A] ========================================================")
    print(f"[TRACK A] Input received:")
    print(f"  Company: '{company}'")
    print(f"  Target Market: '{market}'")
    print(f"  Budget: {budget_display} (${budget_usd:,.0f} USD)")
    print(f"  Timeline: '{timeline}'")
    print(f"  Strategic Question: '{question[:80]}...'")
    if business_model:
        print(f"  Business Model: '{business_model}'")
    print(f"[TRACK A] ========================================================\n")
    
    # Ingest grounding facts for transparency
    grounding_facts = {
        "Research Data": get_data("Research Data", Country=market).get("data", {}),
        "Competition Data": get_data("Competition Data", Country=market).get("data", {}),
        "Legal Data": get_data("Legal Data", Country=market).get("data", {}),
        "Market Data": get_data("Market Data", Country=market).get("data", {}),
        "Risk Data": get_data("Risk Data", Country=market).get("data", {}),
        "Financial Data": get_data("Financial Data", Company=company).get("data", {})
    }
    
    board_reports = {}
    transcript = []
    
    # 1. Execute Core Specialist Agents
    for agent_info in CORE_AGENTS:
        agent_id = agent_info["id"]
        agent_name = agent_info["name"]
        
        print(f"[TRACK A] Executing {agent_name}...")
        
        if progress_callback:
            progress_callback(agent_id, "THINKING", None, None)
            
        agent_fn = agent_info["function"]
        report = agent_fn(
            company=company,
            market=market,
            budget=budget_usd,
            timeline=timeline,
            question=question,
            business_model=business_model
        )
        
        board_reports[agent_id] = report
        
        rec = report.get("recommendation", "MAYBE")
        conf = report.get("confidence", 75)
        print(f"[TRACK A] {agent_name} result: Vote={rec}, Confidence={conf}%")
        
        dialogue_msg = {
            "agent_id": agent_id,
            "name": agent_name,
            "icon": agent_info["icon"],
            "color": agent_info["color"],
            "recommendation": rec,
            "confidence": conf,
            "dialogue": report.get("dialogue", ""),
            "analysis": report.get("analysis", ""),
            "data_verified": report.get("data_verified", False),
            "mind_change_threshold": report.get("mind_change_threshold", ""),
            "key_finding": report.get("key_finding", report.get("analysis", "")[:120]),
            "primary_concern": report.get("primary_concern", "")
        }
        transcript.append(dialogue_msg)
        
        interim_consensus = calculate_consensus(board_reports)
        
        if progress_callback:
            progress_callback(agent_id, "COMPLETED", dialogue_msg, interim_consensus)
            
        time.sleep(0.3)
        
    # 2. Run Consensus & Deterministic Expansion Engine
    consensus_metrics = calculate_consensus(board_reports)
    evidence_quality = get_expansion_evidence_quality(board_reports)
    critical_blockers = build_expansion_critical_blockers(board_reports)
    
    vote_dist = {
        "YES": sum(1 for r in board_reports.values() if r.get("recommendation") in ["YES", "ENTER", "ENTER MARKET"]),
        "NO": sum(1 for r in board_reports.values() if r.get("recommendation") in ["NO", "REJECT", "REJECT EXPANSION"]),
        "MAYBE": sum(1 for r in board_reports.values() if r.get("recommendation") not in ["YES", "ENTER", "ENTER MARKET", "NO", "REJECT", "REJECT EXPANSION"])
    }
    
    print(f"[TRACK A] Running Deterministic Expansion Policy Evaluation...")
    deterministic_eval = evaluate_expansion_decision(
        company=company,
        target_market=market,
        budget=budget_usd,
        timeline=timeline,
        question=question,
        specialist_reports=board_reports,
        evidence_quality=evidence_quality,
        blockers=critical_blockers,
        vote_distribution=vote_dist,
        business_model=business_model
    )
    
    print(f"[TRACK A] Deterministic Decision: {deterministic_eval.get('decision')}")
    print(f"[TRACK A] Rules Passed: {deterministic_eval.get('rules_passed_count')}/9, Failed: {deterministic_eval.get('rules_failed_count')}/9")
    
    # 3. Execute Corporate CEO Agent for Synthesis
    if progress_callback:
        progress_callback("CEO", "THINKING", None, None)
        
    ceo_report = analyze_ceo(
        company=company,
        market=market,
        budget=budget_usd,
        timeline=timeline,
        question=question,
        board_reports=board_reports,
        business_model=business_model
    )
    
    board_reports["CEO"] = ceo_report
    
    ceo_dialogue_msg = {
        "agent_id": "CEO",
        "name": "Corporate CEO",
        "icon": "🎯",
        "color": "#FFD700",
        "recommendation": deterministic_eval.get("decision", ceo_report.get("recommendation", "ENTER MARKET")),
        "confidence": ceo_report.get("confidence", 85),
        "dialogue": ceo_report.get("dialogue", ""),
        "analysis": ceo_report.get("analysis", "")
    }
    transcript.append(ceo_dialogue_msg)
    
    if progress_callback:
        progress_callback("CEO", "COMPLETED", ceo_dialogue_msg, consensus_metrics)
        
    # 4. Assemble Single-Source-of-Truth Canonical BoardRoomResult
    canonical_result = build_expansion_canonical_result(
        company=company,
        market=market,
        budget=budget_usd,
        timeline=timeline,
        question=question,
        specialist_reports=board_reports,
        ceo_report=ceo_report,
        deterministic_eval=deterministic_eval,
        transcript=transcript,
        grounding_facts=grounding_facts,
        business_model=business_model
    )
    
    print(f"[TRACK A] Session Concluded. Final Canonical Decision: {canonical_result['final_decision']} ({canonical_result['confidence']}%)")
    
    return canonical_result

