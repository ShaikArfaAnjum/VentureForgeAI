from config import call_groq_api, format_budget_display, parse_budget_numeric
from services.data_service import get_data

def analyze_operations(company, market, budget, timeline, question, business_model=""):
    """
    Operations Agent: Evaluates supply chain, staffing, execution feasibility, and physical/digital infrastructure.
    """
    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    # Pull real World Bank Logistics Performance Index data
    market_result = get_data("Market Data", Country=market)
    
    if market_result["status"] == "success":
        md = market_result["data"]
        real_data_block = (
            f"REAL DATA CONTEXT (World Bank Logistics Performance Index — cite these metrics):\n"
            f"- {market} Logistics Performance Score (2023): {md.get('Logistics Performance Score (2023)', 'N/A')} out of 5.0 "
            f"(higher = better customs clearance, transport infrastructure, and shipment reliability)\n"
        )
    else:
        real_data_block = "REAL DATA CONTEXT: No verified logistics performance data found for this market — reason from general knowledge, but note this is an estimate.\n"

    system_prompt = (
        "You are an elite Chief Operating Officer (COO). Your role is to examine the logistical feasibility of "
        "expansion, evaluate supply chain networks, distribution channels, staffing and local talent acquisition, "
        "physical/digital infrastructure requirements, and project schedule realism for the expanding enterprise. You are execution-oriented, practical, "
        "and deeply familiar with logistics. "
        "Keep your written analysis to 3-4 professional, dense sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    bm_str = f"\nBusiness Model / Target Customer Context: {business_model}" if business_model else ""
    
    prompt = f"""
    {real_data_block}
    
    Analyze the operational requirements, logistics, supply chain, staffing, and feasibility for {company} entering the {market} market.{bm_str}
    Proposed Capital Allocation: {budget_display}
    Target Timeline: {timeline}
    Strategic Question: "{question}"
    
    Conduct an operational audit and output a JSON response containing:
    1. A detailed 3-4 sentence domain analysis detailing infrastructure requirements, talent acquisition, supply chain stability, and schedule realism for {company} in {market}.
    2. A recommendation of 'YES', 'NO', or 'MAYBE' based on logistical feasibility.
    3. A confidence score between 0 and 100 representing the certainty of your operational assessment.
    4. A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'To address operational execution...') that summarizes your core logistical takeaway.
    5. A concise key finding (1 sentence).
    6. A primary concern (1 sentence).
    7. A mind-change threshold (what operational milestone would change your recommendation).
    
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
        agent_role="OPERATIONS",
        company=company,
        market=market,
        budget=budget_usd,
        timeline=timeline,
        question=question,
        grounding_data=market_result
    )