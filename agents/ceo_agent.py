from config import call_groq_api, format_budget_display, parse_budget_numeric

def analyze_ceo(company, market, budget, timeline, question, board_reports, business_model=""):
    """
    CEO Agent: Synthesizes board feedback and provides executive strategic rationale.
    """
    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    system_prompt = (
        "You are an elite, visionary Chief Executive Officer (CEO). Your job is to listen carefully to the "
        "feedback, empirical data, and risk parameters provided by your core executive team, weigh the strategic and financial "
        "opportunities against the risk exposure, and deliver a synthesized executive rationale. "
        "Your recommendation must be: ENTER MARKET, ENTER WITH CONDITIONS, DELAY ENTRY, or REJECT EXPANSION. "
        "Keep your written executive rationale to 2-3 concise, impactful sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    # Format the board reports for the LLM
    board_reports_text = ""
    for agent_name, report in board_reports.items():
        board_reports_text += f"""
---
[{agent_name} REPORT]
Recommendation: {report.get('recommendation')}
Confidence: {report.get('confidence')}%
Key Finding: {report.get('key_finding', 'N/A')}
Primary Concern: {report.get('primary_concern', 'N/A')}
Detailed Analysis: {report.get('analysis')}
---
"""
        
    bm_str = f"\nBusiness Model / Target Customer: {business_model}" if business_model else ""
    
    prompt = f"""
    You are the CEO of {company}. You are chairing a board meeting to decide on a highly critical corporate expansion.{bm_str}
    
    Strategic Expansion Question: "{question}"
    Target Market: {market}
    Proposed Capital Allocation: {budget_display}
    Target Timeline: {timeline}
    
    Here is the consolidated feedback and formal recommendations submitted by your executive team:
    {board_reports_text}
    
    Based on all of this board input, deliver your final executive decision, overall confidence level, and a concise strategic rationale.
    
    JSON Schema:
    {{
      "analysis": "A 2-3 sentence strategic rationale synthesizing the board reports and explaining the decision.",
      "recommendation": "ENTER MARKET" | "ENTER WITH CONDITIONS" | "DELAY ENTRY" | "REJECT EXPANSION",
      "confidence": integer,
      "dialogue": "string (A 1-2 sentence spoken boardroom statement in character delivered to conclude the meeting.)"
    }}
    """
    
    return call_groq_api(
        prompt=prompt,
        system_prompt=system_prompt,
        response_format={"type": "json_object"},
        agent_role="CEO",
        company=company,
        market=market,
        budget=budget_usd,
        timeline=timeline,
        question=question
    )

