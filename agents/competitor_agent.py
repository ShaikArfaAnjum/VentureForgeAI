from config import call_groq_api, format_budget_display, parse_budget_numeric
from services.data_service import get_data

def analyze_competition(company, market, budget, timeline, question, business_model=""):
    """
    Competitive Intelligence Director: Analyzes competitors, market share, barriers to entry, and gaps.
    """
    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    # Pull real market-leader data for the target country/market
    competition_result = get_data("Competition Data", Country=market)
    
    if competition_result["status"] == "success":
        cd = competition_result["data"]
        real_data_block = (
            f"MACRO CORPORATE DATA CONTEXT (General Sovereign Public Market-Cap Leaders — use strictly as regional enterprise context; "
            f"DO NOT claim unrelated diversified conglomerates like mining, banking, or healthcare leaders are direct sector competitors in niche domains unless relevant):\n"
            f"- Sovereign market cap benchmark in regional territory: {cd.get('Top Company', 'N/A')} ({cd.get('Top Company Symbol', 'N/A')})\n"
            f"- {cd.get('Top Company', 'N/A')} Market Cap Benchmark: {cd.get('Top Company Market Cap (USD)', 'N/A')}\n"
            f"- Tracked public entities in territory: {cd.get('Companies Tracked', 'N/A')}\n"
        )
    else:
        real_data_block = "REAL DATA CONTEXT: No verified regional competitor dataset found on disk — evaluate competitive dynamics using sector domain knowledge.\n"

    system_prompt = (
        "You are an elite Competitive Intelligence Director. Your role is to analyze the competitive forces "
        "in the target market, evaluate direct and indirect competitors relevant to the specific domain, estimate market share concentration, "
        "and discover competitive advantages or gaps for the expanding company. You are strategic, analytical, and highly tactical. "
        "CRITICAL: Do NOT cite unrelated sovereign conglomerates (e.g. mining/banking companies) as direct competitors in unrelated industries. "
        "Keep your written analysis to 3-4 professional, dense sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    bm_str = f"\nBusiness Model / Target Customer Context: {business_model}" if business_model else ""
    
    prompt = f"""
    {real_data_block}
    
    Analyze the competitive landscape for {company} entering the {market} market.{bm_str}
    Proposed Capital Allocation: {budget_display}
    Target Timeline: {timeline}
    Strategic Question: "{question}"
    
    Conduct a competitive assessment and output a JSON response containing:
    1. A detailed 3-4 sentence domain analysis detailing direct competitors specific to {market}, market share dynamics, competitor gaps, entry barriers, and how {company} differentiates.
    2. A recommendation of 'YES', 'NO', or 'MAYBE' based on competitive positioning.
    3. A confidence score between 0 and 100 representing the certainty of your assessment.
    4. A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'Analyzing our competition in...') that summarizes your core competitive takeaway.
    5. A concise key finding (1 sentence).
    6. A primary concern (1 sentence).
    7. A mind-change threshold (what competitive shift would change your recommendation).
    
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
        agent_role="COMPETITOR",
        company=company,
        market=market,
        budget=budget_usd,
        timeline=timeline,
        question=question,
        grounding_data=competition_result
    )