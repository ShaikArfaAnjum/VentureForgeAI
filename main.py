import time
import os
import importlib
import streamlit as st
from ui.styles import inject_custom_css
import ui.components
importlib.reload(ui.components)
from ui.components import (
    render_header,
    render_footer,
    render_glass_card,
    render_chat_bubble,
    render_metric_ring,
    render_agent_vote_card,
    render_validation_roadmap_card,
    render_capital_benchmark_card,
    render_board_agreement_card,
    render_decision_explanation_card,
    render_disagreements_section,
    render_critical_blockers_card,
    render_what_would_change_mind_card,
    render_decision_trace_card,
    render_executive_decision_header,
    render_board_consensus_intelligence,
    render_specialist_position_matrix,
    render_evidence_quality_panel,
    render_what_we_know_panel,
    render_decision_timeline,
    render_board_activity_summary,
    render_data_sources_table,
    render_executive_action_plan,
    render_evidence_ledger_table,
    render_risk_mitigation_panel,
    render_risk_matrix_panel,
    render_deterministic_rule_panel,
    render_discrepancy_alert,
    render_judge_audit_explorer,
    render_why_trust_panel,
    clean_html
)
from services.boardroom_orchestrator import run_boardroom_session, CORE_AGENTS
from services.track_b_orchestrator import run_track_b_session, TRACK_B_AGENTS, calculate_track_b_consensus
from services.consensus_engine import calculate_consensus
from services.report_generator import generate_pdf_report
from services.session_manager import save_session, load_session, list_sessions
from agents.ceo_agent import analyze_ceo

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="BoardRoomAI - Virtual Executive Boardroom",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. Initialize Session States
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "mode" not in st.session_state:
    st.session_state.mode = "expansion"
if "company" not in st.session_state:
    st.session_state.company = ""
if "market" not in st.session_state:
    st.session_state.market = ""
if "budget" not in st.session_state:
    st.session_state.budget = 500000
if "timeline" not in st.session_state:
    st.session_state.timeline = "1 Year"
if "question" not in st.session_state:
    st.session_state.question = ""
if "business_model" not in st.session_state:
    st.session_state.business_model = ""
if "results" not in st.session_state:
    st.session_state.results = None

# Track B Session States
if "business_idea" not in st.session_state:
    st.session_state.business_idea = ""
if "target_market" not in st.session_state:
    st.session_state.target_market = ""
if "capital_budget" not in st.session_state:
    st.session_state.capital_budget = 500000
if "launch_timeline" not in st.session_state:
    st.session_state.launch_timeline = "12 Months"
if "strategic_board_question" not in st.session_state:
    st.session_state.strategic_board_question = ""
if "target_customer" not in st.session_state:
    st.session_state.target_customer = ""

# Inject stylesheet based on page state (img1 for landing/inputs, img2 for execution/results)
if st.session_state.page in ["landing", "input", "launch_input"]:
    inject_custom_css("img1")
else:
    inject_custom_css("img2")

# Persistent Sidebar for Active Boardrooms
if st.session_state.page != "landing":
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 10px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.08);">
                <div style="font-size:20px; font-weight:800; font-family:'Outfit'; color:#FFFFFF;">🏢 BOARDROOM AI</div>
                <div style="font-size:10px; color:#8C9BA5; letter-spacing:1px; text-transform:uppercase; margin-top:2px;">Executive Decision Engine</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.write("")
        if st.session_state.mode == "launch":
            st.markdown(
                """
                <div style="background: rgba(255,184,0,0.12); border: 1px solid rgba(255,184,0,0.3); border-left:3px solid #FFB800; border-radius:10px; padding:10px 12px; margin-bottom:16px;">
                    <div style="font-size:9.5px; color:#FFB800; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">ACTIVE BOARDROOM</div>
                    <div style="font-size:13.5px; color:#FFFFFF; font-weight:700; font-family:'Outfit';">🚀 New Business Launch</div>
                    <div style="font-size:11px; color:#8C9BA5; margin-top:2px;">New Idea → New Market</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='font-size:11px; font-weight:700; color:#8C9BA5; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px;'>BOARD SPECIALISTS</div>", unsafe_allow_html=True)
            sidebar_agents = [
                ("01", "📊", "Market Validator"),
                ("02", "🔍", "Competitive Scout"),
                ("03", "📜", "Regulatory Navigator"),
                ("04", "🚀", "Launch Operations"),
                ("05", "🛡️", "Venture Risk"),
                ("06", "💎", "Capital Strategist"),
                ("07", "👑", "Founder CEO")
            ]
        else:
            st.markdown(
                """
                <div style="background: rgba(0,212,255,0.12); border: 1px solid rgba(0,212,255,0.3); border-left:3px solid #00D4FF; border-radius:10px; padding:10px 12px; margin-bottom:16px;">
                    <div style="font-size:9.5px; color:#00D4FF; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">ACTIVE BOARDROOM</div>
                    <div style="font-size:13.5px; color:#FFFFFF; font-weight:700; font-family:'Outfit';">🏢 Corporate Expansion</div>
                    <div style="font-size:11px; color:#8C9BA5; margin-top:2px;">Existing Co → New Market</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='font-size:11px; font-weight:700; color:#8C9BA5; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px;'>C-SUITE DIRECTORS</div>", unsafe_allow_html=True)
            sidebar_agents = [
                ("01", "🔵", "Market Researcher"),
                ("02", "🟡", "Competitive Intel"),
                ("03", "⚖️", "General Counsel"),
                ("04", "⚙️", "COO"),
                ("05", "🔴", "Chief Risk Officer"),
                ("06", "💰", "Chief Financial Officer"),
                ("07", "👑", "Corporate CEO")
            ]
            
        for num, icon, name in sidebar_agents:
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; padding:7px 10px; margin-bottom:5px; border-radius:8px; background:rgba(22,29,36,0.6); border:1px solid rgba(255,255,255,0.03);">
                    <span style="font-size:10px; color:#505F6C; font-weight:700; width:22px;">{num}</span>
                    <span style="font-size:14px; margin-right:8px;">{icon}</span>
                    <span style="font-size:12px; color:#D2DCE6; font-weight:500;">{name}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        st.write("")
        st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.08); margin:16px 0;'></div>", unsafe_allow_html=True)
        if st.button("← Back to Strategic Selection", key="sidebar_back_landing"):
            st.session_state.page = "landing"
            st.rerun()

# Render Master App Header
if st.session_state.page == "landing":
    render_header("VentureForage AI")
else:
    render_header("BOARDROOM AI")

