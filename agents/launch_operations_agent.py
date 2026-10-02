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

def evaluate_launch_operations(business_idea, target_market, capital_budget, timeline, strategic_question):
    """
    Launch Operations: Evaluates whether a lean MVP-stage business with limited resources
    can realistically operate, establish logistics/supply channels, and launch in the target country.
    Uses data/market_data.csv (Logistics Performance Score 2023).
    """
    budget_str = format_budget(capital_budget)
    
    # Pull real World Bank Logistics Performance Index data
    market_result = get_data("Market Data", Country=target_market)
    
    if market_result["status"] == "success":
        md = market_result["data"]
        lpi_score = md.get('Logistics Performance Score (2023)', 'N/A')
        
        real_data_block = (
            f"REAL DATA CONTEXT (World Bank Logistics Performance Index — cite this metric):\n"
            f"- {target_market} Logistics Performance Score (2023): {lpi_score} / 5.0 "
            f"(measures customs efficiency, transport infrastructure quality, and delivery reliability)\n"
        )
        data_verified = True
    else:
        real_data_block = (
            f"REAL DATA CONTEXT: No verified Logistics Performance Score found for '{target_market}' on disk. "
            f"State clearly that logistics index data is unlisted and evaluate lean MVP execution from general operational principles.\n"
        )
        data_verified = False

    system_prompt = (
        "You are an elite Lean Startup Operations Officer and MVP Execution Lead in a boardroom. "
        "Your role is to evaluate whether a lean, early-stage venture with limited initial resources "
        "can execute its initial launch, manage distribution/delivery, acquire local talent, and build operational workflows. "
        "Do NOT assume enterprise-scale infrastructure. Focus on lean startup realities, asset-light execution, and speed. "
        "Keep your written analysis to 3-4 professional, dense sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    prompt = f"""
    {real_data_block}
    
    Evaluate lean MVP operational feasibility for launching a new business in {target_market}.
    
    Business Idea: "{business_idea}"
    Target Market / Country: {target_market}
    Proposed Launch Budget: {budget_str}
    Execution Timeline: {timeline}
    Strategic Founder Question: "{strategic_question}"
    
    Conduct an operational launch audit and output a JSON response containing:
    1. 'analysis': A detailed 3-4 sentence domain analysis evaluating lean MVP setup, distribution/logistics friction, staffing/talent access, and operational realism within {timeline}. Reference the REAL DATA CONTEXT above where relevant (cite the 2023 Logistics Performance Score).
    2. 'key_finding': A concise single-sentence summary of your MVP operational verdict.
    3. 'strongest_evidence': The primary empirical operational or logistics metric cited.
    4. 'primary_concern': The single biggest operational friction point or supply bottleneck.
    5. 'recommendation': 'YES', 'NO', or 'MAYBE' based on lean execution feasibility.
    6. 'confidence': An integer between 0 and 100 representing certainty.
    7. 'dialogue': A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'Assessing our lean MVP operations in...') summarizing your takeaway.
    8. 'data_verified': boolean ({'true' if data_verified else 'false'}).
    9. 'mind_change_threshold': A single sentence stating what operational milestone or vendor partnership would change your recommendation.
    
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
        agent_role="LAUNCH_OPERATIONS",
        company=business_idea,
        market=target_market,
        budget=capital_budget,
        timeline=timeline,
        question=strategic_question,
        grounding_data=market_result
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
        res["key_finding"] = res.get("analysis", "")[:120] + "..." if len(res.get("analysis", "")) > 120 else res.get("analysis", "MVP operational rollout evaluated.")
    if "strongest_evidence" not in res or not res.get("strongest_evidence"):
        res["strongest_evidence"] = f"Logistics Performance Score for {target_market}" if data_verified else "General regional infrastructure reliability"
    if "primary_concern" not in res or not res.get("primary_concern"):
        res["primary_concern"] = "Supply chain dependencies and local distribution scaling friction."
    if "mind_change_threshold" not in res or not res.get("mind_change_threshold"):
        res["mind_change_threshold"] = "Securing a binding SLA with a regional fulfillment or cloud infrastructure partner would alter this operational assessment."
    return res
