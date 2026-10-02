import os
import re
import json
import time
import random
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

CANDIDATE_MODELS = [
    GROQ_MODEL,
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "gemma2-9b-it",
    "qwen-2.5-32b"
]

# Helper to determine if we should run in simulated/mock mode
def check_is_mock():
    key = os.getenv("GROQ_API_KEY", "")
    return not key or key.strip() == "" or key.strip() == "gsk_your_key_here"

IS_MOCK = check_is_mock()

# Initialize Groq Client safely
client = None
if not IS_MOCK:
    try:
        client = Groq(api_key=GROQ_API_KEY, timeout=6.0)
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}. Switching to mock execution.")
        IS_MOCK = True

def format_budget_display(budget):
    """Formats numeric budget values into clear human-readable USD strings."""
    if isinstance(budget, (int, float)):
        if budget >= 1_000_000:
            return f"${budget / 1_000_000:.2f}M USD"
        elif budget >= 1_000:
            return f"${budget:,.0f} USD"
        elif budget > 0:
            return f"${budget:.2f}M USD"
    return str(budget)

def parse_budget_numeric(budget):
    """Normalizes any budget input into a clean USD float value."""
    try:
        if isinstance(budget, (int, float)):
            b = float(budget)
            if b < 1000 and b > 0:
                return b * 1_000_000.0
            return b
        elif isinstance(budget, str):
            cleaned = re.sub(r"[^\d.]", "", budget)
            val = float(cleaned) if cleaned else 50000.0
            b_lower = budget.lower()
            if "m" in b_lower or "million" in b_lower:
                return val * 1_000_000.0
            elif "k" in b_lower:
                return val * 1_000.0
            elif val < 1000 and val > 0:
                return val * 1_000_000.0
            return val
    except Exception:
        return 50000.0
    return 50000.0