# ==========================================
# PAGE 1: LANDING PAGE
# ==========================================
if st.session_state.page == "landing":
    col1, col2 = st.columns([7, 5])
    
    with col1:
        # Immersive glassmorphic hero callout
        hero_html = """
        <div style="padding: 10px 0;">
            <h2 style="font-size: 28px; color: #FFFFFF; font-family: 'Outfit'; margin-top:0;">
                Where AI executives debate before you decide.
            </h2>
            <p style="font-size: 14.5px; line-height: 1.6; color: #B3C3D0;">
                BoardRoomAI convenes autonomous executive AI agents to stress-test your high-stakes corporate expansions and new business launches. Receive rigorous debate, real-data verification, and auditable strategic decisions in seconds.
            </p>
        </div>
        """
        render_glass_card("THE EXECUTIVE AI ADVANTAGE", hero_html, "#00D4FF")
        
        # Strategic Mode Selection Section
        st.markdown("<h3 style='margin-bottom:14px; margin-top:20px; color:#00D4FF; font-size:18px; font-family:Outfit; letter-spacing:0.5px;'>CHOOSE YOUR STRATEGIC PATH</h3>", unsafe_allow_html=True)
        
        mode_col1, mode_col2 = st.columns(2)
        with mode_col1:
            st.markdown(
                """
                <div style="background: rgba(22, 29, 36, 0.65); border: 1px solid rgba(0, 212, 255, 0.3); border-left: 3px solid #00D4FF; border-radius: 14px; padding: 18px 16px; margin-bottom: 12px; min-height: 195px; display:flex; flex-direction:column; justify-content:space-between;">
                    <div>
                        <div style="display:flex; align-items:center; margin-bottom:4px;">
                            <span style="font-size: 18px; margin-right: 8px;">🏢</span>
                            <strong style="color:#00D4FF; font-size:15px; font-family:'Outfit';">EXPANSION BOARDROOM</strong>
                        </div>
                        <div style="font-size:11px; color:#8C9BA5; margin-bottom:8px; font-weight:600;">
                            Existing Company → New Market
                        </div>
                        <div style="font-size:11.5px; color:#D2DCE6; font-style:italic; line-height:1.4; margin-bottom:8px;">
                            &ldquo;Should we expand an existing company into this market?&rdquo;
                        </div>
                        <div style="font-size:11px; color:#8C9BA5; line-height:1.35;">
                            Evaluate market opportunity, competition, legal exposure, operational feasibility, risk and financial viability before entering a new market.
                        </div>
                    </div>
                    <div style="font-size:9.5px; color:#00FF88; font-weight:700; margin-top:10px; border-top:1px dashed rgba(255,255,255,0.08); padding-top:6px;">
                        Decision: GO / NO-GO / CONDITIONAL GO
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("ENTER EXPANSION BOARDROOM 🏢", key="btn_start_expansion"):
                st.session_state.mode = "expansion"
                st.session_state.page = "input"
                st.rerun()
                
        with mode_col2:
            st.markdown(
                """
                <div style="background: rgba(22, 29, 36, 0.65); border: 1px solid rgba(255, 184, 0, 0.3); border-left: 3px solid #FFB800; border-radius: 14px; padding: 18px 16px; margin-bottom: 12px; min-height: 195px; display:flex; flex-direction:column; justify-content:space-between;">
                    <div>
                        <div style="display:flex; align-items:center; margin-bottom:4px;">
                            <span style="font-size: 18px; margin-right: 8px;">🚀</span>
                            <strong style="color:#FFB800; font-size:15px; font-family:'Outfit';">NEW BUSINESS LAUNCH</strong>
                        </div>
                        <div style="font-size:11px; color:#8C9BA5; margin-bottom:8px; font-weight:600;">
                            New Business Idea → New Market
                        </div>
                        <div style="font-size:11.5px; color:#D2DCE6; font-style:italic; line-height:1.4; margin-bottom:8px;">
                            &ldquo;Should we launch a brand-new business in this market?&rdquo;
                        </div>
                        <div style="font-size:11px; color:#8C9BA5; line-height:1.35;">
                            Validate market demand, competition, regulation, launch readiness, venture risk and capital feasibility before committing resources.
                        </div>
                    </div>
                    <div style="font-size:9.5px; color:#FFB800; font-weight:700; margin-top:10px; border-top:1px dashed rgba(255,255,255,0.08); padding-top:6px;">
                        Decision: LAUNCH / VALIDATE FIRST / DO NOT LAUNCH
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown('<div class="gold-btn">', unsafe_allow_html=True)
            if st.button("ENTER LAUNCH BOARDROOM 🚀", key="btn_start_launch"):
                st.session_state.mode = "launch"
                st.session_state.page = "launch_input"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.write("")
        
        # Virtual Executive Team Feature Cards
        st.markdown("<h3 style='margin-bottom:15px; color:#00D4FF; font-size:18px;'>YOUR DIGITAL BOARD MEMBERS</h3>", unsafe_allow_html=True)
        
        ag_col1, ag_col2 = st.columns(2)
        with ag_col1:
            st.markdown(
                """
                <div style='background: rgba(22, 29, 36, 0.5); padding: 15px; border-radius: 12px; border-left: 3px solid #00D4FF; margin-bottom: 12px;'>
                    <strong style='color:#FFFFFF; font-size:13px;'>🔵 Market Researcher / Validator</strong><br/>
                    <span style='font-size:11.5px; color:#8C9BA5;'>TAM capacity, CAGR demand curves, venture ecosystem momentum & customer segments.</span>
                </div>
                <div style='background: rgba(22, 29, 36, 0.5); padding: 15px; border-radius: 12px; border-left: 3px solid #9E9E9E; margin-bottom: 12px;'>
                    <strong style='color:#FFFFFF; font-size:13px;'>⚖️ Legal & Regulatory Navigator</strong><br/>
                    <span style='font-size:11.5px; color:#8C9BA5;'>World Bank Doing Business, licensing hurdles, regulatory burden & contract enforcement.</span>
                </div>
                <div style='background: rgba(22, 29, 36, 0.5); padding: 15px; border-radius: 12px; border-left: 3px solid #FF6B6B; margin-bottom: 12px;'>
                    <strong style='color:#FFFFFF; font-size:13px;'>🔴 Risk & Venture Hazards</strong><br/>
                    <span style='font-size:11.5px; color:#8C9BA5;'>Fragile States Index, currency exposure, macro risk for first-time market entrants.</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with ag_col2:
            st.markdown(
                """
                <div style='background: rgba(22, 29, 36, 0.5); padding: 15px; border-radius: 12px; border-left: 3px solid #FFB800; margin-bottom: 12px;'>
                    <strong style='color:#FFFFFF; font-size:13px;'>🟡 Competitive Intelligence / Scout</strong><br/>
                    <span style='font-size:11.5px; color:#8C9BA5;'>Incumbent analysis, competitor shares, product voids & strategic foothold barriers.</span>
                </div>
                <div style='background: rgba(22, 29, 36, 0.5); padding: 15px; border-radius: 12px; border-left: 3px solid #00FF88; margin-bottom: 12px;'>
                    <strong style='color:#FFFFFF; font-size:13px;'>⚙️ Operations & Launch Logistics</strong><br/>
                    <span style='font-size:11.5px; color:#8C9BA5;'>Logistics Performance Index (LPI), MVP execution feasibility & infrastructure scaling.</span>
                </div>
                <div style='background: rgba(22, 29, 36, 0.5); padding: 15px; border-radius: 12px; border-left: 3px solid #FFD700; margin-bottom: 12px;'>
                    <strong style='color:#FFFFFF; font-size:13px;'>💰 CFO & Capital Strategist</strong><br/>
                    <span style='font-size:11.5px; color:#8C9BA5;'>Real VC startup funding benchmarks, capital sizing & allocation strategy.</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    with col2:
        # Saved Sessions list
        st.markdown("<h3 style='margin-bottom:15px; color:#FFB800; font-size:18px;'>🏢 BOARDROOM RECS HISTORY</h3>", unsafe_allow_html=True)
        sessions = list_sessions()
        
        if not sessions:
            st.markdown(
                """
                <div style='background: rgba(22, 29, 36, 0.5); padding: 30px; border-radius: 16px; border: 1px dashed rgba(255,255,255,0.1); text-align:center; color:#505F6C;'>
                    <span style='font-size: 24px;'>📂</span><br/>
                    <span style='font-size:12px; margin-top:8px; display:block;'>No past boardroom sessions found on disk. Concurrently launch your first session!</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for s in sessions[:5]: # Show latest 5 sessions
                rec = s.get("decision", "DELAY ENTRY")
                badge_color = "#00FF88" if ("ENTER" in rec or "LAUNCH" in rec and "DO NOT" not in rec) else "#FF6B6B" if ("REJECT" in rec or "DO NOT" in rec) else "#FFB800"
                
                # Check mode indicator
                session_title = s.get("company", "Unknown")
                is_launch_session = (s.get("budget", 0) > 1000) or ("launch" in session_title.lower()) or (s.get("mode") == "launch")
                
                track_label = "🚀 NEW BUSINESS LAUNCH" if is_launch_session else "🏢 CORPORATE EXPANSION"
                track_col = "#FFB800" if is_launch_session else "#00D4FF"
                budget_display = f"${s['budget']:,.0f} USD" if s.get('budget', 0) > 1000 else f"${s['budget']}M USD"
                
                card_html = f"""
                <div style="background: rgba(22, 29, 36, 0.7); border: 1px solid rgba(255,255,255,0.05); border-left: 3px solid {track_col}; border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <span style="font-size:9.5px; color:{track_col}; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">{track_label}</span>
                        <span style="background: rgba(255,255,255,0.05); font-size:9.5px; padding:2px 8px; border-radius:10px; color:#8C9BA5;">{s.get('date', s['timeline'])}</span>
                    </div>
                    <div style="font-weight:700; color:#FFFFFF; font-size:13.5px; font-family:'Outfit'; margin-bottom:4px;">{session_title}</div>
                    <div style="font-size:11px; color:#8C9BA5; margin-bottom:8px;">
                        Target Market: <strong style="color:#D2DCE6;">{s['market']}</strong> &bull; Capital: <strong style="color:#D2DCE6;">{budget_display}</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.04); padding-top:6px;">
                        <span style="color:{badge_color}; font-size:11px; font-weight:800; letter-spacing:0.5px;">{rec}</span>
                        <span style="font-size:10.5px; color:#00D4FF; font-weight:600;">Confidence: {s['confidence']}%</span>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Load button for this session
                if st.button(f"Open Briefing: {session_title[:30]}", key=f"load_{s['filename']}"):
                    loaded_data = load_session(s['filename'])
                    if loaded_data:
                        st.session_state.results = loaded_data
                        if loaded_data.get("mode") == "launch" or "validation_roadmap" in loaded_data:
                            st.session_state.mode = "launch"
                            st.session_state.page = "launch_results"
                        else:
                            st.session_state.mode = "expansion"
                            st.session_state.page = "results"
                        st.rerun()

# ==========================================
# PAGE 2A: TRACK A INPUT FORM (EXPANSION)
# ==========================================
elif st.session_state.page == "input":
    col1, col2 = st.columns([7, 5])
    
    with col1:
        st.markdown("<h2 style='color:#FFFFFF; font-family: Outfit; font-size:24px; margin-top:0;'>CONVENE BOARD OF DIRECTORS 🏢</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#8C9BA5; font-size:13px; margin-top:-10px; margin-bottom:20px;'>Provide expansion variables to deploy AI analytical models.</p>", unsafe_allow_html=True)
        
        # Standard Streamlit Form with CSS Overrides
        with st.form("boardroom_input_form"):
            company = st.text_input("Company Name", value=st.session_state.company, placeholder="e.g., ABC Technologies", help="The name of the company seeking strategic expansion advice.")
            market = st.text_input("Target Market / Domain", value=st.session_state.market, placeholder="e.g., Singapore Smart Home Market", help="The specific market territory or sector you plan to enter.")
            
            # Numeric Budget Input (USD)
            init_budget = int(st.session_state.budget) if st.session_state.budget >= 10000 else 500000
            budget = st.number_input(
                "Proposed Expansion Budget ($ USD)",
                min_value=10000,
                max_value=500000000,
                value=init_budget,
                step=50000,
                help="Total allocation budget reserved for this corporate expansion initiative."
            )
            
            # Dropdown
            timeline = st.selectbox(
                "Strategic Execution Timeline",
                options=["6 Months", "1 Year", "2 Years", "5 Years"],
                index=["6 Months", "1 Year", "2 Years", "5 Years"].index(st.session_state.timeline) if st.session_state.timeline in ["6 Months", "1 Year", "2 Years", "5 Years"] else 1,
                help="The estimated timeframe set to complete target entry permits and reach full operations."
            )
            
            # Text area
            question = st.text_area(
                "Strategic Board Question",
                value=st.session_state.question,
                placeholder="e.g., Should we expand our smart home product line into Singapore with a $500,000 budget over 6 months?",
                help="Specify the core strategic problem the board needs to decide."
            )
            
            # Optional Business Model
            business_model = st.text_input(
                "Business Model / Target Customer (Optional)",
                value=st.session_state.get("business_model", ""),
                placeholder="e.g., B2B enterprise subscription or Direct-to-Consumer retail",
                help="Optional additional context on business model or target customer profile."
            )
            
            # Submit Button
            submit_btn = st.form_submit_button("CONVENE BOARDROOM 🏢")
            
            if submit_btn:
                if not company.strip() or not market.strip() or not question.strip():
                    st.error("❌ Please complete all required form inputs (Company Name, Target Market, and Strategic Question) before convening the board.")
                else:
                    # Save inputs to session state
                    st.session_state.company = company
                    st.session_state.market = market
                    st.session_state.budget = budget
                    st.session_state.timeline = timeline
                    st.session_state.question = question
                    st.session_state.business_model = business_model
                    
                    # Clear previous results to avoid stale state leakage
                    st.session_state.results = None
                    
                    # Navigate to execution page
                    st.session_state.mode = "expansion"
                    st.session_state.page = "execution"
                    st.rerun()
                    
        # Small back link
        if st.button("← Back to Strategic Selection", key="btn_back_input"):
            st.session_state.page = "landing"
            st.rerun()
            
    with col2:
        st.write("")
        st.write("")
        st.markdown("<h3 style='color:#00D4FF; font-family: Outfit; font-size:16px; margin-bottom:12px;'>STRATEGIC GUIDELINE PROFILE</h3>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="glass-card" style="border-left:3px solid #00D4FF; padding:20px;">
                <h4 style="margin-top:0; color:#FFFFFF; font-size:14.5px;">Model Core Directives</h4>
                <ul style="font-size:12px; color:#B3C3D0; padding-left:15px; line-height:1.6;">
                    <li><strong>Market Researcher</strong> models demand capacity, TAM volumes, and adoption curves.</li>
                    <li><strong>Competitive Intel</strong> structures incumbent share matrices and identifies product voids.</li>
                    <li><strong>General Counsel</strong> conducts audits for international permit compliance and licensing schedules.</li>
                    <li><strong>Chief Operations Officer</strong> projects supply chain, physical sites, and operational setups.</li>
                    <li><strong>Chief Risk Officer</strong> structures geopolitical, currency, and macro-economic exposure matrices.</li>
                    <li><strong>Chief Financial Officer</strong> evaluates capital allocation yields, payback break-even thresholds, and NPV indicators.</li>
                    <li><strong>CEO Agent</strong> synthesizes consolidated board arguments to formulate the final recommendation.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

# ==========================================
# PAGE 2B: TRACK B INPUT FORM (NEW BUSINESS LAUNCH)
# ==========================================
elif st.session_state.page == "launch_input":
    col1, col2 = st.columns([7, 5])
    
    with col1:
        st.markdown("<h2 style='color:#FFFFFF; font-family: Outfit; font-size:24px; margin-top:0;'>🚀 NEW BUSINESS LAUNCH BOARDROOM</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#8C9BA5; font-size:13px; margin-top:-10px; margin-bottom:20px;'>Pressure-test a brand-new business before committing capital.</p>", unsafe_allow_html=True)
        
        with st.form("launch_input_form"):
            business_idea = st.text_area(
                "Business Venture Idea",
                value=st.session_state.business_idea,
                placeholder="e.g., AI-powered autonomous precision agriculture platform delivering real-time satellite crop disease analytics to Australian grain farms.",
                help="Describe the new venture, product, or service you plan to build and launch from scratch.",
                height=110
            )
            
            target_market = st.text_input(
                "Target Country / Market",
                value=st.session_state.target_market,
                placeholder="e.g., Australia",
                help="The specific country or geographic territory where the venture will launch."
            )
            
            capital_budget = st.number_input(
                "Proposed Launch Budget ($ USD)",
                min_value=10000,
                max_value=50000000,
                value=st.session_state.capital_budget,
                step=50000,
                help="Total available starting capital / budget (in USD) allocated for launch and runway."
            )
            
            timeline = st.selectbox(
                "Launch Timeline",
                options=["6 Months", "12 Months", "18 Months", "24 Months"],
                index=["6 Months", "12 Months", "18 Months", "24 Months"].index(st.session_state.launch_timeline) if st.session_state.launch_timeline in ["6 Months", "12 Months", "18 Months", "24 Months"] else 1,
                help="The estimated operational timeline to build MVP, register entities, and achieve first customer revenue."
            )
            
            strategic_question = st.text_area(
                "Strategic Board Question",
                value=st.session_state.strategic_board_question,
                placeholder="e.g., Should we launch an AI agritech platform in Australia with a $500,000 launch budget over 12 months?",
                help="The core strategic question for the Founder Board of Directors.",
                height=80
            )
            
            target_customer = st.text_input(
                "Business Model / Target Customer (Optional)",
                value=st.session_state.target_customer,
                placeholder="e.g., B2B SaaS subscription for mid-to-large commercial farms ($1,200/mo)",
                help="Optional additional context on target customer profile or monetization model."
            )
            
            submit_launch_btn = st.form_submit_button("🚀 CONVENE LAUNCH BOARDROOM")
            
            if submit_launch_btn:
                if not business_idea.strip() or not target_market.strip() or not strategic_question.strip():
                    st.error("❌ Please complete all required inputs (Business Idea, Target Country, and Strategic Question) before convening the board.")
                else:
                    st.session_state.business_idea = business_idea
                    st.session_state.target_market = target_market
                    st.session_state.capital_budget = capital_budget
                    st.session_state.launch_timeline = timeline
                    st.session_state.strategic_board_question = strategic_question
                    st.session_state.target_customer = target_customer
                    
                    st.session_state.mode = "launch"
                    st.session_state.page = "launch_execution"
                    st.rerun()
                    
        if st.button("← Back to Strategic Selection", key="btn_back_launch_input"):
            st.session_state.page = "landing"
            st.rerun()
            
    with col2:
        st.write("")
        st.write("")
        st.markdown("<h3 style='color:#FFB800; font-family: Outfit; font-size:16px; margin-bottom:12px;'>VENTURE BOARD DIRECTIVES</h3>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="glass-card" style="border-left:3px solid #FFB800; padding:20px;">
                <h4 style="margin-top:0; color:#FFFFFF; font-size:14.5px;">Track B Specialist Roles</h4>
                <ul style="font-size:12px; color:#B3C3D0; padding-left:15px; line-height:1.6;">
                    <li><strong>📊 Market Validator</strong> assesses startup ecosystem momentum, local VC aggregate funding, and demand signals.</li>
                    <li><strong>🔍 Competitive Scout</strong> tracks market leader concentration and identifies early-stage foothold voids.</li>
                    <li><strong>📜 Regulatory Navigator</strong> audits World Bank ease of doing business, days to start business, and licensing.</li>
                    <li><strong>🚀 Launch Operations</strong> evaluates lean MVP operating logistics, transport reliability, and LPI scores.</li>
                    <li><strong>🛡️ Venture Risk</strong> evaluates Fragile States Index (FSI) exposure for first-time entrants with zero local presence.</li>
                    <li><strong>💎 Capital Strategist</strong> compares proposed budget against empirical startup funding averages in the target country.</li>
                    <li><strong>👑 Founder CEO</strong> synthesizes board findings into a <strong>LAUNCH / VALIDATE FIRST / DO NOT LAUNCH</strong> verdict with a 3-5 step validation roadmap.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

# ==========================================
# PAGE 3A: TRACK A BOARDROOM EXECUTION (LIVE)
# ==========================================
elif st.session_state.page == "execution":
    from config import format_budget_display, parse_budget_numeric
    budget_fmt = format_budget_display(parse_budget_numeric(st.session_state.budget))
    
    st.markdown("<h2 style='text-align:center; color:#FFFFFF; font-family: Outfit; font-size:24px; margin-top:0;'>🏢 THE BOARD DEBATE IN PROGRESS</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#8C9BA5; font-size:13px; margin-top:-10px;'>Company: <strong>{st.session_state.company}</strong> | Expansion target: <strong>{st.session_state.market}</strong> | Budget: <strong>{budget_fmt}</strong></p>", unsafe_allow_html=True)
    
    col_status, col_chat = st.columns([5, 7])
    
    # Placeholders for dynamic rendering
    with col_status:
        st.markdown("<h3 style='color:#00D4FF; font-size:16px; margin-bottom:12px;'>BOARD MEMBER ENGAGEMENTS</h3>", unsafe_allow_html=True)
        status_box = st.empty()
        
        st.write("")
        st.markdown("<h3 style='color:#FFB800; font-size:16px; margin-bottom:12px;'>CONSENSUS ESTIMATES (INTERIM)</h3>", unsafe_allow_html=True)
        metrics_box = st.empty()
        
    with col_chat:
        st.markdown("<h3 style='color:#FFFFFF; font-size:16px; margin-bottom:12px;'>LIVE MEETING TRANSCRIPT</h3>", unsafe_allow_html=True)
        chat_box = st.empty()
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        next_button_box = st.empty()
        
    statuses = {a["id"]: "PENDING" for a in CORE_AGENTS}
    statuses["CEO"] = "PENDING"
    
    current_transcript = []
    current_metrics = {"opportunity_score": 0, "risk_mitigation_score": 0, "market_readiness": 0, "financial_feasibility": 0}
    
    def render_boardroom_state():
        status_html = "<div style='display:flex; flex-direction:column; gap:10px; background: rgba(22, 29, 36, 0.7); border:1px solid rgba(255,255,255,0.05); padding:16px; border-radius:16px;'>"
        for a in CORE_AGENTS:
            aid = a["id"]
            stat = statuses[aid]
            badge_class = "status-thinking" if stat == "THINKING" else "status-speaking" if stat == "SPEAKING" else "status-completed" if stat == "COMPLETED" else ""
            stat_text = stat if stat != "PENDING" else "Waiting..."
            status_html += f"""
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:8px;">
                <span style="font-weight:600; font-size:12.5px; color:#FFFFFF;">{a['icon']} {a['name']}</span>
                <span class="status-badge {badge_class}" style="font-size:9.5px;">{stat_text}</span>
            </div>
            """
        ceo_stat = statuses["CEO"]
        ceo_badge = "status-thinking" if ceo_stat == "THINKING" else "status-speaking" if ceo_stat == "SPEAKING" else "status-completed" if ceo_stat == "COMPLETED" else ""
        ceo_text = ceo_stat if ceo_stat != "PENDING" else "Waiting..."
        status_html += f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding-top:4px;">
            <span style="font-weight:700; font-size:12.5px; color:#FFD700;">🎯 Corporate CEO</span>
            <span class="status-badge {ceo_badge}" style="font-size:9.5px;">{ceo_text}</span>
        </div>
        """
        status_html += "</div>"
        status_box.markdown(clean_html(status_html), unsafe_allow_html=True)
        
        metrics_html = f"""
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
            <div class="metric-container" style="background: rgba(22, 29, 36, 0.7); border-radius:12px; padding:12px; text-align:center;">
                <div class="metric-label" style="font-size:10px; color:#8C9BA5;">OPPORTUNITY</div>
                <div class="metric-value" style="font-size:24px; color:#00D4FF; font-weight:800; font-family:'Outfit';">{current_metrics['opportunity_score']}%</div>
            </div>
            <div class="metric-container" style="background: rgba(22, 29, 36, 0.7); border-radius:12px; padding:12px; text-align:center;">
                <div class="metric-label" style="font-size:10px; color:#8C9BA5;">RISK MITIGATION</div>
                <div class="metric-value" style="font-size:24px; color:#FF6B6B; font-weight:800; font-family:'Outfit';">{current_metrics['risk_mitigation_score']}%</div>
            </div>
            <div class="metric-container" style="background: rgba(22, 29, 36, 0.7); border-radius:12px; padding:12px; text-align:center;">
                <div class="metric-label" style="font-size:10px; color:#8C9BA5;">MARKET READINESS</div>
                <div class="metric-value" style="font-size:24px; color:#00FF88; font-weight:800; font-family:'Outfit';">{current_metrics['market_readiness']}%</div>
            </div>
            <div class="metric-container" style="background: rgba(22, 29, 36, 0.7); border-radius:12px; padding:12px; text-align:center;">
                <div class="metric-label" style="font-size:10px; color:#8C9BA5;">FINANCIAL YIELD</div>
                <div class="metric-value" style="font-size:24px; color:#FFB800; font-weight:800; font-family:'Outfit';">{current_metrics['financial_feasibility']}%</div>
            </div>
        </div>
        """
        metrics_box.markdown(clean_html(metrics_html), unsafe_allow_html=True)
        
        chat_html = "<div style='max-height: 420px; overflow-y: auto; display:flex; flex-direction:column; padding-right:10px;'>"
        if not current_transcript:
            chat_html += """
            <div style="background: rgba(22, 29, 36, 0.4); padding: 40px; border-radius:16px; border:1px dashed rgba(255,255,255,0.05); text-align:center; color:#505F6C; font-size:13px; font-style:italic;">
                🗣️ Establishing secure server link with executive LLM nodes...<br/>Board members are reviewing expansion documents.
            </div>
            """
        else:
            for t in current_transcript:
                rec_badge_color = "#00FF88" if t['recommendation'] in ["YES", "ENTER", "ENTER MARKET"] else "#FF6B6B" if t['recommendation'] in ["NO", "REJECT", "REJECT EXPANSION", "DO NOT ENTER"] else "#FFB800"
                dv_tag = " • Verified ✓" if t.get('data_verified') else ""
                chat_html += f"""
                <div class="chat-bubble" style="border-left: 3px solid {t['color']}; margin-bottom:12px; padding:12px 16px; background: rgba(22, 29, 36, 0.6); border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="font-weight:700; font-size:12.5px; color:#FFFFFF; font-family:'Outfit';">{t['icon']} {t['name']}</span>
                        <span style="color:{rec_badge_color}; font-size:10px; font-weight:700; text-transform:uppercase;">{t['recommendation']} (Conf: {t['confidence']}%{dv_tag})</span>
                    </div>
                    <div style="font-size:12px; color:#D2DCE6; font-style:italic; line-height:1.45;">
                        "{t['dialogue']}"
                    </div>
                </div>
                """
        chat_html += "</div>"
        chat_box.markdown(clean_html(chat_html), unsafe_allow_html=True)

    render_boardroom_state()
    
    def boardroom_callback(agent_id, phase, dialogue_msg=None, interim_consensus=None):
        if phase == "THINKING":
            statuses[agent_id] = "THINKING"
        elif phase == "COMPLETED":
            statuses[agent_id] = "COMPLETED"
            if dialogue_msg:
                current_transcript.append(dialogue_msg)
            if interim_consensus:
                for k, v in interim_consensus.items():
                    current_metrics[k] = v
        render_boardroom_state()
        
    with st.spinner("Conceiving corporate expansion debate..."):
        try:
            results = run_boardroom_session(
                company=st.session_state.company,
                market=st.session_state.market,
                budget=st.session_state.budget,
                timeline=st.session_state.timeline,
                question=st.session_state.question,
                progress_callback=boardroom_callback,
                business_model=st.session_state.get("business_model", "")
            )
            
            st.session_state.results = results
            save_session(results)
            
            st.success("✅ Virtual Executive Board meeting concluded successfully!")
            
            if next_button_box.button("ACCESS EXECUTIVE BRIEFING 📂", key="btn_view_results"):
                st.session_state.page = "results"
                st.rerun()
                
        except Exception as err:
            st.error(f"An unexpected error occurred during execution: {err}")
            if st.button("Back to Input Form", key="btn_err_back"):
                st.session_state.page = "input"
                st.rerun()

# ==========================================
# PAGE 3B: TRACK B BOARDROOM EXECUTION (LIVE)
# ==========================================
elif st.session_state.page == "launch_execution":
    st.markdown("<h2 style='text-align:center; color:#FFFFFF; font-family: Outfit; font-size:24px; margin-top:0;'>🚀 THE LAUNCH BOARDROOM DEBATE IN PROGRESS</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#8C9BA5; font-size:13px; margin-top:-10px;'>Venture: <strong>{st.session_state.business_idea[:50]}...</strong> | Target Market: <strong>{st.session_state.target_market}</strong> | Budget: <strong>${st.session_state.capital_budget:,.0f}</strong></p>", unsafe_allow_html=True)
    
    col_status, col_chat = st.columns([5, 7])
    
    with col_status:
        st.markdown("<h3 style='color:#FFB800; font-size:16px; margin-bottom:12px;'>VENTURE SPECIALIST ENGAGEMENTS</h3>", unsafe_allow_html=True)
        status_box = st.empty()
        
        st.write("")
        st.markdown("<h3 style='color:#00D4FF; font-size:16px; margin-bottom:12px;'>VENTURE CONSENSUS ESTIMATES (INTERIM)</h3>", unsafe_allow_html=True)
        metrics_box = st.empty()
        
    with col_chat:
        st.markdown("<h3 style='color:#FFFFFF; font-size:16px; margin-bottom:12px;'>LIVE MEETING TRANSCRIPT</h3>", unsafe_allow_html=True)
        chat_box = st.empty()
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        next_button_box = st.empty()
        
    launch_statuses = {a["id"]: "PENDING" for a in TRACK_B_AGENTS}
    launch_statuses["FOUNDER_CEO"] = "PENDING"
    
    current_transcript = []
    current_metrics = {"opportunity_score": 0, "risk_mitigation_score": 0, "market_readiness": 0, "financial_feasibility": 0}
    
    def render_launch_boardroom_state():
        status_html = "<div style='display:flex; flex-direction:column; gap:10px; background: rgba(22, 29, 36, 0.7); border:1px solid rgba(255,255,255,0.05); padding:16px; border-radius:16px;'>"
        for a in TRACK_B_AGENTS:
            aid = a["id"]
            stat = launch_statuses[aid]
            badge_class = "status-thinking" if stat == "THINKING" else "status-speaking" if stat == "SPEAKING" else "status-completed" if stat == "COMPLETED" else ""
            stat_text = stat if stat != "PENDING" else "Waiting..."
            status_html += f"""
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:8px;">
                <span style="font-weight:600; font-size:12.5px; color:#FFFFFF;">{a['icon']} {a['name']}</span>
                <span class="status-badge {badge_class}" style="font-size:9.5px;">{stat_text}</span>
            </div>
            """
        ceo_stat = launch_statuses["FOUNDER_CEO"]
        ceo_badge = "status-thinking" if ceo_stat == "THINKING" else "status-speaking" if ceo_stat == "SPEAKING" else "status-completed" if ceo_stat == "COMPLETED" else ""
        ceo_text = ceo_stat if ceo_stat != "PENDING" else "Waiting..."
        status_html += f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding-top:4px;">
            <span style="font-weight:700; font-size:12.5px; color:#FFD700;">👑 Founder CEO</span>
            <span class="status-badge {ceo_badge}" style="font-size:9.5px;">{ceo_text}</span>
        </div>
        """
        status_html += "</div>"
        status_box.markdown(clean_html(status_html), unsafe_allow_html=True)
        
        metrics_html = f"""
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
            <div class="metric-container" style="background: rgba(22, 29, 36, 0.7); border-radius:12px; padding:12px; text-align:center;">
                <div class="metric-label" style="font-size:10px; color:#8C9BA5;">OPPORTUNITY</div>
                <div class="metric-value" style="font-size:24px; color:#00D4FF; font-weight:800; font-family:'Outfit';">{current_metrics['opportunity_score']}%</div>
            </div>
            <div class="metric-container" style="background: rgba(22, 29, 36, 0.7); border-radius:12px; padding:12px; text-align:center;">
                <div class="metric-label" style="font-size:10px; color:#8C9BA5;">VENTURE STABILITY</div>
                <div class="metric-value" style="font-size:24px; color:#FF6B6B; font-weight:800; font-family:'Outfit';">{current_metrics['risk_mitigation_score']}%</div>
            </div>
            <div class="metric-container" style="background: rgba(22, 29, 36, 0.7); border-radius:12px; padding:12px; text-align:center;">
                <div class="metric-label" style="font-size:10px; color:#8C9BA5;">LAUNCH READINESS</div>
                <div class="metric-value" style="font-size:24px; color:#00FF88; font-weight:800; font-family:'Outfit';">{current_metrics['market_readiness']}%</div>
            </div>
            <div class="metric-container" style="background: rgba(22, 29, 36, 0.7); border-radius:12px; padding:12px; text-align:center;">
                <div class="metric-label" style="font-size:10px; color:#8C9BA5;">CAPITAL FEASIBILITY</div>
                <div class="metric-value" style="font-size:24px; color:#FFB800; font-weight:800; font-family:'Outfit';">{current_metrics['financial_feasibility']}%</div>
            </div>
        </div>
        """
        metrics_box.markdown(clean_html(metrics_html), unsafe_allow_html=True)
        
        chat_html = "<div style='max-height: 420px; overflow-y: auto; display:flex; flex-direction:column; padding-right:10px;'>"
        if not current_transcript:
            chat_html += """
            <div style="background: rgba(22, 29, 36, 0.4); padding: 40px; border-radius:16px; border:1px dashed rgba(255,255,255,0.05); text-align:center; color:#505F6C; font-size:13px; font-style:italic;">
                🗣️ Establishing secure server link with executive LLM nodes...<br/>Venture specialists are reviewing empirical market datasets.
            </div>
            """
        else:
            for t in current_transcript:
                rec_val = t.get('recommendation', 'MAYBE')
                rec_badge_color = "#00FF88" if (rec_val in ["YES", "LAUNCH"]) else "#FF6B6B" if (rec_val in ["NO", "DO NOT LAUNCH"]) else "#FFB800"
                dv_tag = " • Verified ✓" if t.get('data_verified') else ""
                chat_html += f"""
                <div class="chat-bubble" style="border-left: 3px solid {t['color']}; margin-bottom:12px; padding:12px 16px; background: rgba(22, 29, 36, 0.6); border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="font-weight:700; font-size:12.5px; color:#FFFFFF; font-family:'Outfit';">{t['icon']} {t['name']}</span>
                        <span style="color:{rec_badge_color}; font-size:10px; font-weight:700; text-transform:uppercase;">{rec_val} (Conf: {t['confidence']}%{dv_tag})</span>
                    </div>
                    <div style="font-size:12px; color:#D2DCE6; font-style:italic; line-height:1.45;">
                        "{t['dialogue']}"
                    </div>
                </div>
                """
        chat_html += "</div>"
        chat_box.markdown(clean_html(chat_html), unsafe_allow_html=True)

    render_launch_boardroom_state()
    
    def launch_callback(agent_id, phase, dialogue_msg=None, interim_consensus=None):
        if phase == "THINKING":
            launch_statuses[agent_id] = "THINKING"
        elif phase == "COMPLETED":
            launch_statuses[agent_id] = "COMPLETED"
            if dialogue_msg:
                current_transcript.append(dialogue_msg)
            if interim_consensus:
                for k, v in interim_consensus.items():
                    current_metrics[k] = v
        render_launch_boardroom_state()
        
    with st.spinner("Conceiving venture launch debate with 7 specialist nodes..."):
        try:
            results = run_track_b_session(
                business_idea=st.session_state.business_idea,
                target_market=st.session_state.target_market,
                capital_budget=st.session_state.capital_budget,
                timeline=st.session_state.launch_timeline,
                strategic_question=st.session_state.strategic_board_question,
                progress_callback=launch_callback
            )
            
            st.session_state.results = results
            save_session(results)
            
            st.success("✅ Venture Launch Board meeting concluded successfully!")
            
            if next_button_box.button("ACCESS VENTURE BRIEFING 📂", key="btn_view_launch_results"):
                st.session_state.page = "launch_results"
                st.rerun()
                
        except Exception as err:
            st.error(f"An unexpected error occurred during execution: {err}")
            if st.button("Back to Launch Form", key="btn_err_launch_back"):
                st.session_state.page = "launch_input"
                st.rerun()

# ==========================================
# PAGE 4A: TRACK A RESULTS DASHBOARD (CORPORATE EXPANSION)
# ==========================================
elif st.session_state.page == "results":
    res = st.session_state.results
    if not res:
        st.warning("⚠️ No active boardroom session details found. Please convene the board first.")
        if st.button("New Session Form", key="btn_no_res_new"):
            st.session_state.page = "input"
            st.rerun()
    else:
        decision = res.get("final_recommendation", res.get("final_decision", res.get("ceo_decision", "DEFER / VALIDATE")))
        confidence = res.get("confidence", res.get("ceo_confidence", 80))
        data_verified = res.get("data_verified", True)
        company = res.get("company", "Company")
        target_market = res.get("market", res.get("target_market", "Target Market"))
        budget = res.get("budget", 500000)
        timeline = res.get("timeline", "12 Months")
        transcript = res.get("transcript", [])
        critical_blockers = res.get("critical_blockers", [])
        validation_roadmap = res.get("validation_roadmap", [])
        mind_change_thresholds = res.get("mind_change_thresholds", [])
        reports = res.get("specialist_reports", {})
        cfo_report = reports.get("CFO", {})
        status = res.get("status", "success")
        
        # 1. Executive Decision Header
        render_executive_decision_header(
            business_idea=company,
            target_market=target_market,
            budget=budget,
            timeline=timeline,
            final_decision=decision,
            confidence=confidence,
            data_verified=data_verified,
            status=status,
            track="expansion",
            data_status=res.get("data_status") or res.get("evidence_summary", {}).get("data_status"),
            evidence_summary=res.get("evidence_summary")
        )
        
        # 1.1 Core Expansion Consensus Metrics
        metrics = res.get("consensus_metrics", {})
        met_col1, met_col2, met_col3, met_col4 = st.columns(4)
        with met_col1:
            render_metric_ring(metrics.get("opportunity_score", 0), "OPPORTUNITY", "TAM capacity & market demand.")
        with met_col2:
            render_metric_ring(metrics.get("risk_mitigation_score", 0), "RISK MITIGATION", "Deterministic risk coverage & mitigation.")
        with met_col3:
            render_metric_ring(metrics.get("market_readiness", 0), "EXPANSION READINESS", "Operational readiness & regulatory clearance.")
        with met_col4:
            render_metric_ring(metrics.get("financial_feasibility", 0), "FINANCIAL YIELD", "Capital adequacy & payback timeframe.")
            
        st.write("")
        
        # Quick Action Controls Row
        act_col1, act_col2, act_col3 = st.columns(3)
        with act_col1:
            with st.spinner("Compiling ReportLab PDF..."):
                try:
                    import importlib
                    import services.report_generator
                    importlib.reload(services.report_generator)
                    pdf_data = services.report_generator.generate_pdf_report(res)
                    filename = f"boardroom_briefing_{str(company).replace(' ', '_').lower()}.pdf"
                    st.download_button(
                        label="DOWNLOAD EXECUTIVE PDF 📥",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        key="btn_pdf_download"
                    )
                except Exception as pdf_err:
                    st.error(f"Error compiling PDF: {pdf_err}")
        
        with act_col2:
            if st.button("REPLAY MEETING SIMULATION 🔄", key="btn_replay_meeting"):
                st.session_state.page = "execution"
                st.rerun()
                
        with act_col3:
            if st.button("CONVENE NEW BOARD 🏢", key="btn_new_meeting"):
                st.session_state.page = "input"
                st.session_state.results = None
                st.rerun()
                
        col_main, col_sidebar = st.columns([8, 4])
        
        with col_main:
            # 2. Decision Explanation / CEO Executive Rationale
            render_decision_explanation_card(res.get("decision_explanation"))
            
            # 3. Deterministic Decision Rule Trace (RULE-001..RULE-009)
            det_eval = res.get("deterministic_eval", {})
            render_deterministic_rule_panel(
                rule_evaluations=res.get("rule_evaluations", []),
                rules_passed=det_eval.get("rules_passed_count", 0),
                total_rules=det_eval.get("total_rules", 9)
            )
            
            # 4. Canonical Structured Evidence Ledger (EVID-001..)
            render_evidence_ledger_table(res.get("evidence_ledger", []))
            
            # 5. Deterministic Risk Mitigation & Residual Exposure Panel
            render_risk_mitigation_panel(res.get("risk_mitigation_breakdown"), res.get("risk_matrix"))
            
            # 6. Sovereign & Expansion Risk Matrix (RISK-001..)
            render_risk_matrix_panel(res.get("risk_matrix", []))
            
            # 7. Specialist Position Matrix
            render_specialist_position_matrix(transcript)
            
            # 8. Critical Blockers Priority
            render_critical_blockers_card(critical_blockers)
            
            # 9. Capital Benchmark Card
            render_capital_benchmark_card(target_market, budget, cfo_report)
            
            # 10. Executive Action Plan (4 Phases)
            render_executive_action_plan(validation_roadmap)
            
        with col_sidebar:
            st.markdown("<h3 style='color:#00D4FF; font-size:16px; margin-bottom:12px; font-family:Outfit;'>BOARD DEBATE AUDITS</h3>", unsafe_allow_html=True)
            
            for t in transcript:
                aid = t.get("agent_id")
                if aid == "CEO":
                    continue
                
                render_agent_vote_card(
                    agent_name=t.get("name"),
                    role=t.get("icon") + " " + CORE_AGENTS[[a["id"] for a in CORE_AGENTS].index(aid)]["name"].split()[-1] if aid in [a["id"] for a in CORE_AGENTS] else t.get("name"),
                    vote=t.get("recommendation"),
                    confidence=t.get("confidence"),
                    analysis=t.get("analysis"),
                    color=t.get("color")
                )
                st.write("")
                
            # What Would Change The Board's Mind
            render_what_would_change_mind_card(mind_change_thresholds)
                
        with st.expander("🗣️ VIEW BOARDROOM MEETING CHAT TRANSCRIPT"):
            for t in transcript:
                render_chat_bubble(
                    name=t.get("name"),
                    icon=t.get("icon"),
                    dialogue=t.get("dialogue"),
                    color=t.get("color")
                )


# ==========================================
# PAGE 4B: TRACK B RESULTS DASHBOARD (VENTURE LAUNCH)
# ==========================================
elif st.session_state.page == "launch_results":
    res = st.session_state.results
    if not res:
        st.warning("⚠️ No active venture launch details found. Please convene the launch board first.")
        if st.button("New Launch Form", key="btn_no_res_launch_new"):
            st.session_state.page = "launch_input"
            st.rerun()
    else:
        decision = res.get("final_recommendation", res.get("final_decision", res.get("ceo_decision", "VALIDATE FIRST")))
        confidence = res.get("confidence", res.get("ceo_confidence", 70))
        data_verified = res.get("data_verified", True)
        business_idea = res.get("business_idea", res.get("company", "New Venture Idea"))
        target_market = res.get("target_market", res.get("market", "Target Market"))
        budget = res.get("capital_budget", res.get("budget", 500000))
        timeline = res.get("timeline", "12 Months")
        transcript = res.get("transcript", [])
        agreement_analysis = res.get("agreement_analysis", {})
        disagreements = res.get("disagreements", {})
        critical_blockers = res.get("critical_blockers", [])
        validation_roadmap = res.get("validation_roadmap", [])
        mind_change_thresholds = res.get("mind_change_thresholds", [])
        reports = res.get("specialist_reports", {})
        capital_report = reports.get("CAPITAL_STRATEGIST", {})
        status = res.get("status", "success")
        
        # 1. Executive Decision Header
        render_executive_decision_header(
            business_idea=business_idea,
            target_market=target_market,
            budget=budget,
            timeline=timeline,
            final_decision=decision,
            confidence=confidence,
            data_verified=data_verified,
            status=status
        )
        
        # 1.1 Core Venture Consensus Metrics
        metrics = res.get("consensus_metrics", {})
        explanations = metrics.get("explanations", {})
        met_col1, met_col2, met_col3, met_col4 = st.columns(4)
        with met_col1:
            render_metric_ring(
                metrics.get("opportunity_score", 0),
                "OPPORTUNITY",
                explanations.get("opportunity_score", "TAM capacity & competitive differentiation.")
            )
        with met_col2:
            render_metric_ring(
                metrics.get("risk_mitigation_score", 0),
                "RISK MITIGATION",
                explanations.get("risk_mitigation_score", "Deterministic risk coverage & mitigation.")
            )
        with met_col3:
            render_metric_ring(
                metrics.get("market_readiness", metrics.get("launch_readiness_score", 0)),
                "LAUNCH READINESS",
                explanations.get("market_readiness", explanations.get("launch_readiness_score", "Commercial infrastructure & legal clearance."))
            )
        with met_col4:
            render_metric_ring(
                metrics.get("financial_feasibility", metrics.get("capital_feasibility_score", 0)),
                "CAPITAL FEASIBILITY",
                explanations.get("financial_feasibility", explanations.get("capital_feasibility_score", "Benchmark calibration & runway."))
            )
        st.write("")
        
        # 1.2 Discrepancy Safety Alert (if any LLM divergence was caught and neutralized)
        render_discrepancy_alert(res.get("discrepancies", []))
        
        # 2. Compact Board Activity Summary
        render_board_activity_summary(transcript, agreement_analysis, disagreements, critical_blockers)
        
        # 3. Visual Decision Timeline
        render_decision_timeline(transcript, decision, status)
        
        # 3.1 Judge Audit & Verification Explorer
        render_judge_audit_explorer(res)
        
        col_main, col_sidebar = st.columns([8, 4])
        
        with col_main:
            # 4. Step 8 Decision Intelligence: WHY THE BOARD DECIDED THIS
            render_decision_explanation_card(res.get("decision_explanation"))
            
            # Trust & Auditability Verification Panel
            render_why_trust_panel(res)
            
            # 5. Deterministic Decision Rule Trace (RULE-001..RULE-008)
            det_eval = res.get("deterministic_eval", {})
            render_deterministic_rule_panel(
                rule_evaluations=res.get("rule_evaluations", []),
                rules_passed=det_eval.get("rules_passed_count", 0),
                total_rules=det_eval.get("total_rules", 8)
            )
            
            # 6. Canonical Structured Evidence Ledger (EVID-001..)
            render_evidence_ledger_table(res.get("evidence_ledger", []))
            
            # 7. Deterministic Risk Mitigation & Residual Exposure Panel
            render_risk_mitigation_panel(res.get("risk_mitigation_breakdown"), res.get("risk_matrix"))
            
            # 7.1 Sovereign & Venture Risk Matrix (RISK-001..)
            render_risk_matrix_panel(res.get("risk_matrix", []))
            
            # 8. Step 10: Board Consensus Intelligence
            render_board_consensus_intelligence(agreement_analysis, transcript)
            
            # 9. Step 10: Specialist Position Matrix
            render_specialist_position_matrix(transcript)
            
            # 10. Step 10: Evidence Quality & Coverage
            render_evidence_quality_panel(agreement_analysis, transcript)
            
            # 11. Step 10: Evidence vs Assumption (What we know / don't know)
            render_what_we_know_panel(transcript, agreement_analysis)
            
            # 12. Step 10: Strategic Disagreements Map
            render_disagreements_section(disagreements)
            
            # 13. Step 10: Critical Blockers Priority
            render_critical_blockers_card(critical_blockers)
            
            # 14. Venture Capital Benchmark Card
            render_capital_benchmark_card(target_market, budget, capital_report)
            
            # 15. Step 10: What Would Change The Board's Mind?
            render_what_would_change_mind_card(mind_change_thresholds)
            
            # 16. Step 10: Executive Action Plan (4 Phases)
            render_executive_action_plan(validation_roadmap)
            
            # 17. Step 10: Data Source Transparency
            render_data_sources_table(transcript)
            
            # 18. Founder CEO Executive Rationale Card
            ceo_rationale_html = f"""
            <div style="font-size: 13.5px; line-height: 1.6; color: #D2DCE6;">
                {res.get('ceo_rationale', res.get('rationale', 'No rationale provided.'))}
            </div>
            """
            render_glass_card("👑 FOUNDER CEO VERDICT & SYNTHESIS", ceo_rationale_html, "#FFD700")
            
            # 19. Action Buttons Row
            act_col1, act_col2, act_col3 = st.columns(3)
            
            with act_col1:
                with st.spinner("Compiling ReportLab PDF..."):
                    try:
                        import importlib
                        import services.report_generator
                        importlib.reload(services.report_generator)
                        pdf_data = services.report_generator.generate_pdf_report(res)
                        idea_slug = business_idea[:25].replace(' ', '_').lower()
                        filename = f"venture_launch_briefing_{idea_slug}.pdf"
                        st.download_button(
                            label="DOWNLOAD EXECUTIVE PDF 📥",
                            data=pdf_data,
                            file_name=filename,
                            mime="application/pdf",
                            key="btn_pdf_launch_download"
                        )
                    except Exception as pdf_err:
                        st.error(f"Error compiling PDF: {pdf_err}")
            
            with act_col2:
                if st.button("REPLAY LAUNCH SIMULATION 🔄", key="btn_replay_launch_meeting"):
                    st.session_state.page = "launch_execution"
                    st.rerun()
                    
            with act_col3:
                if st.button("CONVENE NEW VENTURE 🚀", key="btn_new_launch_meeting"):
                    st.session_state.page = "launch_input"
                    st.session_state.results = None
                    st.rerun()
                    
            st.write("")
            # 20. Step 10: Traceable Decision Trace Audit Trail
            render_decision_trace_card(res.get("decision_trace"))
                    
        with col_sidebar:
            st.markdown("<h3 style='color:#FFB800; font-size:16px; margin-bottom:12px; font-family:Outfit;'>VENTURE SPECIALIST AUDITS</h3>", unsafe_allow_html=True)
            
            for t in transcript:
                aid = t.get("agent_id")
                if aid == "FOUNDER_CEO":
                    continue
                
                render_agent_vote_card(
                    agent_name=t.get("name"),
                    role=t.get("role", t.get("icon") + " Specialist"),
                    vote=t.get("recommendation"),
                    confidence=t.get("confidence"),
                    analysis=t.get("analysis"),
                    color=t.get("color"),
                    data_verified=t.get("data_verified"),
                    mind_change_threshold=t.get("mind_change_threshold"),
                    status=t.get("status")
                )
                st.write("")
                
        with st.expander("🗣️ VIEW VENTURE BOARDROOM MEETING CHAT TRANSCRIPT"):
            for t in transcript:
                render_chat_bubble(
                    name=t.get("name"),
                    icon=t.get("icon"),
                    dialogue=t.get("dialogue"),
                    color=t.get("color")
                )

# Master Page Footer
render_footer()
