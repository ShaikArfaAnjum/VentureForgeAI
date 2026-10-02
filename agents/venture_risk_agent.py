from config import call_groq_api
from services.data_service import get_data

def format_budget(budget):
    """Formats numeric budget values into clear human-readable USD strings."""
    if isinstance(budget, (int, float)):
        if budget >= 1_000_000:
            return f"${budget / 1_000_000:.2f} Million USD"
        elif budget >= 1_000:
            return f"${budget:,.0f} USD"
        else:
            return f"${budget} Million USD"
    return str(budget)

def assess_venture_risk(business_idea, target_market, capital_budget, timeline, strategic_question):
    """
    Venture Risk Officer: Assesses country-level sovereign risk, macroeconomic volatility,
    and institutional hazards for a first-time founder entering with no established local presence.
    Uses data/risk_data.csv (Fragility Score, Global Rank, Security Apparatus, Economy, State Legitimacy).
    """
    budget_str = format_budget(capital_budget)
    
    # Pull real Fragile States Index data for the target market
    risk_result = get_data("Risk Data", Country=target_market)
    
    if risk_result["status"] == "success":
        rd = risk_result["data"]
        frag_score = rd.get('Fragility Score', rd.get('Total', 'N/A'))
        rank = rd.get('Rank', 'N/A')
        sec = rd.get('C1: Security Apparatus', 'N/A')
        econ = rd.get('E1: Economy', 'N/A')
        legit = rd.get('P1: State Legitimacy', 'N/A')
        
        real_data_block = (
            f"REAL DATA CONTEXT (Fragile States Index dataset — cite these figures):\n"
            f"- {target_market} Fragility Score: {frag_score}/120 (higher = higher country risk; <50 = highly stable)\n"
            f"- Global Fragility Rank: {rank}\n"
            f"- Economic Vulnerability Score: {econ}/10\n"
            f"- Security Apparatus Risk Score: {sec}/10\n"
            f"- State Legitimacy Risk Score: {legit}/10\n"
        )
        data_verified = True
    else:
        real_data_block = (
            f"REAL DATA CONTEXT: No verified Fragile States Index entry found for '{target_market}' on disk. "
            f"State clearly that empirical sovereign fragility indices are unlisted and evaluate macroeconomic risk conservatively.\n"
        )
        data_verified = False

    system_prompt = (
        "You are an elite Startup Venture Risk Officer in a boardroom. "
        "Your role is to assess country-level risks—geopolitical fragility, currency fluctuation, economic vulnerability, "
        "and legal stability—specifically from the perspective of an early-stage founder with no local parent company, "
        "no local network, and high vulnerability to macro shocks. "
        "Ground your evaluation strictly in the Fragile States Index dataset. Do NOT invent risks unsupported by data. "
        "Keep your written analysis to 3-4 professional, dense sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    prompt = f"""
    {real_data_block}
    
    Evaluate sovereign venture risks for launching a new business in {target_market}.
    
    Business Idea: "{business_idea}"
    Target Market / Country: {target_market}
    Proposed Launch Budget: {budget_str}
    Execution Timeline: {timeline}
    Strategic Founder Question: "{strategic_question}"
    
    Conduct a venture risk audit and output a JSON response containing:
    1. 'analysis': A detailed 3-4 sentence domain analysis evaluating country fragility, currency volatility, institutional risk, and vulnerability of '{business_idea}' as a new entrant. Reference the REAL DATA CONTEXT above where relevant (cite the Fragility Score, rank, and economic score).
    2. 'key_finding': A concise single-sentence summary of your sovereign and venture risk verdict.
    3. 'strongest_evidence': The primary empirical risk indicator cited.
    4. 'primary_concern': The single biggest macroeconomic, currency, or stability risk.
    5. 'recommendation': 'YES', 'NO', or 'MAYBE' based on venture safety and risk exposure.
    6. 'confidence': An integer between 0 and 100 representing data confidence.
    7. 'dialogue': A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'From a venture risk perspective in...') summarizing your takeaway.
    8. 'data_verified': boolean ({'true' if data_verified else 'false'}).
    9. 'mind_change_threshold': A single sentence stating what specific macroeconomic or geopolitical risk trigger would change your recommendation.
    
    JSON Schema:
    {{
      "analysis": "string",
      "key_finding": "string",
      "strongest_evidence": "string",
      "primary_concern": "string",
      "recommendation": "YES" | "NO" | "MAYBE",
      "confidence": integer,
      "dialogue": "string",
      "data_verified": boolean,
      "mind_change_threshold": "string"
    }}
    """
    
    res = call_groq_api(
        prompt=prompt,
        system_prompt=system_prompt,
        response_format={"type": "json_object"},
        agent_role="VENTURE_RISK",
        company=business_idea,
        market=target_market,
        budget=capital_budget,
        timeline=timeline,
        question=strategic_question,
        grounding_data=risk_result
    )
    res["data_verified"] = data_verified
    if "status" not in res:
        if "[API FAILURE]" in res.get("analysis", "") or "[PARSING ERROR]" in res.get("analysis", ""):
            res["status"] = "error"
            res["error_message"] = res.get("analysis")
        elif data_verified:
            res["status"] = "success"
        else:
            res["status"] = "data_unavailable"
    if "key_finding" not in res or not res.get("key_finding"):
        res["key_finding"] = res.get("analysis", "")[:120] + "..." if len(res.get("analysis", "")) > 120 else res.get("analysis", "Sovereign venture risk evaluated.")
    if "strongest_evidence" not in res or not res.get("strongest_evidence"):
        res["strongest_evidence"] = f"Fragile States Index for {target_market}" if data_verified else "General macroeconomic stability indicators"
    if "primary_concern" not in res or not res.get("primary_concern"):
        res["primary_concern"] = "Macroeconomic volatility and lack of local institutional backing."
    if "mind_change_threshold" not in res or not res.get("mind_change_threshold"):
        res["mind_change_threshold"] = "Verification of stable local banking rails and currency convertibility by a Tier-1 institution would shift this risk recommendation."
    return res
