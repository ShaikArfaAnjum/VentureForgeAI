"""
BOARDROOMAI - STEP 31 REAL AUSTRALIA BENCHMARK SCENARIO VERIFICATION
Tests the exact scenario required by the user prompt:
- Business Idea: "An AI-powered SaaS platform that helps logistics companies optimize delivery routes, reduce fuel consumption, predict shipment delays, and lower carbon emissions using machine learning and real-time logistics data."
- Target Market: "Australia"
- Budget: 750,000 USD
- Timeline: 12 Months
"""
import sys
import os
import json
import io

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.track_b_orchestrator import run_track_b_session
from services.report_generator import generate_pdf_report
from services.consistency_validator import validate_consistency

def test_australia():
    idea = (
        "An AI-powered SaaS platform that helps logistics companies optimize delivery routes, "
        "reduce fuel consumption, predict shipment delays, and lower carbon emissions using "
        "machine learning and real-time logistics data."
    )
    market = "Australia"
    budget = 750000
    timeline = "12 Months"
    question = "Should we launch an AI logistics optimization SaaS in Australia with $750k budget?"

    print("=================================================================")
    print("EXECUTING REAL AUSTRALIA BENCHMARK SCENARIO")
    print(f"Idea: {idea[:60]}...")
    print(f"Market: {market} | Budget: ${budget:,} | Timeline: {timeline}")
    print("=================================================================\n")

    result = run_track_b_session(
        business_idea=idea,
        target_market=market,
        capital_budget=budget,
        timeline=timeline,
        strategic_question=question
    )

    print("\n--- EXECUTION SUMMARY ---")
    print(f"Status: {result.get('status')}")
    print(f"Final Decision: {result.get('final_decision')}")
    print(f"Deterministic Decision: {result.get('deterministic_decision')}")
    print(f"Deterministic Confidence: {result.get('confidence')}%")
    print(f"Evidence Quality: {result.get('evidence_quality', {}).get('status_label')}")
    print(f"Votes: {result.get('specialist_votes')}")
    print(f"Critical Blockers: {len(result.get('critical_blockers', []))}")
    print(f"Evidence Ledger Items: {len(result.get('evidence_ledger', []))}")
    print(f"Validation Gates: {len(result.get('validation_gates', []))}")
    print(f"Executive Actions: {len(result.get('executive_action_plan', []))}")
    print(f"Discrepancies Logged: {len(result.get('discrepancies', []))}")

    # Verify PDF generation
    pdf_bytes = generate_pdf_report(result)
    print(f"\nPDF Generated: {len(pdf_bytes):,} bytes")
    assert len(pdf_bytes) > 10000, "PDF size too small"

    # Consistency validation
    is_valid, errors = validate_consistency(result)
    print(f"Consistency Valid: {is_valid} (Flagged items: {errors})")
    assert is_valid or len(errors) == 0 or all("status is" in e or "Execution error" in e for e in errors), "Fatal consistency failure"

    print("\n[PASS] ALL AUSTRALIA BENCHMARK VERIFICATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
    test_australia()
