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

def validate_market(business_idea, target_market, capital_budget, timeline, strategic_question):
    """
    Market Validator: Evaluates whether the proposed business idea has startup ecosystem
    momentum, capital availability, and demand viability in the target country.
    Uses data/research_data.csv (Startups Tracked, Total Funding, Average Funding per Startup).
    """
    budget_str = format_budget(capital_budget)
    
    # Pull real startup ecosystem funding data for the target market
    research_result = get_data("Research Data", Country=target_market)
    
    if research_result["status"] == "success":
        rd = research_result["data"]
        startups = rd.get('Startups Tracked', 'N/A')
        total_funding = rd.get('Total Funding (USD)', 'N/A')
        avg_funding = rd.get('Average Funding per Startup (USD)', 'N/A')
        
        real_data_block = (
            f"REAL DATA CONTEXT (Startup ecosystem funding dataset — cite these empirical figures):\n"
            f"- Startups tracked in {target_market}: {startups}\n"
            f"- Total funding raised by startups in {target_market}: ${total_funding}\n"
            f"- Average funding per startup: ${avg_funding}\n"
        )
        data_verified = True
    else:
        real_data_block = (
            f"REAL DATA CONTEXT: No verified startup ecosystem funding dataset found for '{target_market}' on disk. "
            f"State clearly that empirical venture data is unavailable for this market and reason from general macroeconomic principles.\n"
        )
        data_verified = False

    system_prompt = (
        "You are an elite Market Validation Specialist and Venture Partner in a startup boardroom. "
        "Your role is to validate whether a brand-new business idea has market appetite, startup ecosystem momentum, "
        "and receptive customer segments in the target country. "
        "Ground your evaluation strictly in the empirical data provided. If data is unavailable, be transparent about limitations. "
        "Do NOT invent market statistics or claim certainty without evidence. "
        "Keep your written analysis to 3-4 professional, dense, and objective sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    prompt = f"""
    {real_data_block}
    
    Evaluate the venture launch feasibility for a new business idea entering {target_market}.
    
    Business Idea: "{business_idea}"
    Target Market / Country: {target_market}
    Proposed Launch Budget: {budget_str}
    Execution Timeline: {timeline}
    Strategic Founder Question: "{strategic_question}"
    
    Conduct a market validation assessment and output a JSON response containing:
    1. 'analysis': A detailed 3-4 sentence domain analysis evaluating startup ecosystem readiness, demand momentum, and compatibility of '{business_idea}' with {target_market}. Reference the REAL DATA CONTEXT above where relevant.
    2. 'key_finding': A concise single-sentence summary of your core validation takeaway.
    3. 'strongest_evidence': The primary empirical fact or metric supporting your view.
    4. 'primary_concern': The single biggest demand or adoption risk identified.
    5. 'recommendation': 'YES', 'NO', or 'MAYBE' based on demand and ecosystem viability.
    6. 'confidence': An integer between 0 and 100 representing data confidence.
    7. 'dialogue': A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'Reviewing startup ecosystem signals in...') summarizing your takeaway.
    8. 'data_verified': boolean ({'true' if data_verified else 'false'}).
    9. 'mind_change_threshold': A single sentence stating what specific empirical evidence or customer traction metric would change your recommendation.
    
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
        agent_role="MARKET_VALIDATOR",
        company=business_idea,
        market=target_market,
        budget=capital_budget,
        timeline=timeline,
        question=strategic_question,
        grounding_data=research_result
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
        res["key_finding"] = res.get("analysis", "")[:120] + "..." if len(res.get("analysis", "")) > 120 else res.get("analysis", "Market demand indicators evaluated.")
    if "strongest_evidence" not in res or not res.get("strongest_evidence"):
        res["strongest_evidence"] = f"Startup ecosystem activity in {target_market}" if data_verified else "General macroeconomic demand patterns"
    if "primary_concern" not in res or not res.get("primary_concern"):
        res["primary_concern"] = "Early-stage customer willingness-to-pay and initial adoption friction."
    if "mind_change_threshold" not in res or not res.get("mind_change_threshold"):
        res["mind_change_threshold"] = "A 30% shift in early-stage investment activity or verified customer waitlist signups would alter this recommendation."
    return res
