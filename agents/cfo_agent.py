from config import call_groq_api, format_budget_display, parse_budget_numeric
from services.data_service import get_data

def analyze_finance(company, market, budget, timeline, question, business_model=""):
    """
    CFO Agent: Evaluates Net Present Value, IRR, capital efficiency, payback period, and budget efficiency.
    """
    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    # Pull real financial data for the company, if available
    financial_result = get_data("Financial Data", Company=company)
    
    if financial_result["status"] == "success":
        fd = financial_result["data"]
        rev_val = fd.get('Revenue', 'N/A')
        rev_str = f"- {company} Disclosed Revenue Benchmark: {rev_val}\n" if rev_val and rev_val != "N/A" else ""
        real_data_block = (
            f"REAL DATA CONTEXT (verified company financial valuation — cite these metrics):\n"
            f"- {company} Market Capitalization: {fd.get('Market Cap', 'N/A')}\n"
            f"{rev_str}"
        )
    else:
        real_data_block = f"REAL DATA CONTEXT: No verified public financial valuation dataset on disk for {company} — evaluate capital adequacy against the proposed {budget_display} budget.\n"

    system_prompt = (
        "You are an elite Chief Financial Officer (CFO). Your role is to examine the financial viability of "
        "expansion, calculate capital requirements, estimate returns on investment (ROI), compute payback periods, "
        "and optimize budget distribution. You speak in numbers, efficiency, NPV, margins, and financial risks. "
        "CRITICAL: Always use the user's exact proposed budget in your calculations. Do NOT replace it with an arbitrary or demo budget. "
        "Keep your written analysis to 3-4 professional, dense sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    bm_str = f"\nBusiness Model / Target Customer Context: {business_model}" if business_model else ""
    
    prompt = f"""
    {real_data_block}
    
    Analyze the financial feasibility, capital efficiency, ROI projections, and payback period for {company} entering the {market} market.{bm_str}
    Proposed Capital Allocation: {budget_display}
    Target Timeline: {timeline}
    Strategic Question: "{question}"
    
    Conduct a financial feasibility audit and output a JSON response containing:
    1. A detailed 3-4 sentence domain analysis detailing Net Present Value (NPV), projected ROI, break-even period, and budget allocation recommendations for {company} based strictly on the proposed {budget_display} budget over {timeline}.
    2. A recommendation of 'YES', 'NO', or 'MAYBE' based on financial return potential and capital adequacy.
    3. A confidence score between 0 and 100 representing the certainty of your financial modeling.
    4. A 1-2 sentence spoken boardroom statement (written in the first-person as a board member, e.g., 'Looking strictly at the capital model...') that summarizes your core financial takeaway.
    5. A concise key finding (1 sentence).
    6. A primary concern (1 sentence).
    7. A mind-change threshold (what financial condition would change your recommendation).
    
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
        agent_role="CFO",
        company=company,
        market=market,
        budget=budget_usd,
        timeline=timeline,
        question=question,
        grounding_data=financial_result
    )