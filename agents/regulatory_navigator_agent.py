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

def navigate_regulations(business_idea, target_market, capital_budget, timeline, strategic_question):
    """
    Regulatory Navigator: Evaluates the incorporation burden, commercial registration friction,
    and compliance landscape for a brand-new business entity entering the target market.
    Uses data/legal_data.csv (Starting a Business Rank/Score, Days to Start Business,
    Ease of Doing Business Rank/Score, Enforcing Contracts Score, Resolving Insolvency Score).
    """
    budget_str = format_budget(capital_budget)
    
    # Pull real World Bank legal & regulatory indicators
    legal_result = get_data("Legal Data", Country=target_market)
    if legal_result["status"] != "success":
        legal_result = get_data("Country Data", Country=target_market)
        
    if legal_result["status"] == "success":
        ld = legal_result["data"]
        ease_rank = ld.get('Ease of Doing Business Rank', 'N/A')
        ease_score = ld.get('Ease of Doing Business Score', 'N/A')
        start_rank = ld.get('Starting a Business Rank', 'N/A')
        start_score = ld.get('Starting a Business Score', 'N/A')
        days_start = ld.get('Days to Start Business', 'N/A')
        enforce_score = ld.get('Enforcing Contracts Score', 'N/A')
        insolv_score = ld.get('Resolving Insolvency Score', 'N/A')
        region = ld.get('Region', 'N/A')
        income = ld.get('IncomeGroup', 'N/A')
        
        real_data_block = (
            f"REAL DATA CONTEXT (World Bank Regulatory & Ease of Business Dataset — cite these metrics):\n"
            f"- Starting a Business Score: {start_score}/100 (Global Rank #{start_rank})\n"
            f"- Average time required to start a business: {days_start} days\n"
            f"- Overall Ease of Doing Business: Score {ease_score}/100 (Rank #{ease_rank})\n"
            f"- Contract Enforcement Score: {enforce_score}/100\n"
            f"- Insolvency Resolution Score: {insolv_score}/100\n"
            f"- World Bank Classification: Region: {region} | Income Group: {income}\n"
        )
        data_verified = True
    else:
        real_data_block = (
            f"REAL DATA CONTEXT: No verified World Bank regulatory dataset found for '{target_market}' on disk. "
            f"State clearly that empirical business registration metrics are unlisted and advise formal legal clearance.\n"
        )
        data_verified = False

    system_prompt = (
        "You are an elite Startup Regulatory Navigator and Venture Counsel in a boardroom. "
        "Your role is to evaluate the incorporation friction, registration barriers, licensing hurdles, "
        "and compliance exposure for a first-time founder launching a new business idea. "
        "Do not present legal advice as certainty; frame your findings as a data-driven strategic assessment based on World Bank metrics. "
        "Keep your written analysis to 3-4 professional, dense sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    prompt = f"""
    {real_data_block}
    
    Evaluate the regulatory and incorporation landscape for launching a new business in {target_market}.
    
    Business Idea: "{business_idea}"
    Target Market / Country: {target_market}
    Proposed Launch Budget: {budget_str}
    Execution Timeline: {timeline}
    Strategic Founder Question: "{strategic_question}"
    
    Conduct a regulatory navigation audit and output a JSON response containing:
    1. 'analysis': A detailed 3-4 sentence domain analysis evaluating business startup ease, incorporation timeframes, licensing hurdles, and legal environment for '{business_idea}'. Reference the REAL DATA CONTEXT above where relevant (cite Starting a Business rank/score and registration days).
    2. 'key_finding': A concise single-sentence summary of your regulatory and incorporation verdict.
    3. 'strongest_evidence': The primary empirical legal/regulatory metric cited.
    4. 'primary_concern': The single biggest compliance, licensing, or registration hurdle.
    5. 'recommendation': 'YES', 'NO', or 'MAYBE' based on regulatory burden and founder friendliness.
    6. 'confidence': An integer between 0 and 100 representing data confidence.
    7. 'dialogue': A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'From an incorporation and compliance standpoint...') summarizing your takeaway.
    8. 'data_verified': boolean ({'true' if data_verified else 'false'}).
    9. 'mind_change_threshold': A single sentence stating what specific regulatory filing clearance or licensing confirmation would change your recommendation.
    
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
        agent_role="REGULATORY_NAVIGATOR",
        company=business_idea,
        market=target_market,
        budget=capital_budget,
        timeline=timeline,
        question=strategic_question,
        grounding_data=legal_result
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
        res["key_finding"] = res.get("analysis", "")[:120] + "..." if len(res.get("analysis", "")) > 120 else res.get("analysis", "Regulatory and compliance burden evaluated.")
    if "strongest_evidence" not in res or not res.get("strongest_evidence"):
        res["strongest_evidence"] = f"World Bank Doing Business indicators for {target_market}" if data_verified else "General jurisdictional business laws"
    if "primary_concern" not in res or not res.get("primary_concern"):
        res["primary_concern"] = "Licensing delays and commercial incorporation friction."
    if "mind_change_threshold" not in res or not res.get("mind_change_threshold"):
        res["mind_change_threshold"] = "Formal legal verification of expedited incorporation or foreign ownership permits would shift this recommendation."
    return res