def generate_mock_response(agent_role, company, market, budget, timeline, question, grounding_data=None):
    """
    Generates realistic, tailored answers grounded in datasets and venture characteristics.
    Evaluates real business constraints (capital adequacy, manufacturing, timeline, inventory, risk).
    """
    import sys
    if "unittest" not in sys.modules and not os.getenv("TESTING"):
        time.sleep(0.15)

    budget_usd = parse_budget_numeric(budget)
    budget_display = format_budget_display(budget_usd)
    
    text_corpus = f"{company} {question} {timeline}".lower()
    is_risky = any(x in text_corpus for x in ["risky", "crypto", "volatile", "dangerous", "unstable", "war"])
    is_drone_aviation = any(x in text_corpus for x in ["drone", "air taxi", "aircraft", "aviation", "evtol", "flight", "aerospace", "passenger air taxi", "passenger air", "last-mile delivery drone"])
    is_heavy_infrastructure = any(x in text_corpus for x in ["air taxi", "passenger", "nationwide network", "airline", "evtol", "telecom network", "rail", "power grid", "passenger air taxi"])
    is_hardware = any(x in text_corpus for x in ["hardware", "device", "smart home", "manufacturing", "inventory", "physical", "electronics", "iot sensor", "tooling", "assembly"]) or is_drone_aviation or is_heavy_infrastructure
    is_manufacturing = any(x in text_corpus for x in ["manufacturing", "factory", "tooling", "assembly", "mass production", "large-scale manufacturing"])
    is_upfront_inventory = any(x in text_corpus for x in ["inventory", "warehousing", "stock", "working capital", "upfront inventory"]) or is_drone_aviation
    is_intl_distribution = any(x in text_corpus for x in ["international distribution", "international", "freight", "customs", "cross-border", "distribution"])
    
    is_short_timeline = any(x in str(timeline).lower() for x in ["6 month", "6m", "3 month", "3m", "90 day", "180 day"]) or ("6" in str(timeline) and "month" in str(timeline).lower()) or ("3" in str(timeline) and "month" in str(timeline).lower())
    is_low_capital = budget_usd <= 150_000
    
    if is_heavy_infrastructure:
        is_critical_capital_deficit = budget_usd < 5_000_000
    elif is_drone_aviation:
        is_critical_capital_deficit = budget_usd < 300_000
    else:
        is_critical_capital_deficit = is_hardware and (is_low_capital or (is_manufacturing and budget_usd < 300_000))
        
    is_critical_hardware_mismatch = is_critical_capital_deficit
    
    has_grounding = bool(grounding_data and grounding_data.get("status") == "success")
    facts = grounding_data.get("data", {}) if has_grounding else {}
    idea_str = company or "the proposed venture"

    # 1. RESEARCHER Mock Response (Track A)
    if agent_role == "RESEARCHER":
        if has_grounding:
            startups = facts.get("Startups Tracked", "numerous")
            total_funding = facts.get("Total Funding (USD)", "substantial capital")
            avg_funding = facts.get("Average Funding per Startup (USD)", "healthy average")
            analysis = (
                f"Market research analysis for {market} indicates an active commercial environment with {startups} "
                f"tracked ecosystem enterprises and ${total_funding} in aggregate sector funding (benchmarking ~${avg_funding} per enterprise). "
                f"For {company}, this validates consumer digital/commercial readiness and expansion TAM within the {timeline} target window."
            )
            dialogue = f"Ecosystem demand data for {market} shows {startups} active enterprises, indicating favorable market adoption conditions for {company}."
            rec = "YES" if not is_risky else "MAYBE"
            confidence = 88
        else:
            tam_est = (budget_usd / 1_000_000.0) * 4.2 if budget_usd > 100_000 else 5.0
            rec = "YES" if not is_risky else "MAYBE"
            confidence = 78
            analysis = (
                f"Market opportunity analysis for {company} entering {market} reveals an estimated addressable sector "
                f"opportunity (TAM) of approximately ${tam_est:.1f}M USD with positive compound growth signals. "
                f"Target customer segments align with {company}'s strategic expansion objective."
            )
            dialogue = f"Target market demand in {market} is expanding steadily, offering viable scale for {company}."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "key_finding": f"Market research confirms positive demand dynamics for {company} in {market}.",
            "primary_concern": f"Customer acquisition cost and local distribution ramp-up in {market}.",
            "mind_change_threshold": f"Pre-orders or signed pilot customer letters of intent exceeding 15% of year-1 target in {market}."
        }
        
    # 2. COMPETITOR Mock Response (Track A)
    elif agent_role == "COMPETITOR":
        if has_grounding:
            leader = facts.get("Top Company", "the domestic conglomerate leader")
            sym = facts.get("Top Company Symbol", "")
            leader_mcap = facts.get("Top Company Market Cap (USD)", "undisclosed")
            comps_count = facts.get("Companies Tracked", "multiple")
            sym_str = f" ({sym})" if sym and sym != "N/A" else ""
            analysis = (
                f"Competitive intelligence tracks {comps_count} major corporate entities in the regional landscape (macro leader: {leader}{sym_str}, valued at {leader_mcap}). "
                f"In the specific {market} domain, {company} faces established regional incumbents, but maintains clear competitive differentiation and agility to capture market share."
            )
            dialogue = f"Regional corporate landscape is anchored by major players like {leader}, but {company} has strong strategic differentiation in {market}."
            rec = "YES" if not is_risky else "MAYBE"
            confidence = 85
        else:
            confidence = 76
            rec = "MAYBE" if (is_risky or budget_usd > 50_000_000) else "YES"
            analysis = (
                f"Competitive landscape in {market} features established domestic providers. "
                f"{company}'s value proposition provides a distinct wedge against entrenched incumbents."
            )
            dialogue = f"Incumbents in {market} hold entrenched positions, but leave distinct product gaps for {company}."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "key_finding": f"Competitive positioning for {company} in {market} is defensible.",
            "primary_concern": f"Incumbent pricing retaliation and local brand loyalty in {market}.",
            "mind_change_threshold": f"Validated proprietary technology or exclusive distribution partnerships in {market}."
        }
        
    # 3. LEGAL Mock Response (Track A)
    elif agent_role == "LEGAL":
        if has_grounding:
            ease_rank = facts.get("Ease of Doing Business Rank", "N/A")
            ease_score = facts.get("Ease of Doing Business Score", "N/A")
            contract_score = facts.get("Enforcing Contracts Score", "N/A")
            days_start = facts.get("Days to Start Business", "N/A")
            income = facts.get("IncomeGroup", "Standard")
            rank_str = f"rank #{int(float(ease_rank))}" if ease_rank != "N/A" and str(ease_rank).replace('.','',1).isdigit() else f"rank {ease_rank}"
            analysis = (
                f"World Bank regulatory indicators place the target jurisdiction at {rank_str} globally with an Ease of Doing Business score of "
                f"{ease_score}/100 and contract enforcement score of {contract_score}/100. Entity establishment averages {days_start} days ({income} bracket), "
                f"providing a reliable legal and commercial framework for {company}'s expansion."
            )
            dialogue = f"Regulatory environment scores {ease_score}/100 for Doing Business with contract enforcement at {contract_score}/100, providing legal predictability for {company}."
            rec = "YES" if (ease_score != "N/A" and float(ease_score) >= 55.0) else "MAYBE"
            confidence = 86
        else:
            confidence = 72
            rec = "NO" if is_risky else "MAYBE" if is_short_timeline else "YES"
            analysis = (
                f"Regulatory framework for {company} in {market} requires foreign corporate registration, localized licensing, and compliance filing. "
                f"Entity formation can proceed under standard commercial guidelines within the {timeline} roadmap."
            )
            dialogue = f"Compliance requirements in {market} are standard, but require formal legal counsel to execute filings within {timeline}."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "key_finding": f"Legal and compliance framework in {market} is navigable within {timeline}.",
            "primary_concern": f"Foreign entity licensing lead time and localized data compliance for {company}.",
            "mind_change_threshold": f"Securing corporate registration and standard commercial compliance filing clearance."
        }

    # 4. OPERATIONS Mock Response (Track A)
    elif agent_role == "OPERATIONS":
        if has_grounding:
            lpi_score = facts.get("Logistics Performance Score (2023)", "N/A")
            lpi_num = float(lpi_score) if lpi_score != "N/A" else 3.0
            analysis = (
                f"World Bank Logistics Performance Index evaluates the target market infrastructure at {lpi_num:.1f}/5.0. "
                f"Transport reliability, customs clearance, and digital connectivity are sufficient to support {company}'s operational deployment within {timeline}."
            )
            dialogue = f"Logistics infrastructure rating of {lpi_num:.1f}/5.0 confirms operational channels will support {company}'s rollout across {timeline}."
            rec = "YES" if lpi_num >= 2.8 else "MAYBE"
            confidence = 85
        else:
            confidence = 74
            rec = "MAYBE" if is_short_timeline else "YES"
            analysis = (
                f"Operational rollout for {company} into {market} requires establishing local distribution partnerships and staffing. "
                f"Given the {timeline} execution window, a staged operational rollout is recommended."
            )
            dialogue = f"Operational logistics in {market} can be executed across {timeline} with regional partner integration."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "key_finding": f"Operational logistics and supply chain are feasible for {company} across {timeline}.",
            "primary_concern": f"Local talent acquisition and channel partner onboarding timeline in {market}.",
            "mind_change_threshold": f"Formalized SLA with regional 3PL partners reducing fulfillment lead time."
        }

    # 5. RISK Mock Response (Track A)
    elif agent_role == "RISK":
        if has_grounding:
            fragility = facts.get("Fragility Score", facts.get("Total", "N/A"))
            frag_num = float(fragility) if fragility != "N/A" else 60.0
            risk_level = "Low" if frag_num < 50 else "Moderate" if frag_num < 80 else "Elevated"
            analysis = (
                f"Sovereign fragility index assesses the target territory at {frag_num:.1f}/120 ({risk_level} macro risk). "
                f"Macroeconomic stability, currency predictability, and institutional governance support {company}'s expansion capital allocation."
            )
            dialogue = f"Sovereign fragility is rated at {frag_num:.1f}/120 ({risk_level} risk), confirming manageable macro exposure for {company}."
            rec = "YES" if frag_num < 75 else "MAYBE" if frag_num < 95 else "NO"
            confidence = 87
        else:
            confidence = 70
            rec = "NO" if is_risky else "MAYBE"
            analysis = (
                f"Macroeconomic risk in {market} is within manageable parameters for {company}. "
                f"Tranche-based capital deployment is recommended to mitigate currency and market volatility."
            )
            dialogue = f"Macro risk for {company} in {market} is manageable via staged capital milestones."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "key_finding": f"Macro and sovereign risk envelope in {market} is acceptable for {company}.",
            "primary_concern": f"Foreign exchange volatility and downside market demand shifts in {market}.",
            "mind_change_threshold": f"Implementation of currency hedging and strict milestone-gated capital drawdowns."
        }

    # 6. CFO Mock Response (Track A)
    elif agent_role == "CFO":
        if is_critical_hardware_mismatch:
            analysis = (
                f"Proposed budget of {budget_display} is severely deficient for physical hardware manufacturing and inventory requirements in {market}. "
                f"Upfront tooling, prototyping, and working capital will rapidly deplete the allocation."
            )
            dialogue = f"Available expansion budget of {budget_display} cannot fund hardware manufacturing and commercial inventory requirements."
            rec = "NO"
            confidence = 92
        elif is_low_capital and (is_manufacturing or is_intl_distribution):
            analysis = (
                f"Capital allocation of {budget_display} provides limited runway for high-complexity operations in {market}. "
                f"Expansion requires milestone-gated funding tranches to protect balance sheet capital."
            )
            dialogue = f"Budget of {budget_display} requires disciplined capital gating across {timeline}."
            rec = "MAYBE"
            confidence = 85
        else:
            analysis = (
                f"Proposed expansion capital of {budget_display} is calibrated for {company}'s entry into {market}. "
                f"Projected unit economics and capital efficiency support milestone-based deployment across {timeline} with targeted payback within {timeline}."
            )
            dialogue = f"Capital allocation of {budget_display} adequately funds {company}'s expansion roadmap across {timeline}."
            rec = "YES"
            confidence = 88
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "key_finding": f"Capital sizing of {budget_display} evaluated across {timeline} roadmap.",
            "primary_concern": f"Working capital burn rate and payback period discipline across {timeline}.",
            "mind_change_threshold": f"Securing additional working capital buffer or formalizing milestone-based burn governance."
        }

    # 7. CEO Mock Response (Track A)
    elif agent_role == "CEO":
        if is_critical_hardware_mismatch:
            rec = "REJECT EXPANSION"
            analysis = f"Executive board synthesis determines that {budget_display} cannot support hardware manufacturing and launch for {company} in {market}."
            dialogue = f"The board rejects expansion for {company} due to severe capital and manufacturing constraints."
        elif is_risky:
            rec = "DELAY ENTRY"
            analysis = f"Consolidated board review advises delaying expansion into {market} until macro volatility and risk mitigations are established for {company}."
            dialogue = f"The board recommends delaying expansion into {market} pending risk de-escalation."
        else:
            rec = "ENTER MARKET"
            analysis = f"Consolidated board evaluation confirms strategic viability for {company} expanding into {market} with {budget_display} over {timeline}."
            dialogue = f"The executive board green-lights market expansion for {company} into {market}."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": 88,
            "dialogue": dialogue,
            "data_verified": has_grounding
        }

    # ==========================================
    # TRACK B: NEW BUSINESS LAUNCH MOCK RESPONSES
    # ==========================================

    # 8. MARKET VALIDATOR Mock Response
    elif agent_role == "MARKET_VALIDATOR":
        if has_grounding:
            startups = facts.get("Startups Tracked", "450+")
            total_funding = facts.get("Total Funding (USD)", "2.8B")
            avg_funding = facts.get("Average Funding per Startup (USD)", "6.2M")
            if is_critical_hardware_mismatch:
                analysis = (
                    f"Startup ecosystem data for {market} confirms {startups} active ventures with ${total_funding} "
                    f"in venture capital. While consumer tech adoption in {market} is receptive, launching an expensive hardware "
                    f"device direct-to-consumer requires extensive marketing and retail channel margin that {budget_display} cannot support."
                )
                dialogue = f"Market appetite in {market} exists, but consumer hardware adoption demands substantial channel and marketing capital."
                rec = "MAYBE"
                confidence = 85
                mct = "Documenting 5,000+ verified direct pre-orders with upfront deposits would provide sufficient demand proof."
            else:
                analysis = (
                    f"Startup ecosystem dataset for {market} documents {startups} active ventures with "
                    f"${total_funding} in cumulative funding (averaging ${avg_funding} per venture). "
                    f"This demonstrates active startup venture infrastructure and receptive market appetite for {idea_str}."
                )
                dialogue = f"Market data confirms {startups} active startups and ${total_funding} total venture capital in {market}, proving initial ecosystem liquidity."
                rec = "YES"
                confidence = 88
                mct = "A 40% decline in early-stage investment deals or lack of local customer demand in pilot testing would change my vote."
        else:
            confidence = 70
            rec = "MAYBE"
            analysis = (
                f"No verified startup ecosystem dataset was found for {market}. Reasoning from regional benchmarks, "
                f"{idea_str} targets an addressable sector, but verified startup capital velocity remains unconfirmed."
            )
            dialogue = f"Verified startup ecosystem metrics for {market} are limited; demand validation requires field customer surveys."
            mct = f"Verified primary customer commitments (100+ letter of intent signups) in {market} would elevate my recommendation to YES."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "mind_change_threshold": mct,
            "key_finding": analysis[:140] + "..." if len(analysis) > 140 else analysis,
            "strongest_evidence": f"Startup ecosystem metrics for {market}" if has_grounding else "General macroeconomic demand patterns",
            "primary_concern": "Customer acquisition cost and brand trust barriers for consumer hardware." if is_hardware else "Early-stage customer willingness-to-pay."
        }

    # 9. COMPETITIVE SCOUT Mock Response
    elif agent_role == "COMPETITIVE_SCOUT":
        if has_grounding:
            leader = facts.get("Top Company", "the domestic incumbent")
            leader_mcap = facts.get("Top Company Market Cap (USD)", "undisclosed")
            comps_count = facts.get("Companies Tracked", "multiple")
            top_comps = facts.get("Top Competitors", leader)
            if is_hardware:
                analysis = (
                    f"Competitive landscape in {market} is heavily contested by entrenched global smart home ecosystems "
                    f"(Google Nest, Amazon Ring, Apple HomeKit) and domestic suppliers. Competing in consumer hardware without "
                    f"retail shelf presence or significant marketing budget creates severe distribution headwinds."
                )
                dialogue = "Global smart home incumbents dominate consumer mindshare; entering with limited budget creates distribution friction."
                rec = "MAYBE"
                confidence = 85
                mct = "Demonstrating a defensible, patented hardware feature that incumbents cannot replicate within 18 months."
            else:
                analysis = (
                    f"Competitive landscape in {market} tracks {comps_count} key corporate players, led by {leader} "
                    f"({leader_mcap}). While major incumbents ({top_comps}) dominate core enterprise share, {idea_str} "
                    f"can target underserved digital-first niches without triggering immediate retaliation."
                )
                dialogue = f"Incumbents in {market} are led by {leader} ({leader_mcap}), but clear feature and agility voids allow a new entrant to carve out a foothold."
                rec = "YES"
                confidence = 85
                mct = f"If {leader} releases a native direct feature equivalent before launch, I would downgrade to NO."
        else:
            confidence = 72
            rec = "MAYBE"
            analysis = (
                f"No verified public competitor dataset found for {market}. General sector analysis indicates "
                f"established incumbents exist, but specific concentration ratios remain unverified."
            )
            dialogue = "Competitor concentration data is unverified on disk; localized competitor teardowns are required."
            mct = "Documenting 3 or more well-funded direct clones in this market would change my vote to NO."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "mind_change_threshold": mct,
            "key_finding": analysis[:140] + "..." if len(analysis) > 140 else analysis,
            "strongest_evidence": f"Incumbent concentration data for {market}" if has_grounding else "Competitor sector benchmarks",
            "primary_concern": "Dominance of entrenched smart home ecosystems with bundled pricing." if is_hardware else "Incumbent feature replication."
        }

    # 10. REGULATORY NAVIGATOR Mock Response
    elif agent_role == "REGULATORY_NAVIGATOR":
        if has_grounding:
            ease_rank = facts.get("Ease of Doing Business Rank", "N/A")
            start_rank = facts.get("Starting a Business Rank", "N/A")
            start_score = facts.get("Starting a Business Score", "N/A")
            days_start = facts.get("Days to Start Business", "N/A")
            enforce_score = facts.get("Enforcing Contracts Score", "N/A")
            if is_hardware:
                analysis = (
                    f"Commercial incorporation in {market} scores {start_score}/100 (rank #{start_rank}). However, consumer hardware "
                    f"with wireless/AI capabilities requires mandatory Regulatory Compliance Mark (RCM / ACMA) compliance, electrical safety testing, "
                    f"and statutory consumer guarantees under Australian Consumer Law (ACL), creating rigorous certification prerequisites."
                )
                dialogue = f"General business registration in {market} is efficient (~{days_start} days), but hardware requires mandatory RCM/ACMA testing and ACL statutory warranty provisions."
                rec = "MAYBE" if is_short_timeline else "YES"
                confidence = 86
                mct = "Receipt of certified RCM / EMC lab test clearance and ACL-compliant warranty policies."
            else:
                analysis = (
                    f"World Bank regulatory metrics for {market} indicate a Starting a Business Score of {start_score}/100 "
                    f"(Rank #{start_rank}) with an average commercial registration timeline of {days_start} days. "
                    f"Contract enforcement scores {enforce_score}/100 (Overall Ease of Doing Business #{ease_rank}), "
                    f"indicating structured incorporation pathways for a first-time founder."
                )
                dialogue = f"Incorporation indicators show a Starting a Business score of {start_score}/100 requiring ~{days_start} days for commercial registration."
                rec = "YES" if (start_score != "N/A" and float(start_score) >= 75.0) else "MAYBE"
                confidence = 86
                mct = "Discovery of foreign equity ownership caps or mandatory local partner equity above 50% would change my vote to NO."
        else:
            confidence = 70
            rec = "MAYBE"
            analysis = (
                f"Verified commercial registration and ease-of-business metrics are unlisted for {market}. "
                f"A first-time founder must conduct formal incorporation due diligence before deploying funds."
            )
            dialogue = "Official World Bank incorporation rankings are unverified for this market; formal legal clearance is advised."
            mct = "Obtaining a clean legal memorandum from local counsel confirming straightforward entity registration would shift my recommendation to YES."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "mind_change_threshold": mct,
            "key_finding": analysis[:140] + "..." if len(analysis) > 140 else analysis,
            "strongest_evidence": f"World Bank regulatory index for {market}" if has_grounding else "General commercial regulations",
            "primary_concern": "Hardware electrical safety, wireless RCM compliance, and Australian Consumer Law warranty liabilities." if is_hardware else "Regulatory filing lead times."
        }

    # 11. LAUNCH OPERATIONS Mock Response
    elif agent_role == "LAUNCH_OPERATIONS":
        if has_grounding:
            lpi_score = facts.get("Logistics Performance Score (2023)", "N/A")
            lpi_num = float(lpi_score) if lpi_score != "N/A" else 3.0
            if is_manufacturing or is_critical_hardware_mismatch or (is_hardware and is_short_timeline):
                analysis = (
                    f"World Bank Logistics Performance Index evaluates {market} at {lpi_num:.1f}/5.0. However, executing large-scale "
                    f"hardware manufacturing, tooling fabrication, production QA, international freight shipping, customs clearance, and local DTC "
                    f"fulfillment within a {timeline} window is operationally unviable under the proposed {budget_display} resource envelope."
                )
                dialogue = f"Hardware tooling, production runs, and international distribution cannot be executed within a {timeline} timeline on {budget_display}."
                rec = "NO"
                confidence = 89
                mct = "Securing verified contract manufacturing agreements with guaranteed 90-day turnaround and domestic consignment warehousing."
            else:
                analysis = (
                    f"World Bank Logistics Performance Index evaluates {market} at {lpi_num:.1f}/5.0. "
                    f"Transport reliability and digital infrastructure are sufficient to support a lean MVP rollout "
                    f"within the projected {timeline} timeline without heavy fixed-asset operational overhead."
                )
                dialogue = f"Logistics Performance Score is {lpi_num:.1f}/5.0; operational channels are viable for lean MVP execution."
                rec = "YES" if lpi_num >= 2.8 else "MAYBE"
                confidence = 86
                mct = "Customs delays exceeding 30 days for essential equipment or lack of reliable local payment rails would change my vote to NO."
        else:
            confidence = 70
            rec = "NO" if (is_manufacturing and is_short_timeline) else "MAYBE"
            analysis = (
                f"Logistics Performance Index data is unverified for {market}. Operational execution for a new venture "
                f"should utilize cloud-native infrastructure and regional 3PL partners to minimize initial operational friction."
            )
            dialogue = "Logistics benchmark data is unverified; initial operations should remain asset-light."
            mct = "Securing a binding SLA with a regional fulfillment/cloud partner would change my recommendation to YES."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "mind_change_threshold": mct,
            "key_finding": analysis[:140] + "..." if len(analysis) > 140 else analysis,
            "strongest_evidence": f"World Bank Logistics Performance Index ({lpi_num:.1f}/5.0)" if has_grounding else "Logistics benchmarks",
            "primary_concern": "Hardware tooling lead times, international freight bottlenecks, and reverse logistics costs." if is_hardware else "3PL fulfillment latency."
        }

    # 12. VENTURE RISK Mock Response
    elif agent_role == "VENTURE_RISK":
        if has_grounding:
            fragility = facts.get("Fragility Score", facts.get("Total", "N/A"))
            rank = facts.get("Rank", "N/A")
            frag_num = float(fragility) if fragility != "N/A" else 60.0
            if is_critical_hardware_mismatch or (is_hardware and is_upfront_inventory):
                analysis = (
                    f"Country sovereign risk in {market} is low (Fragility Score {frag_num:.1f}/120, rank #{rank}). However, the venture "
                    f"carries severe microeconomic risk: near 100% capital concentration in upfront inventory and tooling, single-point supply chain "
                    f"vulnerability, yield risk during initial manufacturing runs, and zero cash buffer to absorb transit or return delays."
                )
                dialogue = f"Sovereign risk in {market} is stable, but capital concentration in upfront hardware inventory creates fatal insolvency risk."
                rec = "NO"
                confidence = 90
                mct = "Structuring a pure on-demand or pre-funded manufacturing model with guaranteed minimum 12 months operating reserves."
            else:
                analysis = (
                    f"Fragile States Index rates {market} at rank {rank} with an overall fragility score of {frag_num:.1f} "
                    f"(Low venture risk). Sovereign risk parameters are well within manageable boundaries for an independent venture."
                )
                dialogue = f"Country fragility is rated at {frag_num:.1f}/120 (low sovereign risk)."
                rec = "YES" if frag_num < 75 else "MAYBE" if frag_num < 95 else "NO"
                confidence = 88
                mct = "Imposition of strict capital outflow controls or sudden currency devaluation exceeding 25% would shift my recommendation to NO."
        else:
            confidence = 72
            rec = "NO" if is_critical_hardware_mismatch else "MAYBE"
            analysis = (
                f"Verified sovereign risk indices are unavailable for {market}. For a first-time founder without local networks, "
                f"macroeconomic volatility must be managed through milestone-based capital deployment."
            )
            dialogue = "Sovereign fragility data is unverified; milestone-based capital tranches are strictly recommended."
            mct = "Verification of stable banking channels and currency convertibility by a Tier-1 financial partner would shift my vote to YES."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "mind_change_threshold": mct,
            "key_finding": analysis[:140] + "..." if len(analysis) > 140 else analysis,
            "strongest_evidence": f"Fragile States Index ({frag_num:.1f}/120) for {market}" if has_grounding else "Macroeconomic risk profile",
            "primary_concern": "Capital concentration in physical inventory and single-batch manufacturing failure risk." if is_hardware else "Market downside volatility."
        }

    # 13. CAPITAL STRATEGIST Mock Response
    elif agent_role == "CAPITAL_STRATEGIST":
        if has_grounding:
            avg_funding = facts.get("Average Funding per Startup (USD)", "N/A")
            tot_funding = facts.get("Total Funding (USD)", "N/A")
            if is_critical_hardware_mismatch:
                analysis = (
                    f"Venture ecosystem benchmarks in {market} average ${avg_funding} per startup. The proposed launch budget of "
                    f"{budget_display} is severely deficient for a consumer hardware startup requiring tooling, components, international shipping, "
                    f"and upfront inventory. Hardware ventures typically require a minimum of $500k-$1M USD to reach commercial delivery."
                )
                dialogue = f"The proposed budget of {budget_display} is critically undercapitalized for hardware development and manufacturing (benchmark average ${avg_funding})."
                rec = "NO"
                confidence = 92
                mct = "Securing minimum committed hardware seed funding of $500,000 USD or conversion to an asset-light white-label model."
            else:
                analysis = (
                    f"The average startup in {market} raises approximately ${avg_funding}, while your proposed launch budget is "
                    f"{budget_display}. Comparing this allocation against ecosystem norms indicates the proposed capital "
                    f"is well-aligned with venture benchmarks to achieve product-market fit across the {timeline} roadmap."
                )
                dialogue = f"The average startup in {market} raises approximately ${avg_funding}, while your proposed budget is {budget_display}. This capital allocation is well-calibrated against local benchmarks."
                rec = "YES"
                confidence = 90
                mct = "A monthly burn rate exceeding projected runway by more than 35% before reaching key MVP milestones would downgrade my recommendation to NO."
        else:
            confidence = 75
            if is_critical_hardware_mismatch:
                rec = "NO"
                analysis = f"A {budget_display} budget cannot support hardware manufacturing and upfront inventory investment."
                dialogue = f"Capital allocation of {budget_display} is severely inadequate for hardware development."
                mct = "Raising at least $500k USD seed capital to fund tooling and inventory."
            else:
                rec = "MAYBE"
                analysis = (
                    f"Verified startup funding benchmarks are unavailable for {market}. Your proposed launch budget of {budget_display} "
                    f"cannot be directly calibrated against empirical ecosystem averages, requiring tight burn-rate controls."
                )
                dialogue = f"Empirical startup funding averages for {market} are unavailable; proposed budget of {budget_display} should be preserved with lean milestone discipline."
                mct = "Constructing a bottom-up unit-economic model demonstrating 18+ months of operational runway would shift my vote to YES."
            
        return {
            "analysis": analysis,
            "recommendation": rec,
            "confidence": confidence,
            "dialogue": dialogue,
            "data_verified": has_grounding,
            "mind_change_threshold": mct,
            "key_finding": analysis[:140] + "..." if len(analysis) > 140 else analysis,
            "strongest_evidence": f"Average startup benchmark (${avg_funding}) in {market}" if has_grounding else "Venture capital guidelines",
            "primary_concern": "Premature cash depletion before reaching first commercial production batch." if is_hardware else "Burn rate runway risk."
        }

    # 14. FOUNDER CEO Mock Response
    elif agent_role == "FOUNDER_CEO":
        if is_critical_hardware_mismatch:
            dec = "DO NOT LAUNCH"
            confidence = 92
            rationale = (
                f"Consolidated board evaluation determines that launching an expensive AI-enabled hardware startup in {market} "
                f"with only {budget_display} and a {timeline} timeline is fundamentally unfeasible. Mandatory capital feasibility, "
                f"manufacturing lead times, upfront inventory financing, and operational logistics constraints cannot be satisfied. "
                f"Immediate launch is rejected to prevent catastrophic early capital loss."
            )
            dialogue = (
                f"The board issues a definitive DO NOT LAUNCH recommendation. An allocation of {budget_display} cannot support "
                f"hardware tooling, compliance certification, and upfront inventory. We must secure adequate capital before proceeding."
            )
            roadmap = [
                "1. Redesign venture as software/AI platform or white-label partnership to eliminate upfront hardware tooling.",
                "2. Secure at least $500,000 - $1,000,000 USD in institutional hardware seed capital before tooling commitment.",
                "3. Secure binding supplier and 3PL distribution agreements with guaranteed payment terms.",
                "4. Conduct comprehensive Australian RCM electrical compliance and consumer law warranty audit."
            ]
        elif is_risky:
            dec = "DO NOT LAUNCH"
            confidence = 86
            rationale = f"Given elevated country risk and unverified market signals in {market}, launching at this time carries disproportionate downside."
            dialogue = "The board recommends halting launch. The sovereign and regulatory hurdles present excessive friction for an early-stage venture."
            roadmap = [
                f"Conduct 30 in-depth customer discovery interviews to validate problem urgency before committing capital.",
                f"Consult local legal counsel in {market} to audit regulatory licensing requirements.",
                f"Stress-test cash reserves against extreme currency volatility scenarios."
            ]
        elif is_short_timeline and budget_usd > 250_000:
            dec = "VALIDATE FIRST"
            confidence = 84
            rationale = f"While market momentum in {market} is attractive, deploying {budget_display} on a compressed {timeline} timeline warrants de-risking key operational assumptions."
            dialogue = "We have high conviction in the thesis, but must validate critical assumptions before committing significant capital."
            roadmap = [
                f"Build and test an asset-light MVP with a controlled cohort of 50 target users in {market}.",
                f"Run targeted customer acquisition ad campaigns to benchmark customer acquisition cost (CAC).",
                f"Establish relationships with local incorporation and compliance partners.",
                f"Calibrate runway milestones to ensure at least 18 months of operating buffer."
            ]
        else:
            dec = "LAUNCH"
            confidence = 88
            rationale = f"Consolidated venture board audit confirms supportive ecosystem liquidity, manageable regulatory friction, and calibrated capital sizing. Green-light for venture launch."
            dialogue = f"The board has reviewed the thesis and datasets. We are green-lighting the venture launch in {market}."
            roadmap = [
                f"Initiate commercial business incorporation and legal entity registration in {market}.",
                f"Deploy Phase-1 lean MVP focused on core high-value user workflows.",
                f"Execute focused early adopter acquisition targeting unserved competitor voids.",
                f"Establish initial local banking, payment rails, and currency hedging."
            ]
            
        return {
            "analysis": rationale,
            "recommendation": dec,
            "confidence": confidence,
            "dialogue": dialogue,
            "validation_roadmap": roadmap,
            "data_verified": has_grounding
        }

