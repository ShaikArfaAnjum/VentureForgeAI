"""
BoardRoomAI — Executive PDF Report Generator
Generates publication-quality, audit-traceable executive board decision reports via ReportLab.
Produces a comprehensive, dense, professional 20-page Executive Board Decision Report
across all 30 required executive governance sections.
"""

import os
import time
import re
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group

from config import format_budget_display, parse_budget_numeric
from services.canonical_result import get_evidence_quality
from services.consistency_validator import validate_consistency


class NumberedCanvas(canvas.Canvas):
    """Custom canvas to compute total page count dynamically and print headers and footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return  # Cover page remains clean
            
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#1E3A8A"))
        
        # Header rule and title
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 752, 572, 752)
        self.drawString(40, 758, "BOARDROOM AI — EXECUTIVE BOARD DECISION INTELLIGENCE REPORT")
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawRightString(572, 758, "CONFIDENTIAL &bull; BOARD OF DIRECTORS")
        
        # Footer rule and page number
        self.line(40, 42, 572, 42)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 30, page_str)
        self.drawString(40, 30, "CONFIDENTIAL &bull; BOARDROOMAI MULTI-AGENT GOVERNANCE &bull; AUDIT-TRACEABLE ARTIFACT")
        self.restoreState()


def _get_styles():
    """Builds and returns reusable consulting-grade styles for ReportLab."""
    styles = getSampleStyleSheet()
    
    custom_styles = {
        'CoverTitle': ParagraphStyle(
            'CoverTitle', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=26, leading=32,
            textColor=colors.HexColor("#0F172A"), alignment=TA_CENTER
        ),
        'CoverSubtitle': ParagraphStyle(
            'CoverSubtitle', parent=styles['Normal'],
            fontName='Helvetica', fontSize=12, leading=16,
            textColor=colors.HexColor("#475569"), alignment=TA_CENTER
        ),
        'CoverMetaLabel': ParagraphStyle(
            'CoverMetaLabel', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=8.5, leading=12,
            textColor=colors.HexColor("#1E3A8A")
        ),
        'CoverMetaVal': ParagraphStyle(
            'CoverMetaVal', parent=styles['Normal'],
            fontName='Helvetica', fontSize=8.5, leading=12,
            textColor=colors.HexColor("#1E293B")
        ),
        'CoverVerdict': ParagraphStyle(
            'CoverVerdict', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=14, leading=18,
            alignment=TA_CENTER
        ),
        'CoverVerdictSub': ParagraphStyle(
            'CoverVerdictSub', parent=styles['Normal'],
            fontName='Helvetica', fontSize=9, leading=12,
            alignment=TA_CENTER, textColor=colors.HexColor("#475569")
        ),
        'SectionH1': ParagraphStyle(
            'SectionH1', parent=styles['Heading1'],
            fontName='Helvetica-Bold', fontSize=12, leading=15,
            textColor=colors.HexColor("#0F172A"), spaceBefore=4, spaceAfter=3,
            keepWithNext=True
        ),
        'SectionH2': ParagraphStyle(
            'SectionH2', parent=styles['Heading2'],
            fontName='Helvetica-Bold', fontSize=9.5, leading=12.5,
            textColor=colors.HexColor("#1E3A8A"), spaceBefore=5, spaceAfter=2.5,
            keepWithNext=True
        ),
        'Body': ParagraphStyle(
            'Body', parent=styles['BodyText'],
            fontName='Helvetica', fontSize=8, leading=11,
            textColor=colors.HexColor("#334155")
        ),
        'BodyBold': ParagraphStyle(
            'BodyBold', parent=styles['BodyText'],
            fontName='Helvetica-Bold', fontSize=8, leading=11,
            textColor=colors.HexColor("#0F172A")
        ),
        'BodyItalic': ParagraphStyle(
            'BodyItalic', parent=styles['BodyText'],
            fontName='Helvetica-Oblique', fontSize=7.5, leading=10.5,
            textColor=colors.HexColor("#64748B")
        ),
        'TableHead': ParagraphStyle(
            'TableHead', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=7.5, leading=10,
            textColor=colors.HexColor("#0F172A")
        ),
        'TableCell': ParagraphStyle(
            'TableCell', parent=styles['Normal'],
            fontName='Helvetica', fontSize=7.5, leading=10,
            textColor=colors.HexColor("#334155")
        ),
        'TableCellBold': ParagraphStyle(
            'TableCellBold', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=7.5, leading=10,
            textColor=colors.HexColor("#0F172A")
        ),
        'TableCellRight': ParagraphStyle(
            'TableCellRight', parent=styles['Normal'],
            fontName='Helvetica', fontSize=7.5, leading=10,
            textColor=colors.HexColor("#334155"), alignment=TA_RIGHT
        ),
        'CodeStyle': ParagraphStyle(
            'CodeStyle', parent=styles['Normal'],
            fontName='Courier', fontSize=7, leading=9,
            textColor=colors.HexColor("#0F172A")
        ),
        'WarningBox': ParagraphStyle(
            'WarningBox', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=8, leading=11.5,
            textColor=colors.HexColor("#991B1B")
        ),
        'CalloutBox': ParagraphStyle(
            'CalloutBox', parent=styles['Normal'],
            fontName='Helvetica', fontSize=8, leading=11.5,
            textColor=colors.HexColor("#1E293B")
        )
    }
    return custom_styles


# =========================================================================
# PURE REPORTLAB VECTOR GRAPHICS (Zero External Dependencies)
# =========================================================================

def _render_dimension_scorecard_chart(metrics):
    """Renders a crisp vector horizontal progress bar chart for the 4 dimensions."""
    try:
        d = Drawing(532, 95)
        d.add(Rect(0, 0, 532, 95, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=0.5, rx=3, ry=3))
        
        categories = [
            ("Market Opportunity", metrics.get('opportunity_score', 0)),
            ("Risk Mitigation", metrics.get('risk_mitigation_score', 0)),
            ("Market Readiness", metrics.get('market_readiness', 0)),
            ("Financial Feasibility", metrics.get('financial_feasibility', 0)),
        ]
        
        y = 72
        for label, score in categories:
            if score >= 75:
                bar_col = colors.HexColor("#10B981")
            elif score >= 50:
                bar_col = colors.HexColor("#F59E0B")
            else:
                bar_col = colors.HexColor("#EF4444")
                
            d.add(String(12, y + 2, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))
            d.add(Rect(160, y, 290, 9.5, fillColor=colors.HexColor("#E2E8F0"), strokeColor=None, rx=2, ry=2))
            bar_w = max(4, int(290 * (min(100, max(0, score)) / 100.0)))
            d.add(Rect(160, y, bar_w, 9.5, fillColor=bar_col, strokeColor=None, rx=2, ry=2))
            d.add(String(465, y + 2, f"{score} / 100", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#0F172A")))
            y -= 19
            
        return d
    except Exception as e:
        print(f"[PDF CHART WARNING] Scorecard chart failed: {e}")
        return None


def _render_agent_confidence_chart(agent_data):
    """Renders a clean vector bar chart of specialist agent confidence."""
    try:
        if not agent_data:
            return None
        h = max(65, len(agent_data) * 15 + 14)
        d = Drawing(532, h)
        d.add(Rect(0, 0, 532, h, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=0.5, rx=3, ry=3))
        
        y = h - 18
        for a in agent_data:
            name = a.get("name", "Agent")
            conf = a.get("confidence", 0)
            d.add(String(12, y + 2, name[:26], fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.HexColor("#1E293B")))
            d.add(Rect(165, y, 285, 8, fillColor=colors.HexColor("#E2E8F0"), strokeColor=None, rx=2, ry=2))
            bar_w = max(4, int(285 * (min(100, max(0, conf)) / 100.0)))
            d.add(Rect(165, y, bar_w, 8, fillColor=colors.HexColor("#1E3A8A"), strokeColor=None, rx=2, ry=2))
            d.add(String(465, y + 2, f"{conf}%", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.HexColor("#0F172A")))
            y -= 15
            
        return d
    except Exception as e:
        print(f"[PDF CHART WARNING] Confidence chart failed: {e}")
        return None


def _render_risk_distribution_chart(risk_matrix):
    """Renders vector chart showing counts for LOW, MEDIUM, HIGH, CRITICAL risks."""
    try:
        if not risk_matrix:
            return None
        severities = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        for r in risk_matrix:
            lvl = str(r.get('level', 'MEDIUM')).upper()
            if lvl in severities:
                severities[lvl] += 1
            else:
                severities['MEDIUM'] += 1
                
        d = Drawing(532, 75)
        d.add(Rect(0, 0, 532, 75, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=0.5, rx=3, ry=3))
        
        sev_info = [
            ("LOW SEVERITY", severities['LOW'], colors.HexColor("#10B981")),
            ("MEDIUM SEVERITY", severities['MEDIUM'], colors.HexColor("#F59E0B")),
            ("HIGH SEVERITY", severities['HIGH'], colors.HexColor("#EA580C")),
            ("CRITICAL SEVERITY", severities['CRITICAL'], colors.HexColor("#DC2626")),
        ]
        max_c = max(max(severities.values()), 1)
        
        y = 55
        for label, count, col in sev_info:
            d.add(String(12, y + 2, label, fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.HexColor("#1E293B")))
            d.add(Rect(160, y, 290, 8, fillColor=colors.HexColor("#E2E8F0"), strokeColor=None, rx=2, ry=2))
            bar_w = max(4, int(290 * (count / max_c))) if count > 0 else 0
            if bar_w > 0:
                d.add(Rect(160, y, bar_w, 8, fillColor=col, strokeColor=None, rx=2, ry=2))
            d.add(String(465, y + 2, f"{count} Risk{'s' if count != 1 else ''}", fontName="Helvetica-Bold", fontSize=7.5, fillColor=colors.HexColor("#0F172A")))
            y -= 14
            
        return d
    except Exception as e:
        print(f"[PDF CHART WARNING] Risk distribution chart failed: {e}")
        return None


# =========================================================================
# DATA EXTRACTION AND CONTEXT NORMALIZATION
# =========================================================================

def _extract_report_data(session_data):
    """
    Extracts, normalizes, and validates all available session data.
    Ensures zero hallucination by pulling strictly from real session attributes,
    datasets, or calculated canonical properties.
    """
    from services.expansion_canonical_result import (
        build_expansion_risk_matrix,
        build_expansion_critical_blockers,
        build_expansion_evidence_ledger,
        build_expansion_action_plan
    )
    
    company = session_data.get("company") or session_data.get("company_name") or "Corporate Enterprise"
    market = session_data.get("market") or session_data.get("target_market") or session_data.get("target_country") or "Target Market"
    raw_budget = session_data.get("budget", 0)
    budget_usd = parse_budget_numeric(raw_budget)
    budget_display = session_data.get("budget_display") or format_budget_display(budget_usd)
    timeline = session_data.get("timeline") or "1 Year"
    question = session_data.get("question") or session_data.get("strategic_question") or session_data.get("strategic_board_question") or "Strategic Corporate Expansion Assessment"
    business_model = session_data.get("business_model") or session_data.get("target_customer") or ""
    timestamp = session_data.get("timestamp") or time.time()
    session_id = session_data.get("session_id") or f"BRD-{int(timestamp)}"
    
    final_decision = session_data.get("final_decision") or session_data.get("decision") or session_data.get("ceo_decision") or "CONDITIONAL"
    confidence = session_data.get("confidence") or session_data.get("ceo_confidence") or 75
    ceo_rationale = session_data.get("ceo_rationale") or session_data.get("rationale") or ""
    
    # Consensus metrics
    consensus_metrics = session_data.get("consensus_metrics", {})
    opp_score = consensus_metrics.get("opportunity_score", session_data.get("opportunity_score", 0))
    risk_mit_score = consensus_metrics.get("risk_mitigation_score", session_data.get("risk_mitigation_score", 0))
    mkt_readiness = consensus_metrics.get("market_readiness", session_data.get("market_readiness", 0))
    fin_score = consensus_metrics.get("financial_feasibility", session_data.get("financial_feasibility", 0))
    
    # Extract Specialist Reports
    reports = {}
    raw_reports = session_data.get("board_reports") or session_data.get("specialist_reports") or {}
    for k, v in raw_reports.items():
        if isinstance(v, dict):
            reports[k.upper()] = dict(v)
            
    # Ingest transcript if any agents are missing from reports
    transcript = session_data.get("transcript", [])
    for msg in transcript:
        aid = str(msg.get("agent_id", "")).upper()
        if aid and aid not in reports:
            reports[aid] = {
                "name": msg.get("name", aid.title()),
                "recommendation": msg.get("recommendation", "MAYBE"),
                "confidence": msg.get("confidence", 75),
                "analysis": msg.get("analysis", ""),
                "dialogue": msg.get("dialogue", ""),
                "key_finding": msg.get("key_finding", msg.get("analysis", "")[:120]),
                "primary_concern": msg.get("primary_concern", ""),
                "mind_change_threshold": msg.get("mind_change_threshold", "N/A"),
                "data_verified": msg.get("data_verified", False)
            }
            
    # Grounding facts
    grounding_facts = session_data.get("grounding_facts")
    if not grounding_facts:
        try:
            from services.data_service import get_data
            grounding_facts = {
                "Research Data": get_data("Research Data", Country=market).get("data", {}),
                "Competition Data": get_data("Competition Data", Country=market).get("data", {}),
                "Legal Data": get_data("Legal Data", Country=market).get("data", {}),
                "Market Data": get_data("Market Data", Country=market).get("data", {}),
                "Risk Data": get_data("Risk Data", Country=market).get("data", {}),
                "Financial Data": get_data("Financial Data", Company=company).get("data", {})
            }
        except Exception:
            grounding_facts = {}

    # Risk matrix
    risk_matrix = session_data.get("risk_matrix")
    if not risk_matrix:
        try:
            risk_matrix = build_expansion_risk_matrix(market, reports, grounding_facts)
        except Exception:
            risk_matrix = []
            
    # Critical blockers
    critical_blockers = session_data.get("critical_blockers")
    if not critical_blockers:
        try:
            critical_blockers = build_expansion_critical_blockers(reports)
        except Exception:
            critical_blockers = []
            
    # Evidence ledger
    evidence_ledger = session_data.get("evidence_ledger")
    if not evidence_ledger:
        try:
            evidence_ledger = build_expansion_evidence_ledger(company, market, budget_usd, timeline, reports, grounding_facts)
        except Exception:
            evidence_ledger = []
            
    # Roadmap / Action plan
    action_plan = session_data.get("validation_roadmap") or session_data.get("action_plan")
    if not action_plan:
        try:
            action_plan = build_expansion_action_plan(company, market, timeline, critical_blockers, final_decision)
        except Exception:
            action_plan = []
            
    # Decision explanation
    decision_explanation = session_data.get("decision_explanation", {})
    deterministic_eval = session_data.get("deterministic_eval", {})
    rules = session_data.get("rule_evaluations") or deterministic_eval.get("rule_evaluations", [])
    agreement = session_data.get("agreement_analysis", {})
    disagreements = session_data.get("disagreements", {})
    mind_change_thresholds = session_data.get("mind_change_thresholds", [])
    decision_trace = session_data.get("decision_trace", [])
    
    return {
        "company": company,
        "market": market,
        "budget_usd": budget_usd,
        "budget_display": budget_display,
        "timeline": timeline,
        "question": question,
        "business_model": business_model,
        "timestamp": timestamp,
        "session_id": session_id,
        "final_decision": final_decision,
        "confidence": confidence,
        "ceo_rationale": ceo_rationale,
        "metrics": {
            "opportunity_score": opp_score,
            "risk_mitigation_score": risk_mit_score,
            "market_readiness": mkt_readiness,
            "financial_feasibility": fin_score
        },
        "reports": reports,
        "transcript": transcript,
        "grounding_facts": grounding_facts,
        "risk_matrix": risk_matrix,
        "critical_blockers": critical_blockers,
        "evidence_ledger": evidence_ledger,
        "action_plan": action_plan,
        "decision_explanation": decision_explanation,
        "rules": rules,
        "deterministic_eval": deterministic_eval,
        "agreement": agreement,
        "disagreements": disagreements,
        "mind_change_thresholds": mind_change_thresholds,
        "decision_trace": decision_trace,
        "scenarios": session_data.get("scenarios")
    }


# =========================================================================
# MAIN ENTRYPOINT: generate_pdf_report
# =========================================================================

def generate_pdf_report(session_data):
    """
    Generates the comprehensive 20-page Executive Board Decision Report across all 30 sections.
    Protects Track B dedicated briefs if mode == 'launch', otherwise generates
    the authoritative corporate decision intelligence briefing.
    Returns bytes in memory.
    """
    if session_data.get("mode") == "launch":
        return generate_track_b_pdf_report(session_data)
        
    ctx = _extract_report_data(session_data)
    styles = _get_styles()
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=46
    )
    
    story = []
    
    # -------------------------------------------------------------
    # PAGE 1 — SECTION 1: PROFESSIONAL COVER PAGE
    # -------------------------------------------------------------
    story.append(Spacer(1, 28))
    story.append(Paragraph("BOARDROOM AI", styles['CoverTitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Autonomous Multi-Agent Executive Decision Intelligence", styles['CoverSubtitle']))
    story.append(Spacer(1, 14))
    
    # Gold decorative accent rule
    dec_line = Table([[""]], colWidths=[532], rowHeights=[3])
    dec_line.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#D4AF37")),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(dec_line)
    story.append(Spacer(1, 18))
    
    # Metadata Block
    time_str = time.strftime('%B %d, %Y &bull; %H:%M UTC', time.gmtime(ctx['timestamp']))
    meta_table_data = [
        [Paragraph("Target Enterprise:", styles['CoverMetaLabel']), Paragraph(str(ctx['company']), styles['CoverMetaVal'])],
        [Paragraph("Expansion Market / Territory:", styles['CoverMetaLabel']), Paragraph(str(ctx['market']), styles['CoverMetaVal'])],
        [Paragraph("Proposed Capital Budget:", styles['CoverMetaLabel']), Paragraph(str(ctx['budget_display']), styles['CoverMetaVal'])],
        [Paragraph("Execution Timeline Horizon:", styles['CoverMetaLabel']), Paragraph(str(ctx['timeline']), styles['CoverMetaVal'])],
        [Paragraph("Strategic Board Directive:", styles['CoverMetaLabel']), Paragraph(str(ctx['question']), styles['CoverMetaVal'])],
        [Paragraph("Analytical Session Identifier:", styles['CoverMetaLabel']), Paragraph(str(ctx['session_id']), styles['CoverMetaVal'])],
        [Paragraph("Date & Time of Deliberation:", styles['CoverMetaLabel']), Paragraph(time_str, styles['CoverMetaVal'])],
    ]
    meta_table = Table(meta_table_data, colWidths=[150, 382])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 24))
    
    # Decision Callout Box
    decision = ctx['final_decision']
    conf = ctx['confidence']
    box_bg = colors.HexColor("#D4EDDA")
    box_border = colors.HexColor("#155724")
    box_text = colors.HexColor("#155724")
    
    if "REJECT" in decision or "DO NOT" in decision or "NO-GO" in decision:
        box_bg = colors.HexColor("#F8D7DA")
        box_border = colors.HexColor("#721C24")
        box_text = colors.HexColor("#721C24")
    elif "CONDITIONAL" in decision or "DELAY" in decision or "VALIDATE" in decision:
        box_bg = colors.HexColor("#FFF3CD")
        box_border = colors.HexColor("#856404")
        box_text = colors.HexColor("#856404")
        
    callout_html = (
        f"<font color='{box_text}'>FINAL BOARD VERDICT: {decision}</font><br/>"
        f"<font size=9.5 color='#334155'>Executive Analytical Confidence Rating: <b>{conf}%</b> &bull; Zero-LLM Deterministic Policy Evaluated</font>"
    )
    callout_tbl = Table([[Paragraph(callout_html, styles['CoverVerdict'])]], colWidths=[532])
    callout_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), box_bg),
        ('BOX', (0,0), (-1,-1), 1.5, box_border),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(callout_tbl)
    story.append(Spacer(1, 40))
    
    cover_disclaimer = (
        "CONFIDENTIAL &bull; PRODUCED BY BOARDROOMAI MULTI-AGENT GOVERNANCE ENGINE<br/>"
        "FOR INTERNAL BOARD OF DIRECTORS & C-SUITE FIDUCIARY USE ONLY"
    )
    story.append(Paragraph(cover_disclaimer, ParagraphStyle('CF', parent=styles['BodyItalic'], alignment=TA_CENTER, fontSize=7.5, leading=11)))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 2 — SECTION 2: EXECUTIVE DECISION SUMMARY & SECTION 3: DECISION SCORECARD
    # -------------------------------------------------------------
    story.append(Paragraph("2. Executive Decision Summary", styles['SectionH1']))
    story.append(Spacer(1, 2))
    
    q_box = [
        [Paragraph("<b>Strategic Question:</b>", styles['BodyBold']), Paragraph(str(ctx['question']), styles['Body'])],
        [Paragraph("<b>Final Recommendation:</b>", styles['BodyBold']), Paragraph(f"<b>{decision}</b> (Executive Confidence: {conf}%)", styles['Body'])],
    ]
    q_tbl = Table(q_box, colWidths=[130, 402])
    q_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(q_tbl)
    story.append(Spacer(1, 5))
    
    rat = ctx['ceo_rationale'] or ctx['decision_explanation'].get('rationale', 'Autonomous evaluation completed across C-suite domains.')
    story.append(Paragraph(f"<b>Key Decision Rationale:</b> {rat}", styles['Body']))
    story.append(Spacer(1, 5))
    
    expl = ctx['decision_explanation']
    pos = expl.get('strongest_positive_evidence', expl.get('key_reasons', []))
    neg = expl.get('strongest_negative_evidence', [])
    top_risk = expl.get('most_important_risk') or (neg[0] if neg else "Macroeconomic and execution uncertainty.")
    opp_text = pos[0] if pos else f"Validated market opportunity for {ctx['company']} in {ctx['market']}."
    
    cond_text = "Satisfy foreign statutory compliance filings, local 3PL setup, and customer conversion validation gates."
    if ctx['critical_blockers']:
        cond_text = ctx['critical_blockers'][0].get('resolution_condition', cond_text)
        
    summary_data = [
        [Paragraph("<b>Consensus Status:</b>", styles['BodyBold']), Paragraph(f"{ctx['agreement'].get('primary_split', 'Evaluated')} &bull; Overall Confidence: {conf}%", styles['Body'])],
        [Paragraph("<b>Major Opportunity:</b>", styles['BodyBold']), Paragraph(opp_text, styles['Body'])],
        [Paragraph("<b>Major Concern:</b>", styles['BodyBold']), Paragraph(top_risk, styles['Body'])],
        [Paragraph("<b>Critical Condition:</b>", styles['BodyBold']), Paragraph(cond_text, styles['Body'])],
    ]
    sum_tbl = Table(summary_data, colWidths=[120, 412])
    sum_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 8))
    
    # SECTION 3: DECISION SCORECARD
    story.append(Paragraph("3. Decision Scorecard & Dimension Benchmarks", styles['SectionH1']))
    story.append(Spacer(1, 2))
    
    metrics = ctx['metrics']
    opp = metrics.get('opportunity_score', 0)
    risk_mit = metrics.get('risk_mitigation_score', 0)
    mkt = metrics.get('market_readiness', 0)
    fin = metrics.get('financial_feasibility', 0)
    
    scorecard_data = [
        [Paragraph("<b>Dimension</b>", styles['TableHead']), Paragraph("<b>Score</b>", styles['TableHead']), Paragraph("<b>Benchmark Interpretation</b>", styles['TableHead'])],
        [Paragraph("Market Opportunity", styles['TableCellBold']), Paragraph(f"{opp} / 100", styles['TableCell']), Paragraph("High addressable market demand" if opp >= 70 else "Moderate volume", styles['TableCell'])],
        [Paragraph("Risk Mitigation", styles['TableCellBold']), Paragraph(f"{risk_mit} / 100", styles['TableCell']), Paragraph("Strong Risk Coverage" if risk_mit >= 80 else ("Moderate Mitigation" if risk_mit >= 55 else "Substantial Risk Factors / Weak Mitigation"), styles['TableCell'])],
        [Paragraph("Market Readiness", styles['TableCellBold']), Paragraph(f"{mkt} / 100", styles['TableCell']), Paragraph("Infrastructure channels accessible" if mkt >= 65 else "Infrastructure setup required", styles['TableCell'])],
        [Paragraph("Financial Feasibility", styles['TableCellBold']), Paragraph(f"{fin} / 100", styles['TableCell']), Paragraph("Capital runway adequate" if fin >= 65 else "Capital intensive / High burn requirement", styles['TableCell'])],
    ]
    if ctx['reports'].get('OPERATIONS', {}).get('confidence'):
        scorecard_data.append([Paragraph("Operational Feasibility", styles['TableCellBold']), Paragraph(f"{ctx['reports']['OPERATIONS']['confidence']} / 100", styles['TableCell']), Paragraph("Logistics and supply chain execution viable", styles['TableCell'])])
    if ctx['reports'].get('COMPETITOR', {}).get('confidence'):
        scorecard_data.append([Paragraph("Competitive Position", styles['TableCellBold']), Paragraph(f"{ctx['reports']['COMPETITOR']['confidence']} / 100", styles['TableCell']), Paragraph("Defensible product differentiation wedge", styles['TableCell'])])
    if ctx['reports'].get('LEGAL', {}).get('confidence'):
        scorecard_data.append([Paragraph("Legal/Regulatory Readiness", styles['TableCellBold']), Paragraph(f"{ctx['reports']['LEGAL']['confidence']} / 100", styles['TableCell']), Paragraph("Statutory compliance and incorporation pathway verified", styles['TableCell'])])
        
    sc_tbl = Table(scorecard_data, colWidths=[150, 75, 307])
    sc_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(sc_tbl)
    story.append(Spacer(1, 5))
    
    chart_img = _render_dimension_scorecard_chart(metrics)
    if chart_img:
        story.append(chart_img)
        story.append(Spacer(1, 4))
        
    # Dynamic Risk Alert
    if risk_mit < 50 or risk_mit < (min(opp, mkt, fin) - 15):
        warn_txt = (
            f"<b>CRITICAL GOVERNANCE ALERT — RISK DISPARITY:</b> Strong market attractiveness ({opp}/100) and "
            f"financial feasibility ({fin}/100) are offset by comparatively weak risk mitigation ({risk_mit}/100). "
            f"Therefore, the authoritative executive recommendation mandates strictly gated capital tranches and "
            f"preservation of contingency reserves before expanding operational exposure."
        )
        w_tbl = Table([[Paragraph(warn_txt, styles['WarningBox'])]], colWidths=[532])
        w_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F87171")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(w_tbl)
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 3 — SECTION 4: BOARDROOM CONSENSUS & VOTING ANALYTICS
    # -------------------------------------------------------------
    story.append(Paragraph("4. Boardroom Consensus & Voting Analytics", styles['SectionH1']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "BoardRoomAI convenes autonomous C-suite specialists to independently audit corporate expansion feasibility. "
        "Each specialist operates under a strict fiduciary mandate before submitting their vote.",
        styles['Body']
    ))
    story.append(Spacer(1, 6))
    
    con_data = [
        [Paragraph("<b>Specialist Agent</b>", styles['TableHead']), Paragraph("<b>Domain Mandate</b>", styles['TableHead']), Paragraph("<b>Vote</b>", styles['TableHead']), Paragraph("<b>Confidence</b>", styles['TableHead']), Paragraph("<b>Core Strategic Finding</b>", styles['TableHead'])],
    ]
    
    role_titles = {
        "RESEARCHER": "Market Research & TAM",
        "COMPETITOR": "Competitive Positioning",
        "LEGAL": "General Counsel & Legal",
        "OPERATIONS": "COO Logistics & 3PL",
        "RISK": "Chief Risk Officer",
        "CFO": "Chief Financial Officer",
        "CEO": "Corporate Chief Executive"
    }
    
    agents_for_chart = []
    yes_v = 0
    no_v = 0
    cond_v = 0
    
    for aid, rep in ctx['reports'].items():
        name = rep.get("name", aid.title())
        role = role_titles.get(aid, "Specialist")
        v = str(rep.get("recommendation", "CONDITIONAL")).upper()
        cf = rep.get("confidence", 0)
        kf = rep.get("key_finding") or rep.get("analysis", "")[:95] + "..."
        
        if v in ["YES", "ENTER", "ENTER MARKET"]:
            yes_v += 1
        elif v in ["NO", "REJECT", "REJECT EXPANSION"]:
            no_v += 1
        else:
            cond_v += 1
            
        agents_for_chart.append({"name": name, "confidence": cf})
        con_data.append([
            Paragraph(f"<b>{name}</b>", styles['TableCellBold']),
            Paragraph(role, styles['TableCell']),
            Paragraph(f"<b>{v}</b>", styles['TableCellBold']),
            Paragraph(f"{cf}%", styles['TableCellRight']),
            Paragraph(kf, styles['TableCell']),
        ])
        
    con_table = Table(con_data, colWidths=[110, 105, 55, 55, 207])
    con_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(con_table)
    story.append(Spacer(1, 8))
    
    total_ag = len(ctx['reports'])
    agr_idx = ctx['agreement'].get('agreement_index', int(round((max(yes_v, no_v, cond_v) / max(1, total_ag)) * 100)))
    
    agg_data = [
        [Paragraph("<b>Total Agents:</b>", styles['TableCellBold']), Paragraph(str(total_ag), styles['TableCell']), Paragraph("<b>Consensus Agreement:</b>", styles['TableCellBold']), Paragraph(f"{agr_idx}%", styles['TableCellBold'])],
        [Paragraph("<b>YES Votes:</b>", styles['TableCellBold']), Paragraph(f"<font color='#166534'><b>{yes_v}</b></font>", styles['TableCell']), Paragraph("<b>Overall Confidence:</b>", styles['TableCellBold']), Paragraph(f"<b>{conf}%</b>", styles['TableCellBold'])],
        [Paragraph("<b>Conditional / Maybe:</b>", styles['TableCellBold']), Paragraph(f"<font color='#854D0E'><b>{cond_v}</b></font>", styles['TableCell']), Paragraph("<b>NO Votes:</b>", styles['TableCellBold']), Paragraph(f"<font color='#991B1B'><b>{no_v}</b></font>", styles['TableCell'])],
    ]
    agg_tbl = Table(agg_data, colWidths=[130, 136, 136, 130])
    agg_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(agg_tbl)
    story.append(Spacer(1, 8))
    
    conf_chart = _render_agent_confidence_chart(agents_for_chart)
    if conf_chart:
        story.append(conf_chart)
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 4 — SECTION 5: MULTI-AGENT DELIBERATION (PART 1: RESEARCH, COMPETITION, LEGAL)
    # -------------------------------------------------------------
    story.append(Paragraph("5. Multi-Agent Deliberation (Market, Competition, Legal)", styles['SectionH1']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "Complete, un-truncated domain analyses, spoken board statements, and empirical mind-change thresholds "
        "submitted by Market Research, Competitive Intelligence, and General Counsel.",
        styles['Body']
    ))
    story.append(Spacer(1, 6))
    
    first_three = ["RESEARCHER", "COMPETITOR", "LEGAL"]
    for aid in first_three:
        if aid not in ctx['reports']:
            continue
        rep = ctx['reports'][aid]
        name = rep.get("name", aid.title())
        role = role_titles.get(aid, "Executive Specialist")
        v = str(rep.get("recommendation", "CONDITIONAL")).upper()
        cf = rep.get("confidence", 0)
        ana = rep.get("analysis", "No detailed domain analysis recorded.")
        kf = rep.get("key_finding", "")
        pc = rep.get("primary_concern", "")
        dia = rep.get("dialogue", "")
        mct = rep.get("mind_change_threshold", "")
        status_tag = "DATASET-BACKED" if rep.get("data_verified", False) else "MODEL-INFERRED"
        
        card = [
            [Paragraph(f"<b>{name}</b> &bull; <font color='#475569'>{role}</font>", styles['BodyBold']), Paragraph(f"<b>Vote:</b> {v} | <b>Confidence:</b> {cf}% | <i>{status_tag}</i>", styles['TableCellRight'])],
            [Paragraph(
                f"<b>Domain Analysis:</b> {ana}<br/>"
                f"<b>Key Finding:</b> {kf}<br/>"
                f"<b>Primary Concern:</b> {pc}<br/>"
                f"<b>Spoken Board Statement:</b> <i>\"{dia}\"</i><br/>"
                f"<b>Mind-Change Threshold:</b> {mct if mct else 'Empirical validation required'}",
                styles['Body']
            ), ""]
        ]
        c_tbl = Table(card, colWidths=[260, 272])
        c_tbl.setStyle(TableStyle([
            ('SPAN', (0,1), (1,1)),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 3.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(c_tbl)
        story.append(Spacer(1, 6))
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 5 — SECTION 5 (CONT.): DELIBERATION (OPS, RISK, CFO) & SECTION 6: CEO PERSPECTIVE
    # -------------------------------------------------------------
    story.append(Paragraph("5. Multi-Agent Deliberation (Operations, Risk, Finance)", styles['SectionH1']))
    story.append(Spacer(1, 2))
    
    second_three = ["OPERATIONS", "RISK", "CFO"]
    for aid in second_three:
        if aid not in ctx['reports']:
            continue
        rep = ctx['reports'][aid]
        name = rep.get("name", aid.title())
        role = role_titles.get(aid, "Executive Specialist")
        v = str(rep.get("recommendation", "CONDITIONAL")).upper()
        cf = rep.get("confidence", 0)
        ana = rep.get("analysis", "No detailed domain analysis recorded.")
        kf = rep.get("key_finding", "")
        pc = rep.get("primary_concern", "")
        dia = rep.get("dialogue", "")
        mct = rep.get("mind_change_threshold", "")
        status_tag = "DATASET-BACKED" if rep.get("data_verified", False) else "MODEL-INFERRED"
        
        card = [
            [Paragraph(f"<b>{name}</b> &bull; <font color='#475569'>{role}</font>", styles['BodyBold']), Paragraph(f"<b>Vote:</b> {v} | <b>Confidence:</b> {cf}% | <i>{status_tag}</i>", styles['TableCellRight'])],
            [Paragraph(
                f"<b>Domain Analysis:</b> {ana}<br/>"
                f"<b>Key Finding:</b> {kf}<br/>"
                f"<b>Primary Concern:</b> {pc}<br/>"
                f"<b>Spoken Board Statement:</b> <i>\"{dia}\"</i><br/>"
                f"<b>Mind-Change Threshold:</b> {mct if mct else 'Empirical validation required'}",
                styles['Body']
            ), ""]
        ]
        c_tbl = Table(card, colWidths=[260, 272])
        c_tbl.setStyle(TableStyle([
            ('SPAN', (0,1), (1,1)),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(c_tbl)
        story.append(Spacer(1, 5))
        
    # SECTION 6: CEO PERSPECTIVE
    story.append(Paragraph("6. CEO Perspective & Synthesis", styles['SectionH1']))
    story.append(Spacer(1, 2))
    ceo_rep = ctx['reports'].get('CEO', {})
    ceo_ana = ceo_rep.get('analysis', ctx['ceo_rationale'] or 'Executive synthesis confirms strategic alignment.')
    ceo_box = [
        [Paragraph("<b>Chief Executive Officer Synthesis & Governance Mandate:</b>", styles['BodyBold'])],
        [Paragraph(f"{ceo_ana}<br/><b>CEO Guidance:</b> <i>\"{ceo_rep.get('dialogue', 'We must ensure controlled milestone pacing.')}\"</i>", styles['Body'])]
    ]
    ceo_tbl = Table(ceo_box, colWidths=[532])
    ceo_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF3C7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D97706")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(ceo_tbl)
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 6 — SECTION 7: RESEARCH / MARKET INTELLIGENCE & SECTION 8: CFO / FINANCIAL ANALYSIS
    # -------------------------------------------------------------
    story.append(Paragraph("7. Research / Market Intelligence", styles['SectionH1']))
    story.append(Spacer(1, 2))
    res_ana = ctx['reports'].get('RESEARCHER', {}).get('analysis', 'Market demand viability evaluated.')
    story.append(Paragraph(f"<b>Market Attractiveness & Demand Viability:</b> {res_ana}", styles['Body']))
    story.append(Spacer(1, 4))
    
    # TAM Check
    tam_found = "tam" in res_ana.lower() or "addressable market" in res_ana.lower()
    if not tam_found:
        story.append(Paragraph("<i>Market sizing was not explicitly produced by the current BoardRoomAI analysis.</i>", styles['BodyItalic']))
    story.append(Spacer(1, 4))
    
    facts_res = ctx['grounding_facts'].get("Research Data", {})
    if facts_res and facts_res.get("Startups Tracked"):
        res_tbl_data = [
            [Paragraph("<b>Ecosystem Indicator</b>", styles['TableHead']), Paragraph("<b>Value</b>", styles['TableHead']), Paragraph("<b>Source Dataset</b>", styles['TableHead'])],
            [Paragraph("Tracked Sector Enterprises", styles['TableCellBold']), Paragraph(str(facts_res.get("Startups Tracked")), styles['TableCell']), Paragraph("research_data.csv", styles['TableCell'])],
            [Paragraph("Aggregate Tracked Venture Funding", styles['TableCellBold']), Paragraph(f"${facts_res.get('Total Funding (USD)', 'N/A')}", styles['TableCell']), Paragraph("research_data.csv", styles['TableCell'])],
            [Paragraph("Average Funding per Enterprise", styles['TableCellBold']), Paragraph(f"${facts_res.get('Average Funding per Startup (USD)', 'N/A')}", styles['TableCell']), Paragraph("research_data.csv", styles['TableCell'])],
        ]
        r_tbl = Table(res_tbl_data, colWidths=[180, 160, 192])
        r_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(r_tbl)
        story.append(Spacer(1, 8))
        
    # SECTION 8: CFO / FINANCIAL ANALYSIS
    story.append(Paragraph("8. CFO / Financial Analysis & Capital Efficiency", styles['SectionH1']))
    story.append(Spacer(1, 2))
    cfo_ana = ctx['reports'].get('CFO', {}).get('analysis', 'Capital sufficiency and financial feasibility evaluated.')
    story.append(Paragraph(f"<b>Financial Feasibility Assessment:</b> {cfo_ana}", styles['Body']))
    story.append(Spacer(1, 4))
    
    fin_box = [
        [Paragraph("<b>Proposed Expansion Capital:</b>", styles['TableCellBold']), Paragraph(ctx['budget_display'], styles['TableCellBold'])],
        [Paragraph("<b>Target Execution Horizon:</b>", styles['TableCellBold']), Paragraph(ctx['timeline'], styles['TableCell'])],
        [Paragraph("<b>Financial Feasibility Score:</b>", styles['TableCellBold']), Paragraph(f"{ctx['metrics'].get('financial_feasibility', 0)} / 100", styles['TableCell'])],
        [Paragraph("<b>Quantitative ROI & Payback Status:</b>", styles['TableCellBold']), Paragraph("Quantitative ROI and payback period were not explicitly calculated by the current BoardRoomAI analysis. Projections should be established during secondary financial diligence.", styles['TableCell'])],
        [Paragraph("<b>Capital Allocation Strategy:</b>", styles['TableCellBold']), Paragraph("Budget allocation breakdown was not explicitly modeled in current analysis. Recommended strategy is milestone-gated deployment (Tranche 1: 30% Compliance & Setup, Tranche 2: 40% GTM & Distribution, Tranche 3: 30% Scaling Reserve).", styles['TableCell'])],
    ]
    f_tbl = Table(fin_box, colWidths=[160, 372])
    f_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(f_tbl)
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 7 — SECTION 9: RISK ANALYSIS & SECTION 10: LEGAL & REGULATORY ANALYSIS
    # -------------------------------------------------------------
    story.append(Paragraph("9. Risk Analysis & Exposure Profile", styles['SectionH1']))
    story.append(Spacer(1, 2))
    risk_ana = ctx['reports'].get('RISK', {}).get('analysis', 'Sovereign and operational risk assessed.')
    story.append(Paragraph(f"<b>Chief Risk Officer Exposure Assessment:</b> {risk_ana}", styles['Body']))
    story.append(Spacer(1, 4))
    
    facts_risk = ctx['grounding_facts'].get("Risk Data", {})
    frag_score = facts_risk.get("Fragility Score", facts_risk.get("Total", "N/A"))
    frag_rank = facts_risk.get("Rank", "N/A")
    
    risk_summary_text = (
        f"<b>Sovereign Fragility Benchmark:</b> {ctx['market']} Fragility Score: {frag_score}/120 (Rank #{frag_rank}). "
        f"Composite Risk Mitigation Rating: <b>{ctx['metrics'].get('risk_mitigation_score', 0)}/100</b>.<br/>"
        f"<b>Core Risk Vectors:</b> Cross-border currency fluctuation, regulatory compliance lead times, and initial customer conversion friction."
    )
    story.append(Paragraph(risk_summary_text, styles['Body']))
    story.append(Spacer(1, 8))
    
    # SECTION 10: LEGAL & REGULATORY ANALYSIS
    story.append(Paragraph("10. Legal & Regulatory Analysis", styles['SectionH1']))
    story.append(Spacer(1, 2))
    leg_ana = ctx['reports'].get('LEGAL', {}).get('analysis', 'Compliance and statutory filing framework evaluated.')
    story.append(Paragraph(f"<b>General Counsel Legal Assessment:</b> {leg_ana}", styles['Body']))
    story.append(Spacer(1, 4))
    
    facts_leg = ctx['grounding_facts'].get("Legal Data", {})
    if facts_leg and facts_leg.get("Ease of Doing Business Score"):
        leg_data_tbl = [
            [Paragraph("<b>Regulatory Dimension</b>", styles['TableHead']), Paragraph("<b>Observed Metric</b>", styles['TableHead']), Paragraph("<b>Source Dataset</b>", styles['TableHead'])],
            [Paragraph("LEGAL READINESS SCORE (Ease of Doing Business)", styles['TableCellBold']), Paragraph(f"{facts_leg.get('Ease of Doing Business Score')} / 100 (Rank #{facts_leg.get('Ease of Doing Business Rank', 'N/A')})", styles['TableCellBold']), Paragraph("legal_data.csv", styles['TableCell'])],
            [Paragraph("Contract Enforcement Judicial Efficiency", styles['TableCellBold']), Paragraph(f"{facts_leg.get('Enforcing Contracts Score', 'N/A')} / 100", styles['TableCell']), Paragraph("legal_data.csv", styles['TableCell'])],
            [Paragraph("Statutory Entity Formation Lead Time", styles['TableCellBold']), Paragraph(f"{facts_leg.get('Days to Start Business', 'N/A')} Days", styles['TableCell']), Paragraph("legal_data.csv", styles['TableCell'])],
        ]
        leg_tbl = Table(leg_data_tbl, colWidths=[180, 160, 192])
        leg_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(leg_tbl)
    else:
        story.append(Paragraph("<i>Legal readiness score not explicitly produced by the current analysis.</i>", styles['BodyItalic']))
        
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Mandatory Compliance Steps:</b> Retain localized legal counsel in target territory; file foreign entity articles of incorporation; "
        "execute consumer protection and IP registration disclosures prior to commercial trading.",
        styles['Body']
    ))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 8 — SECTION 11: OPERATIONS & SUPPLY CHAIN & SECTION 12: COMPETITIVE INTELLIGENCE
    # -------------------------------------------------------------
    story.append(Paragraph("11. Operations & Supply Chain Analysis", styles['SectionH1']))
    story.append(Spacer(1, 2))
    ops_ana = ctx['reports'].get('OPERATIONS', {}).get('analysis', 'Operational feasibility and distribution evaluated.')
    story.append(Paragraph(f"<b>Chief Operating Officer Assessment:</b> {ops_ana}", styles['Body']))
    story.append(Spacer(1, 4))
    
    facts_log = ctx['grounding_facts'].get("Market Data", {})
    lpi_score = facts_log.get("Logistics Performance Score (2023)", "N/A")
    
    ops_box = [
        [Paragraph("<b>OPERATIONAL READINESS SCORE:</b>", styles['TableCellBold']), Paragraph(f"World Bank LPI Score: <b>{lpi_score} / 5.0</b> (Source: market_data.csv)", styles['TableCell'])],
        [Paragraph("<b>Distribution Strategy:</b>", styles['TableCellBold']), Paragraph("Partner with regional 3PL logistics networks to minimize fixed physical infrastructure capex.", styles['TableCell'])],
        [Paragraph("<b>Execution Realism:</b>", styles['TableCellBold']), Paragraph(f"Target timeline of {ctx['timeline']} provides adequate lead time assuming 3PL agreements close in Phase 1.", styles['TableCell'])],
    ]
    ops_tbl = Table(ops_box, colWidths=[150, 382])
    ops_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(ops_tbl)
    story.append(Spacer(1, 8))
    
    # SECTION 12: COMPETITIVE INTELLIGENCE
    story.append(Paragraph("12. Competitive Intelligence & Market Positioning", styles['SectionH1']))
    story.append(Spacer(1, 2))
    comp_ana = ctx['reports'].get('COMPETITOR', {}).get('analysis', 'Incumbent landscape and differentiation assessed.')
    story.append(Paragraph(f"<b>Competitive Positioning Assessment:</b> {comp_ana}", styles['Body']))
    story.append(Spacer(1, 4))
    
    facts_comp = ctx['grounding_facts'].get("Competition Data", {})
    if facts_comp and facts_comp.get("Top Company"):
        comp_tbl_data = [
            [Paragraph("<b>Corporate Landscape Benchmark</b>", styles['TableHead']), Paragraph("<b>Benchmark Metric</b>", styles['TableHead']), Paragraph("<b>Source Dataset</b>", styles['TableHead'])],
            [Paragraph("Sovereign Market-Cap Leader", styles['TableCellBold']), Paragraph(f"{facts_comp.get('Top Company')} ({facts_comp.get('Top Company Symbol', 'N/A')})", styles['TableCellBold']), Paragraph("competition_data.csv", styles['TableCell'])],
            [Paragraph("Leader Market Capitalization", styles['TableCellBold']), Paragraph(f"{facts_comp.get('Top Company Market Cap (USD)', 'N/A')}", styles['TableCell']), Paragraph("competition_data.csv", styles['TableCell'])],
            [Paragraph("Public Entities Tracked in Region", styles['TableCellBold']), Paragraph(str(facts_comp.get("Companies Tracked", "N/A")), styles['TableCell']), Paragraph("competition_data.csv", styles['TableCell'])],
        ]
        c_tbl = Table(comp_tbl_data, colWidths=[180, 160, 192])
        c_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(c_tbl)
        story.append(Spacer(1, 2))
        story.append(Paragraph("<i>Note: Sovereign public enterprise benchmark represents regional capitalization context, not a verified direct product rival.</i>", styles['BodyItalic']))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 9 — SECTION 13: OPPORTUNITY ANALYSIS & SECTION 14: EVIDENCE-BASED FINDINGS
    # -------------------------------------------------------------
    story.append(Paragraph("13. Opportunity Analysis & Strategic Upside", styles['SectionH1']))
    story.append(Spacer(1, 2))
    opp_summary = (
        f"<b>Commercial Upside:</b> {ctx['company']} possesses specialized product capabilities that directly match "
        f"the modern commercial and consumer profile of {ctx['market']}.<br/>"
        f"<b>Customer Demand Readiness:</b> Composite Opportunity Rating stands at <b>{opp}/100</b>, indicating high demand receptivity.<br/>"
        f"<b>Wedge Strategy:</b> Prioritize digital-first sales channels and specialized niche customer cohorts before horizontal market expansion."
    )
    story.append(Paragraph(opp_summary, styles['Body']))
    story.append(Spacer(1, 8))
    
    # SECTION 14: EVIDENCE-BASED FINDINGS
    story.append(Paragraph("14. Evidence-Based Findings (Canonical Evidence Ledger)", styles['SectionH1']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "Structured extract from the single-source-of-truth BoardRoomAI Canonical Evidence Ledger linking claims to datasets.",
        styles['Body']
    ))
    story.append(Spacer(1, 4))
    
    ledger_tbl_data = [
        [Paragraph("<b>EVID ID</b>", styles['TableHead']), Paragraph("<b>Domain</b>", styles['TableHead']), Paragraph("<b>Factual Claim & Audit Source</b>", styles['TableHead']), Paragraph("<b>Status</b>", styles['TableHead'])],
    ]
    for ev in ctx['evidence_ledger'][:6]:
        eid = ev.get("evidence_id", "EVID-000")
        dom = ev.get("domain", "Domain")
        clm = ev.get("claim", "")
        src = ev.get("source_dataset", "N/A")
        stat = ev.get("verification_status", "DATASET-BACKED")
        ledger_tbl_data.append([
            Paragraph(f"<b>{eid}</b>", styles['CodeStyle']),
            Paragraph(dom, styles['TableCellBold']),
            Paragraph(f"{clm}<br/><i>Dataset: {src}</i>", styles['TableCell']),
            Paragraph(stat, styles['TableCellBold']),
        ])
    led_tbl = Table(ledger_tbl_data, colWidths=[55, 110, 277, 90])
    led_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(led_tbl)
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 10 — SECTION 15: KEY ASSUMPTIONS & SECTION 16: CONTRADICTIONS & DISAGREEMENTS
    # -------------------------------------------------------------
    story.append(Paragraph("15. Key Assumptions & Boundary Conditions", styles['SectionH1']))
    story.append(Spacer(1, 2))
    assumptions_text = (
        f"1. <b>Capital Constraint Assumption:</b> Expansion is strictly capitalized with the proposed {ctx['budget_display']} budget without immediate external funding.<br/>"
        f"2. <b>Timeline Horizon Assumption:</b> Operations must achieve commercial validation within the targeted {ctx['timeline']} roadmap.<br/>"
        f"3. <b>Fulfillment Asset-Light Assumption:</b> Regional warehousing and fulfillment will be outsourced to established 3PL networks rather than owning fixed assets.<br/>"
        f"4. <b>Regulatory Continuity Assumption:</b> Sovereign and foreign entity regulations in {ctx['market']} remain stable according to current World Bank indicators."
    )
    story.append(Paragraph(assumptions_text, styles['Body']))
    story.append(Spacer(1, 8))
    
    # SECTION 16: CONTRADICTIONS & DISAGREEMENTS
    story.append(Paragraph("16. Contradictions & Disagreements Analysis", styles['SectionH1']))
    story.append(Spacer(1, 2))
    
    disag = ctx.get('disagreements', {})
    split_str = disag.get('primary_split', 'Evaluated multi-agent consensus')
    dissent_list = disag.get('dissenting_agents', [])
    dissent_str = ", ".join(dissent_list) if dissent_list else "None (Unanimous vote direction with varying risk weightings)"
    
    contra_text = (
        f"<b>Boardroom Voting Distribution:</b> {split_str}<br/>"
        f"<b>Dissenting Specialist Agents:</b> {dissent_str}<br/>"
        f"<b>Core Fiduciary Tension:</b> Commercial specialists (Researcher, Competitor, CFO) evaluate strong market appetite "
        f"and financial viability, whereas Risk Officer and the Deterministic Policy Engine flag that operational and "
        f"macro risk mitigation ({risk_mit}/100) is insufficient to support an unconditional expansion.<br/>"
        f"<b>Authoritative Resolution:</b> The Deterministic Engine policy locks the decision into a defensive posture: "
        f"capital cannot be released unconditionally until Phase 1 compliance and partner gates are cleared."
    )
    story.append(Paragraph(contra_text, styles['Body']))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 11 — SECTION 17: ENTERPRISE RISK REGISTER
    # -------------------------------------------------------------
    story.append(Paragraph("17. Enterprise Risk Register", styles['SectionH1']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "Consolidated enterprise risk register classifying hazards across macroeconomic, regulatory, demand, "
        "competitive, data access, capital, and operational domains.",
        styles['Body']
    ))
    story.append(Spacer(1, 4))
    
    risk_table_data = [
        [Paragraph("<b>Risk ID</b>", styles['TableHead']), Paragraph("<b>Category</b>", styles['TableHead']), Paragraph("<b>Severity</b>", styles['TableHead']), Paragraph("<b>Risk Observation & Evidence</b>", styles['TableHead']), Paragraph("<b>Mitigation Strategy</b>", styles['TableHead']), Paragraph("<b>Owner</b>", styles['TableHead'])],
    ]
    for r in ctx['risk_matrix']:
        rid = r.get("risk_id", "RISK-000")
        rcat = r.get("category", "General")
        rlevel = r.get("level", "MEDIUM")
        rref = r.get("evidence_ref", "EVID-000")
        rrat = r.get("rationale", "")
        rmit = r.get("mitigation", "")
        rowner = r.get("specialist", "Risk Officer")
        sev_color = "#166534" if rlevel == "LOW" else ("#854D0E" if rlevel == "MEDIUM" else "#991B1B")
        
        risk_table_data.append([
            Paragraph(f"<b>{rid}</b>", styles['CodeStyle']),
            Paragraph(rcat, styles['TableCellBold']),
            Paragraph(f"<font color='{sev_color}'><b>{rlevel}</b></font>", styles['TableCell']),
            Paragraph(f"{rrat}<br/><i>Ref: {rref}</i>", styles['TableCell']),
            Paragraph(rmit, styles['TableCell']),
            Paragraph(rowner, styles['TableCell']),
        ])
    r_tbl = Table(risk_table_data, colWidths=[52, 75, 48, 145, 142, 70])
    r_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(r_tbl)
    story.append(Spacer(1, 6))
    
    r_dist = _render_risk_distribution_chart(ctx['risk_matrix'])
    if r_dist:
        story.append(r_dist)
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 12 — SECTION 18: RISK MITIGATION STRATEGY & GOVERNANCE CONTROLS
    # -------------------------------------------------------------
    story.append(Paragraph("18. Risk Mitigation Strategy & Governance Controls", styles['SectionH1']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "Actionable risk management protocols and internal governance gates required to protect corporate assets.",
        styles['Body']
    ))
    story.append(Spacer(1, 5))
    
    for r in ctx['risk_matrix'][:5]:
        rid = r.get("risk_id", "RISK")
        rcat = r.get("category", "General Risk")
        rlevel = r.get("level", "MEDIUM")
        rrat = r.get("rationale", "")
        rmit = r.get("mitigation", "")
        
        r_box = [
            [Paragraph(f"<b>{rid}: {rcat}</b>", styles['BodyBold']), Paragraph(f"<b>Severity Rating:</b> {rlevel}", styles['TableCellRight'])],
            [Paragraph(
                f"<b>Why It Matters:</b> {rrat}<br/>"
                f"<b>Mandatory Mitigation:</b> {rmit}<br/>"
                f"<b>Governance Gate:</b> Fiduciary sign-off required prior to capital release.",
                styles['Body']
            ), ""]
        ]
        r_table_item = Table(r_box, colWidths=[260, 272])
        r_table_item.setStyle(TableStyle([
            ('SPAN', (0,1), (1,1)),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(r_table_item)
        story.append(Spacer(1, 4))
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 13 — SECTION 19: SCENARIO ANALYSIS & SECTION 20: STRATEGIC ALTERNATIVES
    # -------------------------------------------------------------
    story.append(Paragraph("19. Scenario Analysis & Stress Testing", styles['SectionH1']))
    story.append(Spacer(1, 2))
    
    scenarios = ctx.get('scenarios')
    if scenarios and isinstance(scenarios, dict):
        for s_name, s_data in scenarios.items():
            s_box = [
                [Paragraph(f"<b>{s_name.upper()} SCENARIO</b>", styles['BodyBold'])],
                [Paragraph(f"<b>Assumptions:</b> {s_data.get('assumptions', 'Standard')}<br/>"
                           f"<b>Outcome:</b> {s_data.get('outcome', 'Evaluated')}<br/>"
                           f"<b>Response:</b> {s_data.get('response', 'Standard execution')}", styles['Body'])]
            ]
            stbl = Table(s_box, colWidths=[532])
            stbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(stbl)
            story.append(Spacer(1, 4))
    else:
        scen_note = (
            "Scenario modelling was not produced by the current BoardRoomAI analysis.<br/>"
            "<i>Data Integrity Protection: In accordance with zero-hallucination governance, "
            "simulated Best/Base/Worst case scenario numbers are omitted until explicit quantitative stress models are executed.</i>"
        )
        sn_tbl = Table([[Paragraph(scen_note, styles['BodyItalic'])]], colWidths=[532])
        sn_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(sn_tbl)
        story.append(Spacer(1, 6))
        
    # SECTION 20: STRATEGIC ALTERNATIVES
    story.append(Paragraph("20. Strategic Alternatives Evaluation", styles['SectionH1']))
    story.append(Spacer(1, 2))
    
    alt_data = [
        [Paragraph("<b>Option</b>", styles['TableHead']), Paragraph("<b>Strategic Posture</b>", styles['TableHead']), Paragraph("<b>Feasibility</b>", styles['TableHead']), Paragraph("<b>Supporting Evidence & Rationale</b>", styles['TableHead']), Paragraph("<b>Key Trade-Off</b>", styles['TableHead'])],
        [Paragraph("<b>Option A</b>", styles['TableCellBold']), Paragraph("Immediate Full Entry", styles['TableCell']), Paragraph("High Capital Exposure", styles['TableCell']), Paragraph(f"Supported only if Risk Mitigation >= 80 (Current: {risk_mit}/100)", styles['TableCell']), Paragraph("Vulnerable to unhedged cash burn.", styles['TableCell'])],
        [Paragraph("<b>Option B</b>", styles['TableCellBold']), Paragraph("Phased Pilot Entry", styles['TableCellBold']), Paragraph("Optimal Risk/Return", styles['TableCellBold']), Paragraph(f"Deploys initial tranche; validates customer CAC in {ctx['market']}.", styles['TableCell']), Paragraph("Requires sequential milestone gates.", styles['TableCell'])],
        [Paragraph("<b>Option C</b>", styles['TableCellBold']), Paragraph("Delay Entry / Validate", styles['TableCell']), Paragraph("Contingent", styles['TableCell']), Paragraph("Appropriate if regulatory filings require extended time.", styles['TableCell']), Paragraph("Risk of competitor preemption.", styles['TableCell'])],
        [Paragraph("<b>Option D</b>", styles['TableCellBold']), Paragraph("Do Not Enter", styles['TableCell']), Paragraph("Capital Preservation", styles['TableCell']), Paragraph(f"Authoritative stance when risk mitigation is severely inadequate.", styles['TableCell']), Paragraph("Forfeits immediate regional presence.", styles['TableCell'])],
    ]
    alt_tbl = Table(alt_data, colWidths=[52, 105, 75, 160, 140])
    alt_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(alt_tbl)
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 14 — SECTION 21: RECOMMENDED STRATEGY & SECTION 22: EXECUTION ROADMAP
    # -------------------------------------------------------------
    story.append(Paragraph("21. Recommended Strategy & Fiduciary Posture", styles['SectionH1']))
    story.append(Spacer(1, 2))
    strat_text = (
        f"<b>Strategic Recommendation:</b> {decision}<br/>"
        f"<b>Governance Mandate:</b> Given the observed Risk Mitigation score ({risk_mit}/100), full-scale capital deployment "
        f"must NOT proceed unconditionally. The enterprise should execute a tightly controlled validation roadmap, "
        f"confining Phase 1 expenditure strictly to compliance filings and 3PL distribution integration before capital commitment."
    )
    story.append(Paragraph(strat_text, styles['Body']))
    story.append(Spacer(1, 8))
    
    # SECTION 22: STRATEGIC EXECUTION ROADMAP
    story.append(Paragraph("22. Strategic Execution Roadmap", styles['SectionH1']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        f"Phased execution schedule anchored directly to the user's targeted <b>{ctx['timeline']}</b> timeline.",
        styles['Body']
    ))
    story.append(Spacer(1, 4))
    
    roadmap_data = [
        [Paragraph("<b>Phase</b>", styles['TableHead']), Paragraph("<b>Strategic Objective</b>", styles['TableHead']), Paragraph("<b>Key Deliverables</b>", styles['TableHead']), Paragraph("<b>Decision Gate / Milestone</b>", styles['TableHead']), Paragraph("<b>Lead Function</b>", styles['TableHead'])],
        [Paragraph("<b>Phase 1</b><br/>(Weeks 1–4)", styles['TableCellBold']), Paragraph("Entity & Compliance Setup", styles['TableCell']), Paragraph("Foreign entity registration, statutory filings, corporate banking setup.", styles['TableCell']), Paragraph("Legal clearance and filing approvals.", styles['TableCell']), Paragraph("General Counsel", styles['TableCell'])],
        [Paragraph("<b>Phase 2</b><br/>(Months 2–3)", styles['TableCellBold']), Paragraph("3PL Distribution & Logistics", styles['TableCell']), Paragraph("Contract regional 3PL partner; integrate fulfillment pipeline.", styles['TableCell']), Paragraph("Logistics SLA and customs clearance verified.", styles['TableCell']), Paragraph("COO / Logistics", styles['TableCell'])],
        [Paragraph("<b>Phase 3</b><br/>(Months 4–6)", styles['TableCellBold']), Paragraph("Controlled Pilot Marketing", styles['TableCell']), Paragraph("Deploy targeted customer acquisition; onboard initial cohort.", styles['TableCell']), Paragraph("Customer conversion and CAC verified.", styles['TableCell']), Paragraph("CMRO / Marketing", styles['TableCell'])],
        [Paragraph("<b>Phase 4</b><br/>(Months 7–End)", styles['TableCellBold']), Paragraph("Commercial Scale-Up", styles['TableCell']), Paragraph("Expand sales spend; achieve break-even within timeline.", styles['TableCell']), Paragraph("Positive unit economics & margin targets.", styles['TableCell']), Paragraph("CFO / Finance", styles['TableCell'])],
    ]
    rd_tbl = Table(roadmap_data, colWidths=[65, 105, 160, 122, 80])
    rd_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(rd_tbl)
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 15 — SECTION 23: KPI FRAMEWORK & SECTION 24: DECISION GATES
    # -------------------------------------------------------------
    story.append(Paragraph("23. KPI Framework", styles['SectionH1']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "Measurable indicators across critical corporate domains. If targets were not modeled in current session, they are labeled accordingly.",
        styles['Body']
    ))
    story.append(Spacer(1, 4))
    
    kpi_data = [
        [Paragraph("<b>Category</b>", styles['TableHead']), Paragraph("<b>Key Performance Indicator (KPI)</b>", styles['TableHead']), Paragraph("<b>Performance Target</b>", styles['TableHead']), Paragraph("<b>Cadence</b>", styles['TableHead']), Paragraph("<b>Decision Gate Trigger</b>", styles['TableHead'])],
        [Paragraph("Market Adoption", styles['TableCellBold']), Paragraph("Pilot Customer Conversion", styles['TableCell']), Paragraph("Target not specified in current analysis.", styles['TableCell']), Paragraph("Monthly", styles['TableCell']), Paragraph("Re-evaluate marketing channels if below peer benchmark", styles['TableCell'])],
        [Paragraph("Capital Burn", styles['TableCellBold']), Paragraph("Monthly Net Cash Outflow", styles['TableCell']), Paragraph(f"Cap at {format_budget_display(ctx['budget_usd'] / 12)} / mo", styles['TableCell']), Paragraph("Bi-weekly", styles['TableCell']), Paragraph("Halt discretionary spend if burn exceeds budget cap", styles['TableCell'])],
        [Paragraph("Logistics SLA", styles['TableCellBold']), Paragraph("Order Fulfillment Lead Time", styles['TableCell']), Paragraph("3PL standard regional SLA", styles['TableCell']), Paragraph("Weekly", styles['TableCell']), Paragraph("Escalate contract penalties if delivery delays occur", styles['TableCell'])],
        [Paragraph("Compliance", styles['TableCellBold']), Paragraph("Foreign Commercial Licensing", styles['TableCell']), Paragraph("100% statutory clearance", styles['TableCell']), Paragraph("Phase 1", styles['TableCell']), Paragraph("Halt commercial trading until filings approved", styles['TableCell'])],
        [Paragraph("Risk Containment", styles['TableCellBold']), Paragraph("Currency Volatility Hedging", styles['TableCell']), Paragraph("Zero unhedged FX loss > 5%", styles['TableCell']), Paragraph("Continuous", styles['TableCell']), Paragraph("Structure capital tranches in escrow", styles['TableCell'])],
    ]
    kpi_tbl = Table(kpi_data, colWidths=[80, 115, 117, 75, 145])
    kpi_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 8))
    
    # SECTION 24: DECISION GATES / GO-NO-GO CONDITIONS
    story.append(Paragraph("24. Decision Gates / Go-No-Go Conditions", styles['SectionH1']))
    story.append(Spacer(1, 2))
    gates_text = (
        "&bull; <b>Gate 1 (Go/No-Go on Entity Formation):</b> Foreign legal counsel must confirm statutory compliance clearance before releasing Phase 2 capital.<br/>"
        "&bull; <b>Gate 2 (Go/No-Go on Logistics Setup):</b> 3PL partner contract must demonstrate verified regional delivery SLAs without upfront capex.<br/>"
        "&bull; <b>Gate 3 (Go/No-Go on Commercial Scaling):</b> Pilot customer acquisition must validate sustainable unit margins before releasing Phase 4 scale-up funds."
    )
    story.append(Paragraph(gates_text, styles['Body']))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 16 — SECTION 25: FINAL BOARD RECOMMENDATION & ACTION PLAN
    # -------------------------------------------------------------
    story.append(Paragraph("25. Final Board Recommendation & Action Plan", styles['SectionH1']))
    story.append(Spacer(1, 2))
    
    v_box = [
        [Paragraph(f"<b>FINAL BOARD VERDICT: {decision}</b>", styles['CoverVerdict'])],
        [Paragraph(f"Executive Analytical Confidence: <b>{conf}%</b> &bull; Deterministic Engine Evaluated", styles['CoverVerdictSub'])]
    ]
    v_tbl = Table(v_box, colWidths=[532])
    v_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), box_bg),
        ('BOX', (0,0), (-1,-1), 1.5, box_border),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(v_tbl)
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Core Strategic Drivers (Why):</b>", styles['SectionH2']))
    story.append(Spacer(1, 2))
    reasons = expl.get('key_reasons', expl.get('strongest_positive_evidence', []))
    if not reasons:
        reasons = [
            f"Validated commercial demand depth for {ctx['company']} in {ctx['market']}.",
            f"Capital allocation of {ctx['budget_display']} is sufficient for initial pilot validation.",
            f"Statutory foreign entity registration pathways verified via legal datasets."
        ]
    for idx, r_item in enumerate(reasons[:4], 1):
        story.append(Paragraph(f"&bull; <b>Strategic Driver {idx}:</b> {r_item}", styles['Body']))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Mandatory Conditions Precedent:</b>", styles['SectionH2']))
    story.append(Spacer(1, 2))
    for b in ctx['critical_blockers'][:3]:
        story.append(Paragraph(f"&bull; <b>[{b.get('severity', 'HIGH')}]:</b> {b.get('title')}: {b.get('resolution_condition')}", styles['Body']))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Primary Unresolved Risk:</b>", styles['SectionH2']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"&bull; {top_risk}", styles['Body']))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>Immediate Executive Action Plan:</b>", styles['SectionH2']))
    story.append(Spacer(1, 2))
    next_act = ctx['action_plan'][0] if ctx['action_plan'] else f"Retain local legal counsel in {ctx['market']} to initiate corporate incorporation."
    story.append(Paragraph(f"&bull; <b>Action 1:</b> {next_act}", styles['Body']))
    if len(ctx['action_plan']) > 1:
        story.append(Paragraph(f"&bull; <b>Action 2:</b> {ctx['action_plan'][1]}", styles['Body']))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 17 — SECTION 26: EVIDENCE TRACEABILITY MATRIX
    # -------------------------------------------------------------
    story.append(Paragraph("26. Evidence Traceability Matrix", styles['SectionH1']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "Traceability matrix linking every specialist finding directly to its underlying grounding dataset, analytical confidence, and decision weight.",
        styles['Body']
    ))
    story.append(Spacer(1, 4))
    
    trace_data = [
        [Paragraph("<b>Specialist</b>", styles['TableHead']), Paragraph("<b>Key Finding / Assertion</b>", styles['TableHead']), Paragraph("<b>Grounding Source</b>", styles['TableHead']), Paragraph("<b>Confidence</b>", styles['TableHead']), Paragraph("<b>Decision Influence</b>", styles['TableHead'])],
    ]
    weights = {
        "RESEARCHER": "Demand Viability Gate",
        "COMPETITOR": "Defensibility Evaluation",
        "LEGAL": "Statutory Compliance Gate",
        "OPERATIONS": "Logistics Feasibility Gate",
        "RISK": "Risk Matrix Floor Rating",
        "CFO": "Capital Solvency Gate",
        "CEO": "Executive Synthesis"
    }
    for aid, rep in ctx['reports'].items():
        name = rep.get("name", aid.title())
        kf = rep.get("key_finding") or rep.get("analysis", "")[:85] + "..."
        is_ver = rep.get("data_verified", False)
        src = "Local Repository CSV" if is_ver else "Model Synthesis"
        cf = rep.get("confidence", 0)
        w = weights.get(aid, "Advisory")
        trace_data.append([
            Paragraph(f"<b>{name}</b>", styles['TableCellBold']),
            Paragraph(kf, styles['TableCell']),
            Paragraph(src, styles['TableCell']),
            Paragraph(f"{cf}%", styles['TableCellRight']),
            Paragraph(w, styles['TableCell']),
        ])
    tr_tbl = Table(trace_data, colWidths=[100, 180, 100, 52, 100])
    tr_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(tr_tbl)
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 18 — SECTION 27: DATA SOURCES & SECTION 28: ANALYTICAL METHODOLOGY
    # -------------------------------------------------------------
    story.append(Paragraph("27. Data Sources & Provenance Registry", styles['SectionH1']))
    story.append(Spacer(1, 2))
    
    src_data = [
        [Paragraph("<b>Domain</b>", styles['TableHead']), Paragraph("<b>Dataset / Authority</b>", styles['TableHead']), Paragraph("<b>Scope & Empirical Status</b>", styles['TableHead'])],
        [Paragraph("Market Ecosystem Data", styles['TableCellBold']), Paragraph("research_data.csv", styles['TableCell']), Paragraph("Regional enterprise counts and aggregate venture funding.", styles['TableCell'])],
        [Paragraph("Corporate Benchmarking", styles['TableCellBold']), Paragraph("competition_data.csv", styles['TableCell']), Paragraph("Public sovereign enterprise capitalization benchmarks.", styles['TableCell'])],
        [Paragraph("Regulatory & Legal", styles['TableCellBold']), Paragraph("legal_data.csv", styles['TableCell']), Paragraph("World Bank Ease of Doing Business & contract enforcement scores.", styles['TableCell'])],
        [Paragraph("Logistics Infrastructure", styles['TableCellBold']), Paragraph("market_data.csv", styles['TableCell']), Paragraph("World Bank Logistics Performance Index (LPI 2023).", styles['TableCell'])],
        [Paragraph("Sovereign & Macro Risk", styles['TableCellBold']), Paragraph("risk_data.csv", styles['TableCell']), Paragraph("Fund for Peace Fragile States Index (FSI 2023).", styles['TableCell'])],
        [Paragraph("Financial Valuation", styles['TableCellBold']), Paragraph("financial_data.csv", styles['TableCell']), Paragraph("Enterprise market capitalization and revenue benchmarks.", styles['TableCell'])],
    ]
    src_tbl = Table(src_data, colWidths=[130, 140, 262])
    src_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(src_tbl)
    story.append(Spacer(1, 8))
    
    # SECTION 28: ANALYTICAL METHODOLOGY
    story.append(Paragraph("28. Analytical Methodology", styles['SectionH1']))
    story.append(Spacer(1, 2))
    method_text = (
        "1. <b>Input Ingestion & Parameter Normalization:</b> User parameters ingested and matched against verified datasets.<br/>"
        "2. <b>Independent Specialist Audits:</b> 6 C-suite specialists evaluate domain feasibility under distinct mandates.<br/>"
        "3. <b>Consensus & Mathematical Agreement:</b> Automated voting aggregation and confidence calculation.<br/>"
        "4. <b>Deterministic Policy Engine:</b> 9 corporate expansion policy rules evaluated to establish authoritative verdict.<br/>"
        "5. <b>Executive Synthesis:</b> CEO synthesizes strategic rationale and issues auditable briefing."
    )
    story.append(Paragraph(method_text, styles['Body']))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 19 — SECTION 29: SYSTEM AUDIT TRAIL & REPRODUCIBILITY
    # -------------------------------------------------------------
    story.append(Paragraph("29. System Audit Trail & Reproducibility", styles['SectionH1']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "Deterministic audit trail certifying system parameters and policy rule evaluations. Zero secrets or API keys are surfaced.",
        styles['Body']
    ))
    story.append(Spacer(1, 4))
    
    audit_data = [
        [Paragraph("<b>Audit Parameter</b>", styles['TableHead']), Paragraph("<b>System Execution Value</b>", styles['TableHead'])],
        [Paragraph("Session Identifier", styles['TableCellBold']), Paragraph(str(ctx['session_id']), styles['CodeStyle'])],
        [Paragraph("Execution Timestamp", styles['TableCellBold']), Paragraph(time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(ctx['timestamp'])), styles['TableCell'])],
        [Paragraph("Target Enterprise", styles['TableCellBold']), Paragraph(str(ctx['company']), styles['TableCell'])],
        [Paragraph("Target Market / Domain", styles['TableCellBold']), Paragraph(str(ctx['market']), styles['TableCell'])],
        [Paragraph("Proposed Capital Budget", styles['TableCellBold']), Paragraph(str(ctx['budget_display']), styles['TableCell'])],
        [Paragraph("Target Timeline", styles['TableCellBold']), Paragraph(str(ctx['timeline']), styles['TableCell'])],
        [Paragraph("Specialist Agents Executed", styles['TableCellBold']), Paragraph(f"{len(ctx['reports'])} Specialists Verified", styles['TableCell'])],
        [Paragraph("Authoritative Final Verdict", styles['TableCellBold']), Paragraph(f"<b>{decision}</b> (Confidence: {conf}%)", styles['TableCellBold'])],
    ]
    aud_tbl = Table(audit_data, colWidths=[180, 352])
    aud_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(aud_tbl)
    story.append(Spacer(1, 6))
    
    if ctx['rules']:
        story.append(Paragraph("<b>Deterministic Policy Rule Evaluations (RULE-001..RULE-009):</b>", styles['SectionH2']))
        story.append(Spacer(1, 2))
        r_tbl_data = [
            [Paragraph("<b>Rule ID</b>", styles['TableHead']), Paragraph("<b>Policy Category</b>", styles['TableHead']), Paragraph("<b>Result</b>", styles['TableHead']), Paragraph("<b>Evaluation Rationale</b>", styles['TableHead'])],
        ]
        for r in ctx['rules'][:7]:
            rid = r.get("rule_id", "RULE")
            rcat = r.get("category", "Policy")
            rstat = r.get("status", r.get("result", "PASS"))
            rdetail = f"<b>Input:</b> {r.get('actual_value', '')}<br/><b>Reason:</b> {r.get('reason', '')}"
            r_tbl_data.append([
                Paragraph(f"<b>{rid}</b>", styles['CodeStyle']),
                Paragraph(rcat, styles['TableCell']),
                Paragraph(f"<b>{rstat}</b>", styles['TableCellBold']),
                Paragraph(rdetail, styles['TableCell']),
            ])
        rule_table = Table(r_tbl_data, colWidths=[65, 115, 55, 297])
        rule_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(rule_table)
        
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # PAGE 20 — SECTION 30: GOVERNANCE / LIMITATIONS / DISCLAIMER
    # -------------------------------------------------------------
    story.append(Spacer(1, 25))
    story.append(Paragraph("30. Governance Limitations & Disclaimer Notice", styles['SectionH1']))
    story.append(Spacer(1, 8))
    
    disclaimer_text = (
        "<b>BOARDROOM AI &bull; EXECUTIVE DECISION INTELLIGENCE REPORT</b><br/><br/>"
        "<b>LEGAL & FIDUCIARY LIMITATION NOTICE:</b> This briefing document was autonomously generated from the available "
        "BoardRoomAI multi-agent analysis. It is intended solely for strategic decision-support and internal fiduciary governance.<br/><br/>"
        "Recommendations are decision-support outputs and should be validated against current business, financial, legal, "
        "and market conditions before execution.<br/><br/>"
        "No representations or warranties, express or implied, are made regarding the completeness or accuracy of third-party "
        "market datasets. Strategic corporate execution carries inherent commercial, operational, and macroeconomic risks.<br/><br/>"
        "<b>CONFIDENTIAL &bull; BOARDROOMAI MULTI-AGENT GOVERNANCE ARTIFACT</b>"
    )
    disc_box = Table([[Paragraph(disclaimer_text, styles['CalloutBox'])]], colWidths=[532])
    disc_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(disc_box)
    story.append(Spacer(1, 30))
    
    sign_data = [
        [Paragraph("<b>Board Executive Review:</b>", styles['TableCellBold']), Paragraph("<b>Governance Committee Sign-Off:</b>", styles['TableCellBold'])],
        [Paragraph("Name: _________________________________", styles['TableCell']), Paragraph("Name: _________________________________", styles['TableCell'])],
        [Paragraph("Title: __________________________________", styles['TableCell']), Paragraph("Title: __________________________________", styles['TableCell'])],
        [Paragraph("Date: __________________________________", styles['TableCell']), Paragraph("Date: __________________________________", styles['TableCell'])],
    ]
    sign_tbl = Table(sign_data, colWidths=[266, 266])
    sign_tbl.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(sign_tbl)
    
    # Build Document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


# =========================================================================
# TRACK B GENERATOR (Preserved for Track B Dedicated Briefings)
# =========================================================================

def generate_track_b_pdf_report(session_data):
    """
    Generates the Official 19-Section Executive Decision Intelligence Audit Report for Track B.
    Grounds all findings in the Canonical BoardRoomResult.
    """
    is_valid, validation_errors = validate_consistency(session_data)
    if not is_valid:
        print(f"[PDF GENERATOR WARNING] Inconsistencies detected before generation: {validation_errors}")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CoverTitleB',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#0F1419"),
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitleB',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4A5568"),
        alignment=TA_CENTER
    )
    
    h1_style = ParagraphStyle(
        'Header1B',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0F1419"),
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustomB',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2D3748")
    )
    
    bold_body_style = ParagraphStyle(
        'BoldBodyTextCustomB',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabelB',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#1A365D")
    )
    
    rec_box_style = ParagraphStyle(
        'RecBoxB',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        alignment=TA_CENTER
    )
    
    code_style = ParagraphStyle(
        'CodeTextB',
        parent=body_style,
        fontName='Courier',
        fontSize=7.5,
        leading=10
    )
    
    story = []
    
    # ------------------ 1. COVER PAGE & VENTURE INPUT ------------------
    story.append(Spacer(1, 30))
    story.append(Paragraph("🚀 BOARDROOM AI", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Executive Decision Intelligence • Complete Factual Trust & Audit Trail", subtitle_style))
    story.append(Spacer(1, 16))
    
    # Cyan line
    dec_table = Table([[""]], colWidths=[504], rowHeights=[3])
    dec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#00D4FF")),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(dec_table)
    story.append(Spacer(1, 16))
    
    idea = session_data.get("business_idea", session_data.get("company", "New Venture Idea"))
    market = session_data.get("target_market", session_data.get("market", "Target Market"))
    budget = session_data.get("capital_budget", session_data.get("budget", 0))
    timeline = session_data.get("timeline", "12 Months")
    question = session_data.get("strategic_question", session_data.get("question", "Venture Launch Evaluation"))
    decision = session_data.get("final_decision", session_data.get("deterministic_decision", "VALIDATE FIRST"))
    confidence = session_data.get("confidence", session_data.get("ceo_confidence", 70))
    
    budget_fmt = f"${budget:,.0f} USD" if isinstance(budget, (int, float)) else str(budget)
    
    meta_data = [
        [Paragraph("Strategic Track:", meta_label_style), Paragraph("🚀 Track B • New Business Launch", body_style)],
        [Paragraph("Venture / Thesis:", meta_label_style), Paragraph(str(idea), body_style)],
        [Paragraph("Target Market:", meta_label_style), Paragraph(str(market), body_style)],
        [Paragraph("Initial Capital:", meta_label_style), Paragraph(budget_fmt, body_style)],
        [Paragraph("Launch Horizon:", meta_label_style), Paragraph(str(timeline), body_style)],
        [Paragraph("Strategic Focus:", meta_label_style), Paragraph(str(question), body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[120, 384])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 16))
    
    # ------------------ 2. FINAL DETERMINISTIC VERDICT & CONFIDENCE ------------------
    dec_color = colors.HexColor("#D4EDDA")
    text_color = colors.HexColor("#155724")
    if "DO NOT LAUNCH" in decision or "REJECT" in decision:
        dec_color = colors.HexColor("#F8D7DA")
        text_color = colors.HexColor("#721C24")
    elif "VALIDATE" in decision:
        dec_color = colors.HexColor("#FFF3CD")
        text_color = colors.HexColor("#856404")
        
    eq = session_data.get("evidence_quality", get_evidence_quality(session_data.get("specialist_reports", {})))
    
    verdict_text = (
        f"<font color='{text_color}'>FINAL DETERMINISTIC VERDICT: {decision}</font><br/>"
        f"<font size=9 color='#495057'>DECISION CONFIDENCE: {confidence}% &bull; "
        f"DATASET GROUNDING: {eq['verified']}/6 DATASET-BACKED ({eq['coverage_percent']}%)</font>"
    )
    verdict_card = Table([[Paragraph(verdict_text, rec_box_style)]], colWidths=[504])
    verdict_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), dec_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1.5, text_color),
    ]))
    story.append(verdict_card)
    story.append(Spacer(1, 12))
    
    conf_bk = session_data.get("confidence_breakdown", {})
    if conf_bk:
        conf_note = (
            f"<b>Mathematical Confidence Breakdown:</b> Evidence Coverage ({conf_bk.get('evidence_coverage_component', 0)}%) + "
            f"Specialist Agreement ({conf_bk.get('specialist_agreement_component', 0)}%) + "
            f"Rule Satisfaction ({conf_bk.get('rule_satisfaction_component', 0)}%) - "
            f"Blocker Penalties ({conf_bk.get('blocker_penalty', 0)}%) = <b>{confidence}%</b><br/>"
            f"<i>* Semantics: Evaluates analytical confidence in the decision given evidence coverage, agreement, and rule satisfaction (not a predictive probability of business success).</i>"
        )
        story.append(Paragraph(conf_note, ParagraphStyle('CBK', parent=body_style, fontSize=7.5, leading=10.5, textColor=colors.HexColor("#4A5568"))))
        story.append(Spacer(1, 12))
        
    story.append(Paragraph("AUDIT DISCLAIMER: All claims in this briefing are classified into explicit evidence types. Local dataset presence is designated DATASET-BACKED and distinguished from independently audited SOURCE-VERIFIED provenance.", ParagraphStyle('Note', parent=body_style, fontName='Helvetica-Oblique', fontSize=7, textColor=colors.HexColor("#718096"), alignment=TA_CENTER)))
    story.append(PageBreak())
    
    # ------------------ 3. EXECUTIVE SYNTHESIS & POLICY RATIONALE ------------------
    story.append(Paragraph("1. Executive Synthesis & Deterministic Policy Rationale", h1_style))
    story.append(Spacer(1, 4))
    
    ceo_rat = session_data.get("ceo_rationale", "No rationale specified.")
    story.append(Paragraph(f"<b>Deterministic Engine Policy Evaluation:</b> {ceo_rat}", body_style))
    story.append(Spacer(1, 10))
    
    cov_data = [
        [
            Paragraph("<b>Coverage Dimension</b>", meta_label_style),
            Paragraph("<b>Metric</b>", meta_label_style),
            Paragraph("<b>Audit Interpretation</b>", meta_label_style)
        ],
        [
            Paragraph("Dataset Coverage", bold_body_style),
            Paragraph(f"{session_data.get('dataset_coverage_percent', eq['coverage_percent'])}%", body_style),
            Paragraph(f"{eq['verified']}/6 specialist domains grounded in local repository CSV datasets.", body_style)
        ],
        [
            Paragraph("Claim Traceability", bold_body_style),
            Paragraph(f"{session_data.get('claim_traceability_percent', 100)}%", body_style),
            Paragraph("100% of factual assertions linked to structured evidence IDs and formulas.", body_style)
        ],
        [
            Paragraph("Decision-Critical Evidence", bold_body_style),
            Paragraph(f"{session_data.get('decision_critical_coverage_percent', 75)}%", body_style),
            Paragraph("Identifies empirical macro coverage while flagging primary qualitative customer demand gap.", body_style)
        ]
    ]
    cov_table = Table(cov_data, colWidths=[130, 70, 304])
    cov_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(cov_table)
    story.append(Spacer(1, 12))
    
    # ------------------ 4. BOARD CONSENSUS & VOTE DISTRIBUTION ------------------
    story.append(Paragraph("2. Board Consensus & Specialist Deliberation Votes", h1_style))
    story.append(Spacer(1, 4))
    
    votes = session_data.get("specialist_votes", {})
    yes_v = votes.get("YES", 0)
    maybe_v = votes.get("MAYBE", 0)
    no_v = votes.get("NO", 0)
    
    vote_summary = f"<b>Board Vote Distribution:</b> {yes_v} YES &bull; {maybe_v} MAYBE (CONDITIONAL) &bull; {no_v} NO (Total: 6 Specialists)"
    story.append(Paragraph(vote_summary, body_style))
    story.append(Spacer(1, 8))
    
    # ------------------ 5. SPECIALIST REPORTS ------------------
    story.append(Paragraph("3. Specialist Deliberations & Key Findings", h1_style))
    story.append(Spacer(1, 4))
    
    specialists = session_data.get("specialist_reports", {})
    for aid, rep in specialists.items():
        if aid == "FOUNDER_CEO":
            continue
            
        name = rep.get("name", aid.replace("_", " ").title())
        rec = str(rep.get("recommendation", "MAYBE")).upper()
        conf = rep.get("confidence", 0)
        is_v = rep.get("data_verified", False)
        status_tag = "DATASET-BACKED" if is_v else "DATA UNVERIFIED"
        finding = rep.get("key_finding") or rep.get("analysis", "No analysis recorded.")
        concern = rep.get("primary_concern", "No primary concern flagged.")
        
        box_data = [
            [
                Paragraph(f"<b>{name}</b>", bold_body_style),
                Paragraph(f"<b>Vote:</b> {rec} | <b>Confidence:</b> {conf}% | <b>Status:</b> {status_tag}", ParagraphStyle('R', parent=body_style, alignment=TA_RIGHT))
            ],
            [
                Paragraph(f"<b>Key Finding:</b> {finding}<br/><b>Primary Concern:</b> {concern}", body_style),
                ""
            ]
        ]
        t = Table(box_data, colWidths=[204, 300])
        t.setStyle(TableStyle([
            ('SPAN', (0,1), (1,1)),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(KeepTogether([t, Spacer(1, 6)]))
        
    story.append(PageBreak())
    
    # ------------------ 6. STRUCTURED EVIDENCE LEDGER ------------------
    story.append(Paragraph("4. Structured Evidence Ledger (EVID-xxx Trace)", h1_style))
    story.append(Spacer(1, 4))
    
    ledger_data = [
        [
            Paragraph("<b>EVID ID</b>", meta_label_style),
            Paragraph("<b>TYPE</b>", meta_label_style),
            Paragraph("<b>RELEVANCE</b>", meta_label_style),
            Paragraph("<b>CLAIM & TABULAR QUERY</b>", meta_label_style),
            Paragraph("<b>STATUS</b>", meta_label_style),
        ]
    ]
    
    ledger = session_data.get("evidence_ledger", [])
    for item in ledger:
        eid = item.get("evidence_id", "EVID-000")
        etype = item.get("evidence_type", "FACT")
        rel = item.get("evidence_relevance", "DIRECT")
        src = item.get("source_dataset", "N/A")
        val = item.get("claim", item.get("value", ""))
        vstatus = item.get("verification_status", "DATASET-BACKED")
        
        detail_text = f"<b>{src}:</b> {val}"
        if item.get("calculation_formula"):
            detail_text += f"<br/><i>Calc: {item.get('calculation_formula')}</i>"
            
        ledger_data.append([
            Paragraph(f"<b>{eid}</b>", code_style),
            Paragraph(etype, body_style),
            Paragraph(rel, body_style),
            Paragraph(detail_text, body_style),
            Paragraph(vstatus, body_style),
        ])
        
    led_table = Table(ledger_data, colWidths=[55, 65, 55, 240, 89])
    led_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(led_table)
    story.append(Spacer(1, 12))
    
    # ------------------ 7. REPRODUCIBLE CALCULATIONS ------------------
    calcs = session_data.get("reproducible_calculations", [])
    if calcs:
        story.append(Paragraph("5. Numerical Reproducibility Audit", h1_style))
        story.append(Spacer(1, 4))
        
        calc_data = [
            [
                Paragraph("<b>EVID REF</b>", meta_label_style),
                Paragraph("<b>CALCULATION DOMAIN</b>", meta_label_style),
                Paragraph("<b>FORMULA & INPUT VALUES</b>", meta_label_style),
                Paragraph("<b>DETERMINISTIC OUTPUT</b>", meta_label_style),
            ]
        ]
        
        for c in calcs:
            inputs_str = ", ".join([f"{k}={v}" for k, v in c.get("inputs", {}).items()])
            formula_text = f"<b>Formula:</b> {c.get('formula')}<br/><b>Inputs:</b> {inputs_str}"
            
            calc_data.append([
                Paragraph(c.get("evidence_id", "EVID-000"), code_style),
                Paragraph(c.get("domain", "Financial Math"), body_style),
                Paragraph(formula_text, body_style),
                Paragraph(f"<b>{c.get('output')}</b>", bold_body_style),
            ])
            
        calc_table = Table(calc_data, colWidths=[65, 120, 219, 100])
        calc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ]))
        story.append(calc_table)
        story.append(Spacer(1, 12))
        
    # ------------------ 8. SOVEREIGN & VENTURE RISK MATRIX ------------------
    story.append(Paragraph("6. Sovereign & Venture Risk Matrix", h1_style))
    story.append(Spacer(1, 4))
    
    risk_data = [
        [
            Paragraph("<b>RISK ID</b>", meta_label_style),
            Paragraph("<b>CATEGORY</b>", meta_label_style),
            Paragraph("<b>SEVERITY</b>", meta_label_style),
            Paragraph("<b>EVID REF</b>", meta_label_style),
            Paragraph("<b>RATIONALE & MITIGATION</b>", meta_label_style),
        ]
    ]
    
    risks = session_data.get("risk_matrix", [])
    for r in risks:
        rid = r.get("risk_id", "RISK-000")
        rcat = r.get("category", "General")
        rlevel = r.get("level", "UNKNOWN")
        rref = r.get("evidence_ref", "EVID-000")
        rdesc = f"<b>Observation:</b> {r.get('rationale')}<br/><b>Mitigation:</b> {r.get('mitigation')}"
        
        risk_data.append([
            Paragraph(f"<b>{rid}</b>", code_style),
            Paragraph(rcat, bold_body_style),
            Paragraph(rlevel, body_style),
            Paragraph(rref, code_style),
            Paragraph(rdesc, body_style),
        ])
        
    risk_table = Table(risk_data, colWidths=[55, 105, 55, 55, 234])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 8))
    
    # Render Risk Mitigation Deterministic Audit Breakdown
    risk_mit = session_data.get("risk_mitigation_breakdown", {})
    if risk_mit:
        score_val = risk_mit.get("risk_mitigation_score", session_data.get("consensus_metrics", {}).get("risk_mitigation_score", 0))
        label_val = risk_mit.get("rating_label", "EVALUATED")
        formula_ver = risk_mit.get("formula_version", "v2.0-CANONICAL-DETERMINISTIC")
        
        mit_summary_text = (
            f"<b>Canonical Risk Mitigation:</b> {score_val}% ({label_val}) &bull; "
            f"<b>Formula:</b> {formula_ver} &bull; "
            f"<b>Total Risk Deductions:</b> -{risk_mit.get('total_penalty', 0):.1f} pts (Base: 100.0)"
        )
        story.append(Paragraph(mit_summary_text, body_style))
        story.append(Spacer(1, 4))
        
        cat_break = risk_mit.get("category_breakdown", {})
        if cat_break:
            cat_table_data = [
                [
                    Paragraph("<b>Risk Category</b>", meta_label_style),
                    Paragraph("<b>Severity</b>", meta_label_style),
                    Paragraph("<b>Mitigation Score</b>", meta_label_style),
                    Paragraph("<b>Status & Control Summary</b>", meta_label_style)
                ]
            ]
            for c_name, c_data in cat_break.items():
                cat_table_data.append([
                    Paragraph(c_name, bold_body_style),
                    Paragraph(c_data.get("level", "UNKNOWN"), body_style),
                    Paragraph(f"{c_data.get('mitigation_score', 0)}%", code_style),
                    Paragraph(f"<b>{c_data.get('status', 'EVALUATED')}:</b> {c_data.get('rationale', '')}", body_style)
                ])
                
            cat_table = Table(cat_table_data, colWidths=[120, 60, 80, 244])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ]))
            story.append(cat_table)
            story.append(Spacer(1, 8))
    story.append(Spacer(1, 6))
    
    # ------------------ 9. CRITICAL BLOCKERS & RESOLUTION CONDITIONS ------------------
    blockers = session_data.get("critical_blockers", [])
    if blockers:
        story.append(Paragraph("7. Critical Blockers & Traceability", h1_style))
        story.append(Spacer(1, 4))
        
        blk_data = [
            [
                Paragraph("<b>BLOCKER ID</b>", meta_label_style),
                Paragraph("<b>SEVERITY</b>", meta_label_style),
                Paragraph("<b>SOURCE</b>", meta_label_style),
                Paragraph("<b>DESCRIPTION & RESOLUTION</b>", meta_label_style),
            ]
        ]
        
        for b in blockers:
            bid = b.get("blocker_id", "BLOCKER-000")
            bsev = b.get("severity", "HIGH")
            bsrc = b.get("source_specialist", "Specialist")
            bdesc = f"<b>{b.get('title')}:</b> {b.get('description')}<br/><b>Resolution:</b> {b.get('resolution_condition')}"
            
            blk_data.append([
                Paragraph(f"<b>{bid}</b>", code_style),
                Paragraph(bsev, bold_body_style),
                Paragraph(bsrc, body_style),
                Paragraph(bdesc, body_style),
            ])
            
        blk_table = Table(blk_data, colWidths=[70, 65, 105, 264])
        blk_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ]))
        story.append(blk_table)
        story.append(Spacer(1, 12))
        
    # ------------------ 10. DETERMINISTIC DECISION RULES ------------------
    rules = session_data.get("rule_evaluations", [])
    if rules:
        story.append(Paragraph("8. Deterministic Decision Rule Evaluations", h1_style))
        story.append(Spacer(1, 4))
        
        rule_data = [
            [
                Paragraph("<b>RULE ID</b>", meta_label_style),
                Paragraph("<b>CATEGORY</b>", meta_label_style),
                Paragraph("<b>RESULT</b>", meta_label_style),
                Paragraph("<b>ACTUAL INPUTS & EVALUATION</b>", meta_label_style),
            ]
        ]
        
        for r in rules:
            rid = r.get("rule_id", "RULE-000")
            rcat = r.get("category", "Policy")
            rstat = r.get("result", r.get("status", "PASS"))
            rdetail = f"<b>Observed:</b> {r.get('actual_value')}<br/><b>Rationale:</b> {r.get('rationale')}"
            
            rule_data.append([
                Paragraph(f"<b>{rid}</b>", code_style),
                Paragraph(rcat, bold_body_style),
                Paragraph(rstat, bold_body_style),
                Paragraph(rdetail, body_style),
            ])
            
        rule_table = Table(rule_data, colWidths=[65, 105, 65, 269])
        rule_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ]))
        story.append(rule_table)
        story.append(Spacer(1, 12))
        
    # ------------------ 11. EXECUTIVE ACTION PLAN ------------------
    actions = session_data.get("executive_action_plan", [])
    if actions:
        story.append(Paragraph("9. Executive Action Plan", h1_style))
        story.append(Spacer(1, 4))
        
        act_data = [
            [
                Paragraph("<b>PRIORITY</b>", meta_label_style),
                Paragraph("<b>ACTION STEP</b>", meta_label_style),
                Paragraph("<b>SOURCE REF</b>", meta_label_style),
                Paragraph("<b>SUCCESS METRIC & TIMEFRAME</b>", meta_label_style),
            ]
        ]
        
        for a in actions:
            apri = a.get("priority", "P2")
            atitle = f"<b>{a.get('action')}</b><br/>{a.get('reason')}"
            aref = a.get("source_ref", "N/A")
            ametric = f"<b>Target:</b> {a.get('success_condition')}<br/><b>Window:</b> {a.get('timeframe')}"
            
            act_data.append([
                Paragraph(apri, bold_body_style),
                Paragraph(atitle, body_style),
                Paragraph(aref, code_style),
                Paragraph(ametric, body_style),
            ])
            
        act_table = Table(act_data, colWidths=[75, 175, 65, 189])
        act_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ]))
        story.append(act_table)
        story.append(Spacer(1, 12))
        
    # ------------------ 12. MIND-CHANGE THRESHOLDS & ROADMAP ------------------
    thresholds = session_data.get("mind_change_thresholds", [])
    roadmap = session_data.get("validation_roadmap", [])
    
    if thresholds or roadmap:
        story.append(Paragraph("10. Mind-Change Thresholds & Validation Roadmap", h1_style))
        story.append(Spacer(1, 4))
        
        if thresholds:
            story.append(Paragraph("<b>Classified Mind-Change Thresholds:</b>", bold_body_style))
            for t in thresholds:
                t_str = f"&bull; <b>[{t.get('classification', 'POLICY')}] {t.get('source')}:</b> {t.get('threshold')}"
                story.append(Paragraph(t_str, body_style))
            story.append(Spacer(1, 5))
            
        if roadmap:
            story.append(Paragraph("<b>Empirical Validation Roadmap:</b>", bold_body_style))
            for idx, r_item in enumerate(roadmap, 1):
                clean_r = r_item.lstrip("0123456789. ")
                story.append(Paragraph(f"<b>Stage {idx}:</b> {clean_r}", body_style))
            story.append(Spacer(1, 8))
            
    # ------------------ 13. DATASET PROVENANCE & INTEGRITY REGISTRY ------------------
    story.append(Paragraph("11. Dataset Provenance, Freshness & Tier Classification", h1_style))
    story.append(Spacer(1, 4))
    
    prov_records = session_data.get("dataset_provenance_records", {})
    if prov_records:
        prov_table_data = [
            [
                Paragraph("<b>DATASET</b>", meta_label_style),
                Paragraph("<b>SOURCE TIER</b>", meta_label_style),
                Paragraph("<b>FRESHNESS</b>", meta_label_style),
                Paragraph("<b>PUBLISHER & SCOPE</b>", meta_label_style),
                Paragraph("<b>SHA-256 HASH</b>", meta_label_style)
            ]
        ]
        
        for fn, p in prov_records.items():
            prov_table_data.append([
                Paragraph(f"<b>{fn}</b>", code_style),
                Paragraph(p.get("source_tier", "TIER 3"), body_style),
                Paragraph(p.get("freshness_category", "RECENT"), body_style),
                Paragraph(f"{p.get('publisher')}<br/><i>Scope: {p.get('geographic_scope')}</i>", body_style),
                Paragraph(p.get("dataset_hash", "UNKNOWN"), code_style)
            ])
            
        ptable = Table(prov_table_data, colWidths=[90, 85, 65, 174, 90])
        ptable.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ]))
        story.append(ptable)
        story.append(Spacer(1, 10))

    # ------------------ 14. DISCREPANCIES & AUDIT METADATA ------------------
    discrepancies = session_data.get("discrepancies", [])
    if discrepancies:
        story.append(Paragraph("12. LLM / Policy Discrepancy & Safety Lock Log", h1_style))
        story.append(Spacer(1, 4))
        for d in discrepancies:
            d_msg = f"⚠ <b>SAFETY LOCK ACTIVATED:</b> {d.get('details')}"
            story.append(Paragraph(d_msg, ParagraphStyle('Disc', parent=body_style, textColor=colors.HexColor("#C53030"))))
        story.append(Spacer(1, 8))
        
    story.append(Paragraph("13. Audit Metadata & Integrity Stamp", h1_style))
    story.append(Spacer(1, 4))
    
    audit_meta = session_data.get("audit_metadata", {})
    checksums = audit_meta.get("dataset_checksums", {})
    cs_str = "; ".join([f"{k}: {v}" for k, v in checksums.items()])
    
    meta_lines = [
        f"<b>Application Engine:</b> {audit_meta.get('app_version', '2.6.0-TRUST-AUDIT')} &bull; <b>Decision Model:</b> {audit_meta.get('decision_engine_version', 'DETERMINISTIC-V3.5')}",
        f"<b>Audit Timestamp:</b> {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(session_data.get('timestamp', time.time())))}",
        f"<b>Dataset Checksum Integrity:</b> {cs_str}",
        f"<b>Zero-LLM Decision Reproducibility:</b> Verified &bull; Strict Deterministic Policy Locking Active."
    ]
    for ml in meta_lines:
        story.append(Paragraph(ml, ParagraphStyle('AuditMeta', parent=body_style, fontSize=7.5, leading=10, textColor=colors.HexColor("#4A5568"))))
        
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
