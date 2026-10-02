def calculate_consensus(board_reports):
    """
    Aggregates the individual recommendations and confidence scores of the 6 core agents
    to calculate 4 high-level strategic business metrics for Track A:
    - Opportunity Score: Market TAM capacity and competitor voids
    - Risk Mitigation Score: Deterministic risk coverage across legal, sovereign, financial, and operational vectors
    - Market Readiness: Research TAM, competitor voids, and legal compliance clearance
    - Financial Feasibility: CFO unit economics and operations execution cost feasibility
    """
    score_map = {
        "YES": 100.0,
        "ENTER": 100.0,
        "ENTER MARKET": 100.0,
        "LAUNCH": 100.0,
        "MAYBE": 50.0,
        "DELAY": 50.0,
        "DELAY ENTRY": 50.0,
        "VALIDATE": 50.0,
        "VALIDATE FIRST": 50.0,
        "NO": 0.0,
        "REJECT": 0.0,
        "REJECT EXPANSION": 0.0,
        "DO NOT LAUNCH": 0.0
    }
    
    # Extract reports with defaults if an agent fails
    researcher = board_reports.get("RESEARCHER", {"recommendation": "MAYBE", "confidence": 70})
    competitor = board_reports.get("COMPETITOR", {"recommendation": "MAYBE", "confidence": 70})
    legal = board_reports.get("LEGAL", {"recommendation": "MAYBE", "confidence": 70})
    operations = board_reports.get("OPERATIONS", {"recommendation": "MAYBE", "confidence": 70})
    risk = board_reports.get("RISK", {"recommendation": "MAYBE", "confidence": 70})
    cfo = board_reports.get("CFO", {"recommendation": "MAYBE", "confidence": 70})
    
    # 1. Opportunity Score (Based on Market Size/TAM and Competitive Gap)
    opp_res_score = score_map.get(str(researcher.get("recommendation", "MAYBE")).upper(), 50.0)
    opp_comp_score = score_map.get(str(competitor.get("recommendation", "MAYBE")).upper(), 50.0)
    res_conf = max(1, researcher.get("confidence", 70))
    comp_conf = max(1, competitor.get("confidence", 70))
    opp_weight = res_conf + comp_conf
    opportunity_score = int(
        ((opp_res_score * res_conf) + (opp_comp_score * comp_conf)) / opp_weight
    )
    
    # 2. Risk Mitigation Score (Deterministic risk coverage calculation)
    base_mitigation = 100.0
    risk_penalties = 0.0
    
    cro_rec = str(risk.get("recommendation", "MAYBE")).upper()
    leg_rec = str(legal.get("recommendation", "MAYBE")).upper()
    cfo_rec = str(cfo.get("recommendation", "MAYBE")).upper()
    ops_rec = str(operations.get("recommendation", "MAYBE")).upper()
    
    if cro_rec in ["NO", "REJECT", "REJECT EXPANSION"]:
        risk_penalties += 25.0
    elif cro_rec in ["MAYBE", "DELAY", "DELAY ENTRY"]:
        risk_penalties += 10.0
    else:
        risk_penalties += 2.0  # Baseline residual exposure
        
    if leg_rec in ["NO", "REJECT", "REJECT EXPANSION"]:
        risk_penalties += 22.0
    elif leg_rec in ["MAYBE", "DELAY", "DELAY ENTRY"]:
        risk_penalties += 8.0
        
    if cfo_rec in ["NO", "REJECT", "REJECT EXPANSION"]:
        risk_penalties += 15.0
    elif cfo_rec in ["MAYBE", "DELAY", "DELAY ENTRY"]:
        risk_penalties += 5.0
        
    if ops_rec in ["NO", "REJECT", "REJECT EXPANSION"]:
        risk_penalties += 12.0
    elif ops_rec in ["MAYBE", "DELAY", "DELAY ENTRY"]:
        risk_penalties += 4.0
        
    # Check data verification gaps
    all_reports = [researcher, competitor, legal, operations, risk, cfo]
    unverified = sum(1 for r in all_reports if not r.get("data_verified", False))
    errors = sum(1 for r in all_reports if r.get("status") == "error")
    
    risk_penalties += (unverified * 4.0) + (errors * 15.0)
    risk_mitigation_score = int(max(5, min(95, round(base_mitigation - risk_penalties))))
    
    # 3. Market Readiness (Combines research TAM, competitor voids, and legal clearance)
    leg_score = score_map.get(leg_rec, 50.0)
    leg_conf = max(1, legal.get("confidence", 70))
    readiness_weight = res_conf + comp_conf + leg_conf
    market_readiness = int(
        ((opp_res_score * res_conf) + 
         (opp_comp_score * comp_conf) + 
         (leg_score * leg_conf)) / readiness_weight
    )
    
    # 4. Financial Feasibility (CFO analysis + Operations execution cost feasibility)
    fin_cfo_score = score_map.get(cfo_rec, 50.0)
    fin_ops_score = score_map.get(ops_rec, 50.0)
    cfo_conf = max(1, cfo.get("confidence", 70))
    ops_conf = max(1, operations.get("confidence", 70))
    fin_weight = (cfo_conf * 1.5 + ops_conf)
    financial_feasibility = int(
        ((fin_cfo_score * cfo_conf * 1.5) + 
         (fin_ops_score * ops_conf)) / fin_weight
    )
    
    return {
        "opportunity_score": max(5, min(100, opportunity_score)),
        "risk_mitigation_score": max(5, min(100, risk_mitigation_score)),
        "market_readiness": max(5, min(100, market_readiness)),
        "financial_feasibility": max(5, min(100, financial_feasibility))
    }
