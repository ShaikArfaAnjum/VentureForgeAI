from config import call_groq_api
from services.data_service import get_data

def parse_currency_value(val_str):
    """Parses currency strings like '7.63 Million', '$138,372', '1.57 Billion' to numeric USD."""
    if not val_str or val_str == "N/A":
        return None
    cleaned = str(val_str).replace("$", "").replace(",", "").strip()
    try:
        if "billion" in cleaned.lower():
            num = float(cleaned.lower().replace("billion", "").strip())
            return num * 1_000_000_000
        elif "million" in cleaned.lower():
            num = float(cleaned.lower().replace("million", "").strip())
            return num * 1_000_000
        elif "k" in cleaned.lower():
            num = float(cleaned.lower().replace("k", "").strip())
            return num * 1_000
        else:
            return float(cleaned)
    except Exception:
        return None

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

def strategize_capital(business_idea, target_market, capital_budget, timeline, strategic_question):
    """
    Capital Strategist: Evaluates capital sizing, runway feasibility, and budget calibration
    for a brand-new startup venture by benchmarking against real ecosystem funding data.
    Uses data/research_data.csv (Average Funding per Startup, Total Funding, Startups Tracked).
    
    Explicitly compares:
    'The average startup here raises approximately $X, while your proposed launch budget is approximately $Y.
     Your proposed budget is [ABOVE / BELOW / IN LINE WITH] that benchmark.'
    Does NOT fabricate ungrounded corporate NPV, ROI, or public market multiples.
    """
    budget_str = format_budget(capital_budget)
    proposed_val = capital_budget * 1_000_000 if (isinstance(capital_budget, (int, float)) and capital_budget < 1000) else float(capital_budget)
    
    # Pull real startup ecosystem funding data for benchmark comparison
    research_result = get_data("Research Data", Country=target_market)
    
    benchmark_position = "UNVERIFIED"
    if research_result["status"] == "success":
        rd = research_result["data"]
        avg_funding = rd.get('Average Funding per Startup (USD)', 'N/A')
        tot_funding = rd.get('Total Funding (USD)', 'N/A')
        startups = rd.get('Startups Tracked', 'N/A')
        
        bench_num = parse_currency_value(avg_funding)
        if bench_num:
            if proposed_val > bench_num * 1.20:
                benchmark_position = "ABOVE"
            elif proposed_val < bench_num * 0.80:
                benchmark_position = "BELOW"
            else:
                benchmark_position = "IN LINE WITH"
                
        real_data_block = (
            f"REAL DATA CONTEXT (Startup ecosystem funding benchmarks — REQUIRED BENCHMARK COMPARISON):\n"
            f"- Average funding per startup in {target_market}: ${avg_funding} USD\n"
            f"- Total ecosystem venture capital tracked: ${tot_funding} USD\n"
            f"- Total active startups tracked: {startups}\n"
            f"- Proposed Launch Budget: {budget_str}\n"
            f"- Mathematical Position: Your proposed budget ({budget_str}) is {benchmark_position} the local startup funding benchmark (${avg_funding} USD).\n"
        )
        data_verified = True
    else:
        real_data_block = (
            f"REAL DATA CONTEXT: No verified startup ecosystem funding benchmark found for '{target_market}' on disk. "
            f"State clearly that empirical average startup funding metrics are unavailable for direct calibration.\n"
        )
        data_verified = False

    system_prompt = (
        "You are an elite Venture Capital Strategist and Startup CFO in a boardroom. "
        "Your role is to determine whether the proposed launch budget is sensible for a new venture in the target country. "
        "CRITICAL RULES: "
        "1. Do NOT use public corporate financial metrics (revenue, market cap, corporate NPV/ROI) because this is a brand-new venture. "
        "2. You MUST explicitly compare: 'The average startup in {target_market} raises approximately $X, while your proposed launch budget is approximately $Y. Your proposed budget is [ABOVE / BELOW / IN LINE WITH] that benchmark.' "
        "3. Accurately explain whether the proposed budget is below, in line with, or above the local ecosystem benchmark. "
        "4. Do NOT fabricate ungrounded ROI, NPV, or multi-year revenue projections. State financial data limitations transparently. "
        "Keep your written analysis to 3-4 professional, dense sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    prompt = f"""
    {real_data_block}
    
    Evaluate capital sizing, runway efficiency, and budget benchmark alignment for launching a new business in {target_market}.
    
    Business Idea: "{business_idea}"
    Target Market / Country: {target_market}
    Proposed Launch Budget: {budget_str}
    Execution Timeline: {timeline}
    Strategic Founder Question: "{strategic_question}"
    
    Conduct a capital strategy audit and output a JSON response containing:
    1. 'analysis': A detailed 3-4 sentence domain analysis evaluating capital sizing against the local startup benchmark. You MUST explicitly state: "The average startup in {target_market} raises approximately $X, while your proposed launch budget is approximately $Y. Your proposed budget is [ABOVE / BELOW / IN LINE WITH] that benchmark." Assess budget realism over the {timeline} horizon.
    2. 'key_finding': A concise single-sentence summary of your capital feasibility verdict.
    3. 'strongest_evidence': The primary empirical funding benchmark cited.
    4. 'primary_concern': The single biggest capital sizing or burn rate risk.
    5. 'recommendation': 'YES', 'NO', or 'MAYBE' based on capital efficiency and budget realism.
    6. 'confidence': An integer between 0 and 100 representing data confidence.
    7. 'dialogue': A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'Looking at startup funding benchmarks in...') summarizing your takeaway.
    8. 'data_verified': boolean ({'true' if data_verified else 'false'}).
    9. 'mind_change_threshold': A single sentence stating what specific burn rate, milestone efficiency, or co-investment commitment would change your recommendation.
    
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
        agent_role="CAPITAL_STRATEGIST",
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
        res["key_finding"] = res.get("analysis", "")[:120] + "..." if len(res.get("analysis", "")) > 120 else res.get("analysis", "Capital sizing and funding benchmark evaluated.")
    if "strongest_evidence" not in res or not res.get("strongest_evidence"):
        res["strongest_evidence"] = f"Average startup funding benchmark in {target_market}: ${avg_funding if data_verified else 'N/A'}"
    if "primary_concern" not in res or not res.get("primary_concern"):
        res["primary_concern"] = f"Budget alignment relative to local startup funding ({benchmark_position if data_verified else 'unverified'})."
    if "mind_change_threshold" not in res or not res.get("mind_change_threshold"):
        res["mind_change_threshold"] = "Constructing a unit-economic model demonstrating 18+ months of operational runway under conservative burn rates would alter this recommendation."
    return res
