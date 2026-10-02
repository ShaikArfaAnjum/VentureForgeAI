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
def scout_competition(business_idea, target_market, capital_budget, timeline, strategic_question):
    """
    Competitive Scout: Evaluates market crowdedness, incumbent concentration,
    and whether a new entrant can realistically establish a foothold.
    Uses data/competition_data.csv (Top Company, Symbol, Market Cap, Tracked Companies, Top Competitors).
    """
    budget_str = format_budget(capital_budget)
    # Pull real competitor landscape data for the target market
    competition_result = get_data("Competition Data", Country=target_market)    
    if competition_result["status"] == "success":
        cd = competition_result["data"]
        top_co = cd.get('Top Company', 'N/A')
        top_sym = cd.get('Top Company Symbol', 'N/A')
        top_mcap = cd.get('Top Company Market Cap (USD)', 'N/A')
        tracked_count = cd.get('Companies Tracked', 'N/A')
        top_comps = cd.get('Top Competitors', top_co)
        sym_str = f" ({top_sym})" if top_sym and top_sym != "N/A" else ""
        real_data_block = (
            f"REAL DATA CONTEXT (Competition intelligence dataset — cite these empirical figures):\n"
            f"- Market leader in {target_market}: {top_co}{sym_str}\n"
            f"- Market leader valuation: {top_mcap}\n"
            f"- Tracked public/major companies: {tracked_count}\n"
            f"- Major key competitors: {top_comps}\n"
        )
        data_verified = True
    else:
        real_data_block = (
            f"REAL DATA CONTEXT: No verified competitor intelligence dataset found for '{target_market}' on disk. "
            f"State clearly that public competitor concentration data is unavailable and evaluate entry barriers from general sector dynamics.\n"
        )
        data_verified = False

    system_prompt = (
        "You are an elite Competitive Intelligence Scout and Market Strategist in a startup boardroom. "
        "Your role is to determine how crowded the target country is and whether a brand-new entrant with a novel idea "
        "can establish a defensible foothold against dominant incumbents. "
        "Do NOT fabricate competitor names or market shares. Ground your insights strictly in available data. "
        "Keep your written analysis to 3-4 professional, dense, and tactical sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    prompt = f"""
    {real_data_block}
    
    Evaluate the competitive barrier and crowdedness for launching a new business in {target_market}.
    
    Business Idea: "{business_idea}"
    Target Market / Country: {target_market}
    Proposed Launch Budget: {budget_str}
    Execution Timeline: {timeline}
    Strategic Founder Question: "{strategic_question}"
    
    Conduct a competitive scouting audit and output a JSON response containing:
    1. 'analysis': A detailed 3-4 sentence domain analysis evaluating incumbent strength, competitor concentration, moat requirements, and whitespace opportunities for '{business_idea}'. Reference the REAL DATA CONTEXT above where relevant.
    2. 'key_finding': A concise single-sentence summary of your competitive barrier verdict.
    3. 'strongest_evidence': The primary empirical competitor metric cited.
    4. 'primary_concern': The single biggest incumbent threat or entry barrier.
    5. 'recommendation': 'YES', 'NO', or 'MAYBE' based on competitive positioning and entry viability.
    6. 'confidence': An integer between 0 and 100 representing data certainty.
    7. 'dialogue': A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'From a competitive scouting lens...') summarizing your takeaway.
    8. 'data_verified': boolean ({'true' if data_verified else 'false'}).
    9. 'mind_change_threshold': A single sentence stating what competitive shift or proprietary moat evidence would change your recommendation.
    
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
        agent_role="COMPETITIVE_SCOUT",
        company=business_idea,
        market=target_market,
        budget=capital_budget,
        timeline=timeline,
        question=strategic_question,
        grounding_data=competition_result
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
        res["key_finding"] = res.get("analysis", "")[:120] + "..." if len(res.get("analysis", "")) > 120 else res.get("analysis", "Competitive positioning evaluated.")
    if "strongest_evidence" not in res or not res.get("strongest_evidence"):
        res["strongest_evidence"] = f"Incumbent landscape in {target_market}" if data_verified else "General sector competition dynamics"
    if "primary_concern" not in res or not res.get("primary_concern"):
        res["primary_concern"] = "Incumbent market entrenchment and pricing power."
    if "mind_change_threshold" not in res or not res.get("mind_change_threshold"):
        res["mind_change_threshold"] = "Discovery of a direct competitor releasing an equivalent proprietary feature would downgrade this recommendation."
    return res
