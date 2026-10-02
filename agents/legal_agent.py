from config import call_groq_api, format_budget_display, parse_budget_numeric
from services.data_service import get_data

def analyze_legal(company, market, budget, timeline, question, business_model=""):
    """
    Legal & Regulatory Counsel: Evaluates compliance, regulatory landscape, legal barriers, and contract risks.
    """
    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    # Pull real World Bank Ease of Doing Business & regulatory data
    legal_result = get_data("Legal Data", Country=market)
    if legal_result["status"] != "success":
        legal_result = get_data("Country Data", Country=market)
        
    if legal_result["status"] == "success":
        ld = legal_result["data"]
        ease_rank = ld.get('Ease of Doing Business Rank', 'N/A')
        ease_score = ld.get('Ease of Doing Business Score', 'N/A')
        enforce_score = ld.get('Enforcing Contracts Score', 'N/A')
        days_start = ld.get('Days to Start Business', 'N/A')
        region = ld.get('Region', 'N/A')
        income = ld.get('IncomeGroup', 'N/A')
        
        real_data_block = (
            f"REAL DATA CONTEXT (World Bank Ease of Doing Business & Regulatory Data — cite these metrics):\n"
            f"- {market} Ease of Doing Business Rank: #{ease_rank} (Score: {ease_score}/100)\n"
            f"- Contract Enforcement Score: {enforce_score}/100\n"
            f"- Time required to start a business: {days_start} days\n"
            f"- World Bank Classification: Region: {region} | Income Group: {income}\n"
        )
    else:
        real_data_block = "REAL DATA CONTEXT: No verified regulatory classification data found for this market — reason from general knowledge, but note this is an estimate.\n"

    system_prompt = (
        "You are a cautious and rigorous General Counsel (Chief Legal & Compliance Officer). Your role is to "
        "identify legal risks, international and local regulatory frameworks, compliance licensing protocols, "
        "and intellectual property requirements for the expanding enterprise. You are objective, risk-aware, and precise in your legal assessments. "
        "Keep your written analysis to 3-4 professional, dense sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    bm_str = f"\nBusiness Model / Target Customer Context: {business_model}" if business_model else ""
    
    prompt = f"""
    {real_data_block}
    
    Analyze the regulatory compliance, legal exposure, and licensing requirements for {company} entering the {market} market.{bm_str}
    Proposed Capital Allocation: {budget_display}
    Target Timeline: {timeline}
    Strategic Question: "{question}"
    
    Conduct a legal audit and output a JSON response containing:
    1. A detailed 3-4 sentence domain analysis detailing main regulatory bodies, compliance permits needed, liability risks, and timeline feasibility for {company} in {market}.
    2. A recommendation of 'YES', 'NO', or 'MAYBE' based on legal risk level.
    3. A confidence score between 0 and 100 representing the certainty of your legal finding.
    4. A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'From a legal and regulatory perspective...') that summarizes your core compliance takeaway.
    5. A concise key finding (1 sentence).
    6. A primary concern (1 sentence).
    7. A mind-change threshold (what legal/regulatory resolution would change your recommendation).
    
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
        agent_role="LEGAL",
        company=company,
        market=market,
        budget=budget_usd,
        timeline=timeline,
        question=question,
        grounding_data=legal_result
    )