from config import call_groq_api

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

def decide_founder_ceo(business_idea, target_market, capital_budget, timeline, strategic_question, specialist_reports):
    """
    Founder CEO: Synthesizes the 6 specialist venture board reports and delivers
    the definitive final decision: LAUNCH, VALIDATE FIRST, or DO NOT LAUNCH.
    Produces a concrete, customized 3-5 step validation roadmap responding directly
    to concerns flagged by the specialists.
    """
    budget_str = format_budget(capital_budget)
    
    system_prompt = (
        "You are an elite, visionary Startup Founder CEO chairing a venture boardroom meeting. "
        "Your role is to evaluate the consolidated findings, data points, competitive forces, regulatory friction, "
        "and risk parameters provided by your 6 specialist board members, and make the definitive founder call. "
        "Your final recommendation MUST be EXACTLY ONE OF: 'LAUNCH', 'VALIDATE FIRST', or 'DO NOT LAUNCH'. "
        "CRITICAL ERROR-AWARENESS RULE: If one or more specialist reports indicate data unavailability or execution failure, "
        "you must exercise founder caution: do NOT declare 'LAUNCH' without sufficient empirical backing. "
        "Instead, choose 'VALIDATE FIRST' (or 'DO NOT LAUNCH' if risk is severe). "
        "You MUST also generate a 'validation_roadmap' containing 3 to 5 concrete, actionable de-risking steps "
        "where each step explicitly cites a named specialist concern (e.g., 'Address Market Validator's customer demand concern by...', 'Address Launch Operations' logistics friction by...'). "
        "Do NOT produce generic motivational advice. "
        "Keep your written executive rationale to 2-3 concise, high-impact sentences. "
        "You must output ONLY a valid JSON object matching the schema below. Do NOT output any markdown blocks outside the JSON."
    )
    
    # Format the specialist reports for the LLM
    specialist_reports_text = ""
    data_verified_overall = True
    unverified_or_failed_count = 0
    
    for role_name, report in specialist_reports.items():
        rec = report.get('recommendation', 'MAYBE')
        conf = report.get('confidence', 70)
        analysis = report.get('analysis', '')
        mct = report.get('mind_change_threshold', '')
        is_verified = report.get('data_verified', True)
        status = report.get('status', 'success' if is_verified else 'data_unavailable')
        err_msg = report.get('error_message')
        
        if not is_verified or status == "error":
            data_verified_overall = False
            unverified_or_failed_count += 1
            
        mct_str = f"Mind-Change Threshold: {mct}\n" if mct else ""
        err_str = f"Execution Status: {status.upper()} (Error: {err_msg})\n" if err_msg else f"Execution Status: {status.upper()}\n"
        
        specialist_reports_text += f"""
---
[{role_name} REPORT]
Status: {status}
Recommendation: {rec}
Confidence: {conf}%
Data Verified: {is_verified}
{err_str}Analysis: {analysis}
{mct_str}---
"""
        
    prompt = f"""
    You are the Founder & CEO leading the venture board session for: "{business_idea}".
    
    Target Market / Country: {target_market}
    Proposed Launch Budget: {budget_str}
    Execution Timeline: {timeline}
    Strategic Question: "{strategic_question}"
    
    Consolidated Specialist Venture Reports:
    {specialist_reports_text}
    
    Based on all specialist input and empirical signals, deliver your final strategic decision, overall confidence score, rationale, and validation roadmap. Each roadmap step MUST tie back to a named specialist's concern.
    
    JSON Schema:
    {{
      "analysis": "A 2-3 sentence strategic executive rationale synthesizing the board input and explaining your decision.",
      "recommendation": "LAUNCH" | "VALIDATE FIRST" | "DO NOT LAUNCH",
      "confidence": integer,
      "dialogue": "A 1-2 sentence spoken boardroom closing statement in character.",
      "validation_roadmap": [
        "Action step 1 directly responding to a named specialist concern",
        "Action step 2 directly responding to a named specialist concern",
        "Action step 3 directly responding to a named specialist concern"
      ],
      "data_verified": boolean
    }}
    """
    
    res = call_groq_api(
        prompt=prompt,
        system_prompt=system_prompt,
        response_format={"type": "json_object"},
        agent_role="FOUNDER_CEO",
        company=business_idea,
        market=target_market,
        budget=capital_budget,
        timeline=timeline,
        question=strategic_question
    )
    
    # Check for API failure
    if res.get("status") == "error" or "[API FAILURE]" in res.get("analysis", ""):
        res["status"] = "error"
        res["confidence"] = 0
        res["recommendation"] = "VALIDATE FIRST"
        res["data_verified"] = False
        return res
        
    # CONSERVATIVE DECISION SAFEGUARDS
    # Rule 1: If critical empirical data is unavailable or unverified, do NOT confidently recommend LAUNCH
    if not data_verified_overall or unverified_or_failed_count > 0:
        if res.get("recommendation") == "LAUNCH":
            res["recommendation"] = "VALIDATE FIRST"
            res["confidence"] = min(res.get("confidence", 50), 50)
            if "unverified" not in res.get("analysis", "").lower() and "unavailable" not in res.get("analysis", "").lower():
                res["analysis"] = f"While market premise shows promise, critical empirical datasets for {target_market} remain unverified or unavailable. The board recommends VALIDATE FIRST before capital deployment. " + res.get("analysis", "")
                
    # Rule 2: If specialist execution failed, note incomplete analysis in rationale
    if unverified_or_failed_count > 0 and any(r.get("status") == "error" for r in specialist_reports.values()):
        if "incomplete" not in res.get("analysis", "").lower():
            res["analysis"] = f"[CAUTION: Decision synthesized with incomplete specialist analysis due to node execution errors] " + res.get("analysis", "")
    
    # Ensure validation_roadmap is present and valid
    if "validation_roadmap" not in res or not isinstance(res["validation_roadmap"], list) or len(res["validation_roadmap"]) < 3:
        res["validation_roadmap"] = [
            f"Conduct 30 targeted customer discovery interviews in {target_market} to validate willingness-to-pay (addressing Market Validator).",
            f"Complete legal and incorporation compliance audit for new business setup in {target_market} (addressing Regulatory Navigator).",
            f"Deploy an asset-light pilot MVP to test customer acquisition and unit economics against the {budget_str} budget (addressing Capital Strategist & Launch Operations)."
        ]
        
    res["data_verified"] = data_verified_overall
    return res
