from config import call_groq_api, format_budget_display, parse_budget_numeric
from services.data_service import get_data

def analyze_risk(company, market, budget, timeline, question, business_model=""):
    """
    Risk Agent: Evaluates market volatility, currency, geopolitical risk, and operational vulnerabilities.
    """
    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    # Pull real Fragile States Index data for the target market/country
    risk_result = get_data("Risk Data", Country=market)
    
    if risk_result["status"] == "success":
        rd = risk_result["data"]
        frag_score = rd.get('Fragility Score', rd.get('Total', 'N/A'))
        real_data_block = (
            f"REAL DATA CONTEXT (Fragile States Index dataset — cite these figures):\n"
            f"- {market} Fragility Score: {frag_score}/120 (higher = more fragile/risky; under 50 = highly stable)\n"
            f"- {market} Global Fragility Rank: {rd.get('Rank', 'N/A')}\n"
            f"- Security Apparatus Risk Score: {rd.get('C1: Security Apparatus', 'N/A')}/10\n"
            f"- Economic Vulnerability Score: {rd.get('E1: Economy', 'N/A')}/10\n"
            f"- State Legitimacy Score: {rd.get('P1: State Legitimacy', 'N/A')}/10\n"
        )
    else:
        real_data_block = "REAL DATA CONTEXT: No verified Fragile States Index data found for this market — reason from general knowledge, but note this is an estimate.\n"

    system_prompt = (
        "You are a conservative Chief Risk Officer (CRO). Your role is to examine geopolitical factors, "
        "currency exchange volatility, inflation/macroeconomic stability, asset protection, and concentration risks for the enterprise. "
        "You are highly analytical, security-conscious, and prepare for worst-case scenarios. "
        "Keep your written analysis to 3-4 professional, dense sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    bm_str = f"\nBusiness Model / Target Customer Context: {business_model}" if business_model else ""
    
    prompt = f"""
    {real_data_block}
    
    Analyze the strategic risks, geopolitical issues, currency exposures, and market volatility for {company} entering the {market} market.{bm_str}
    Proposed Capital Allocation: {budget_display}
    Target Timeline: {timeline}
    Strategic Question: "{question}"
    
    Conduct a risk matrix assessment and output a JSON response containing:
    1. A detailed 3-4 sentence domain analysis detailing currency volatility, political risks, concentration hazards, and mitigation requirements for {company} in {market}.
    2. A recommendation of 'YES', 'NO', or 'MAYBE' based on risk exposure safety.
    3. A confidence score between 0 and 100 representing the certainty of your risk assessment.
    4. A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'From a comprehensive risk matrix standpoint...') that summarizes your core risk takeaway.
    5. A concise key finding (1 sentence).
    6. A primary concern (1 sentence).
    7. A mind-change threshold (what risk reduction would change your recommendation).
    
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
        agent_role="RISK",
        company=company,
        market=market,
        budget=budget_usd,
        timeline=timeline,
        question=question,
        grounding_data=risk_result
    )