"""
Verification test script for Launch Case 4: DO NOT LAUNCH
Business Venture: Consumer hardware startup developing an expensive AI-enabled smart home device requiring large-scale manufacturing, international distribution, and significant upfront inventory investment
Country: Australia
Budget: $50,000 USD
Timeline: 6 Months
Question: Should we launch this AI-enabled smart home hardware business in Australia with only a $50,000 budget and a six-month timeline?
"""
import sys
import os
import io

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.track_b_orchestrator import run_track_b_session
from services.report_generator import generate_pdf_report
from services.consistency_validator import validate_consistency
from ui.components import render_decision_trace_card, render_critical_blockers_card, render_executive_decision_header

def test_case_4():
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass

    idea = "Consumer hardware startup developing an expensive AI-enabled smart home device requiring large-scale manufacturing, international distribution, and significant upfront inventory investment"
    market = "Australia"
    budget = 50000
    timeline = "6 Months"
    question = "Should we launch this AI-enabled smart home hardware business in Australia with only a $50,000 budget and a six-month timeline?"

    print("=" * 70)
    print("EXECUTING LAUNCH CASE 4 (DO NOT LAUNCH VERIFICATION)")
    print(f"Venture: {idea}")
    print(f"Market: {market} | Budget: ${budget:,} | Timeline: {timeline}")
    print("=" * 70 + "\n")

    result = run_track_b_session(
        business_idea=idea,
        target_market=market,
        capital_budget=budget,
        timeline=timeline,
        strategic_question=question
    )

    print("\n--- TEST CASE 4 AUDIT RESULTS ---")
    decision = result.get("final_decision")
    confidence = result.get("confidence")
    rules_passed = result.get("deterministic_eval", {}).get("rules_passed_count")
    total_rules = result.get("deterministic_eval", {}).get("total_rules")
    blockers = result.get("critical_blockers", [])
    votes = result.get("specialist_votes")
    
    print(f"Final Decision: {decision}")
    print(f"Confidence: {confidence}%")
    print(f"Rules Passed: {rules_passed}/{total_rules}")
    print(f"Specialist Votes: {votes}")
    print(f"Critical Blockers Count: {len(blockers)}")
    for idx, b in enumerate(blockers, 1):
        print(f"  [{idx}] {b.get('severity')} - {b.get('source', b.get('source_specialist'))}: {b.get('title')}")
        print(f"      Description: {b.get('description')[:90]}...")

    # Assertions
    assert decision == "DO NOT LAUNCH", f"Expected 'DO NOT LAUNCH', got '{decision}'"
    assert confidence >= 75, f"Expected high confidence (>=75%), got {confidence}%"
    assert len(blockers) > 0, "Expected critical blockers for $50k hardware launch"
    
    # Test UI component safety
    print("\n--- TESTING UI COMPONENTS RENDERING ---")
    try:
        # Test render_decision_trace_card with both dict and list
        render_decision_trace_card(result.get("decision_trace"))
        render_decision_trace_card(result.get("decision_trace", {}).get("stages", []))
        print("✓ render_decision_trace_card passed without AttributeError")
    except Exception as e:
        print(f"✕ render_decision_trace_card failed: {e}")
        raise e

    # Test PDF Generation
    pdf_bytes = generate_pdf_report(result)
    print(f"✓ PDF Generated successfully: {len(pdf_bytes):,} bytes")
    assert len(pdf_bytes) > 10000, "PDF size too small"

    print("\n" + "=" * 70)
    print("✅ LAUNCH CASE 4 PASSED WITH AUTHORITATIVE 'DO NOT LAUNCH' VERDICT!")
    print("=" * 70)

if __name__ == "__main__":
    test_case_4()
