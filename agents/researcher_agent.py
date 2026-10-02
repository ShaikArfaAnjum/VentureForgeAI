from config import call_groq_api, format_budget_display, parse_budget_numeric
from services.data_service import get_data

def analyze_market(company, market, budget, timeline, question, business_model=""):
    """
    Market Researcher: Analyzes market size, TAM, growth rate, segments, and trends.
    """
    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    # Pull real startup ecosystem funding data for the target market
    research_result = get_data("Research Data", Country=market)
    
    if research_result["status"] == "success":
        rd = research_result["data"]
        real_data_block = (
            f"REAL DATA CONTEXT (regional enterprise/startup ecosystem funding data — use as macro context, do not contradict it):\n"
            f"- Tracked enterprises/startups in {market}: {rd.get('Startups Tracked', 'N/A')}\n"
            f"- Total sector venture funding: ${rd.get('Total Funding (USD)', 'N/A')}\n"
            f"- Average funding per enterprise: ${rd.get('Average Funding per Startup (USD)', 'N/A')}\n"
        )
    else:
        real_data_block = "REAL DATA CONTEXT: No verified sector ecosystem data found for this market — reason from domain knowledge, noting this is an estimate.\n"

    system_prompt = (
        "You are an elite Chief Market Research Officer (CMRO). Your role is to evaluate the market size, "
        "Total Addressable Market (TAM), projected compound annual growth rate (CAGR), and customer segments. "
        "You speak with data-driven precision, and your insights are grounded in market analytics. "
        "Keep your written analysis to 3-4 professional, dense sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    bm_str = f"\nBusiness Model / Target Customer Context: {business_model}" if business_model else ""
    
    prompt = f"""
    {real_data_block}
    
    Analyze the strategic entry into the {market} market for {company}.{bm_str}
    Proposed Capital Allocation: {budget_display}
    Target Timeline: {timeline}
    Strategic Question: "{question}"
    
    Conduct a market research audit and output a JSON response containing:
    1. A detailed 3-4 sentence domain analysis detailing market size, TAM, growth rate, customer segments, and demand viability for {company} in {market}.
    2. A recommendation of 'YES', 'NO', or 'MAYBE' based on demand viability.
    3. A confidence score between 0 and 100 representing the certainty of your data.
    4. A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'Looking at the TAM of...') that summarizes your core takeaway.
    5. A concise key finding (1 sentence).
    6. A primary concern (1 sentence).
    7. A mind-change threshold (what empirical evidence would change your recommendation).
    
    JSON Schema:
    {{
      "analysis": "string",
      "recommendation": "YES" | "NO" | "MAYBE",
      "confidence": integer,
      "dialogue": "string",
      "key_finding": "string",
      "primary_concern": "string",
      "mind_change_threshold": "string"
    }}
    """
    
    return call_groq_api(
        prompt=prompt,
        system_prompt=system_prompt,
        response_format={"type": "json_object"},
        agent_role="RESEARCHER",
        company=company,
        market=market,
        budget=budget_usd,
        timeline=timeline,
        question=question,
        grounding_data=research_result
    )