def call_groq_api(prompt, system_prompt=None, response_format=None, agent_role="RESEARCHER", company="", market="", budget=100, timeline="1 Year", question="", grounding_data=None):
    """
    Safely dispatches a prompt to the Groq API with automatic model fallback.
    If the API fails, is missing, or is in mock mode, it switches seamlessly to domain-grounded simulation.
    Supports both Track A (Expansion) and Track B (New Business Launch) agent roles with 100% backward compatibility.
    """
    global IS_MOCK, client
    
    if IS_MOCK or client is None:
        return generate_mock_response(agent_role, company, market, budget, timeline, question, grounding_data=grounding_data)
        
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Try candidate models in order if configured model encounters deprecation or error
    tested_models = []
    for model_name in CANDIDATE_MODELS:
        if model_name in tested_models:
            continue
        tested_models.append(model_name)
        
        try:
            kwargs = {
                "messages": messages,
                "model": model_name,
                "temperature": 0.2,
                "timeout": 5.0
            }
            if response_format and response_format.get("type") == "json_object":
                kwargs["response_format"] = response_format
                
            completion = client.chat.completions.create(**kwargs)
            result_text = completion.choices[0].message.content
            
            # Clean and parse JSON response
            try:
                if "```json" in result_text:
                    json_content = re.search(r"```json\s*(.*?)\s*```", result_text, re.DOTALL).group(1)
                elif "```" in result_text:
                    json_content = re.search(r"```\s*(.*?)\s*```", result_text, re.DOTALL).group(1)
                else:
                    json_content = result_text.strip()
                    
                parsed = json.loads(json_content)
                
                # Standardize recommendations and keys based on agent role
                rec = str(parsed.get("recommendation", "MAYBE")).upper()
                
                if agent_role == "FOUNDER_CEO":
                    if rec in ["LAUNCH", "ENTER", "ENTER MARKET", "YES"]:
                        rec_val = "LAUNCH"
                    elif rec in ["DO NOT LAUNCH", "REJECT", "REJECT EXPANSION", "NO"]:
                        rec_val = "DO NOT LAUNCH"
                    else:
                        rec_val = "VALIDATE FIRST"
                elif agent_role == "CEO":
                    if rec in ["YES", "ENTER", "ENTER MARKET"]:
                        rec_val = "ENTER MARKET"
                    elif rec in ["NO", "REJECT", "REJECT EXPANSION"]:
                        rec_val = "REJECT EXPANSION"
                    else:
                        rec_val = "DELAY ENTRY"
                else:
                    if rec in ["YES", "ENTER", "ENTER MARKET", "LAUNCH"]:
                        rec_val = "YES"
                    elif rec in ["NO", "REJECT", "REJECT EXPANSION", "DO NOT LAUNCH"]:
                        rec_val = "NO"
                    else:
                        rec_val = "MAYBE"
                    
                result_dict = {
                    "analysis": parsed.get("analysis", result_text),
                    "recommendation": rec_val,
                    "confidence": int(parsed.get("confidence", 75)),
                    "dialogue": parsed.get("dialogue", parsed.get("analysis", result_text)[:150] + "...")
                }
                
                # Forward optional structured fields if present in schema
                if "data_verified" in parsed:
                    result_dict["data_verified"] = bool(parsed["data_verified"])
                elif grounding_data is not None:
                    result_dict["data_verified"] = bool(grounding_data.get("status") == "success")
                    
                if "mind_change_threshold" in parsed:
                    result_dict["mind_change_threshold"] = str(parsed["mind_change_threshold"])
                    
                if "key_finding" in parsed:
                    result_dict["key_finding"] = str(parsed["key_finding"])
                    
                if "strongest_evidence" in parsed:
                    result_dict["strongest_evidence"] = str(parsed["strongest_evidence"])
                    
                if "primary_concern" in parsed:
                    result_dict["primary_concern"] = str(parsed["primary_concern"])
                    
                if "validation_roadmap" in parsed and isinstance(parsed["validation_roadmap"], list):
                    result_dict["validation_roadmap"] = parsed["validation_roadmap"]
                    
                return result_dict
                
            except Exception as parse_err:
                print(f"Error parsing Groq response as JSON: {parse_err}. Falling back to domain model.")
                return generate_mock_response(agent_role, company, market, budget, timeline, question, grounding_data=grounding_data)
                
        except Exception as e:
            err_msg = str(e)
            print(f"Groq model {model_name} failed: {err_msg[:80]}... Trying next model.")
            continue

    # If all models fail, gracefully fallback to domain grounded evaluation
    return generate_mock_response(agent_role, company, market, budget, timeline, question, grounding_data=grounding_data)