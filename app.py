"""Streamlit UI for the Market Research Agent."""

import asyncio
import os

import streamlit as st

from src.models import ResearchBrief
from src.orchestrator import ResearchOrchestrator
from src.export import (
    export_to_pdf,
    export_to_docx,
    create_asset_bundle,
    get_filename_from_title,
)

# Page config
st.set_page_config(
    page_title="Market Research Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

@st.cache_resource
def _load_css() -> str:
    """Load CSS from external file, cached across reruns."""
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    with open(css_path) as f:
        return f.read()


# Apply styles from external CSS file
st.markdown(
    f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{_load_css()}</style>
""",
    unsafe_allow_html=True,
)


def render_hero():
    """Render the hero section."""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
        <h1 class="hero-title">
            The Most Advanced<br>
            <span class="teal-accent">Market Research</span> Technology
        </h1>
        <p class="hero-subtitle">
            Professional-grade market research powered by 8 specialized AI agents.
            Get $25K-quality insights in minutes, not weeks.
        </p>
        """,
            unsafe_allow_html=True,
        )

        # Feature badges
        st.markdown(
            """
        <div style="margin-bottom: 2rem;">
            <span class="feature-badge">📊 8 AI Agents</span>
            <span class="feature-badge">🔍 Source Verified</span>
            <span class="feature-badge">📈 Deep Analysis</span>
            <span class="feature-badge">⚡ Fast Results</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        # Stats
        st.markdown(
            """
        <div style="background: linear-gradient(135deg, #007A75 0%, #00a896 100%);
                    border-radius: 20px; padding: 1.75rem; color: white; text-align: center;
                    box-shadow: 0 8px 30px rgba(0, 122, 117, 0.35), inset 0 1px 0 rgba(255,255,255,0.2);
                    position: relative; overflow: hidden;"
             role="region" aria-label="Statistics">
            <div style="position: absolute; top: -50%; right: -50%; width: 100%; height: 100%;
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);"></div>
            <div style="font-size: 2.75rem; font-weight: 700; font-family: 'Inter', sans-serif;
                        text-shadow: 0 2px 4px rgba(0,0,0,0.1);">8+</div>
            <div style="font-size: 0.875rem; color: #ffffff; font-weight: 500;
                        letter-spacing: 0.02em;">Specialized Agents</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
        <div style="background: linear-gradient(145deg, #ffffff 0%, #f0fdf9 100%);
                    border-radius: 20px; padding: 1.75rem; text-align: center;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.06), 0 8px 40px rgba(0, 122, 117, 0.08);
                    border: 1px solid rgba(0, 122, 117, 0.1);">
            <div style="font-size: 2.75rem; font-weight: 700; font-family: 'Inter', sans-serif;
                        background: linear-gradient(135deg, #007A75 0%, #00a896 100%);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">5</div>
            <div style="font-size: 0.875rem; color: #4a5568; font-weight: 500;
                        letter-spacing: 0.02em;">Research Waves</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def create_intake_form():
    """Create the 15-question intake form with modern card design."""

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown(
        """
    <h2 style="font-size: 2rem; font-weight: 600; color: #1a1a2e; margin-bottom: 0.5rem;">
        Research Intake
    </h2>
    <p style="color: #4a5568; margin-bottom: 2rem;">
        Tell us about your project. The more detail you provide, the better your research will be.
    </p>
    """,
        unsafe_allow_html=True,
    )

    # Phase 1: The Offering
    st.markdown(
        """
    <div class="intake-card">
        <div class="card-header">
            <div class="card-icon">💡</div>
            <div>
                <p class="card-title">Phase 1: The Offering</p>
                <p class="card-subtitle">What are you building?</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    offering_what = st.text_input(
        "What is it?",
        placeholder="e.g., productivity app, online course, SaaS platform...",
        help="Product, service, course, marketplace, etc.",
    )

    offering_problem = st.text_area(
        "What problem does it solve?",
        placeholder="In one sentence, what pain point does this address?",
        height=80,
    )

    col1, col2 = st.columns(2)
    with col1:
        offering_delivery = st.selectbox(
            "How would it be delivered?",
            options=[
                "",
                "Online/SaaS",
                "Mobile app",
                "In-person",
                "Physical product",
                "Course/Workshop",
                "Consulting/Service",
                "Marketplace",
                "Other",
            ],
        )

    with col2:
        offering_pricing = st.selectbox(
            "Pricing model in mind?",
            options=[
                "",
                "One-time purchase",
                "Subscription",
                "Tiered/Freemium",
                "Usage-based",
                "Not sure yet",
            ],
        )

    # Phase 2: Customer Hypothesis
    st.markdown(
        """
    <div class="intake-card" style="margin-top: 2rem;">
        <div class="card-header">
            <div class="card-icon">👥</div>
            <div>
                <p class="card-title">Phase 2: Customer Hypothesis</p>
                <p class="card-subtitle">Who is your target audience?</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    target_customer = st.text_area(
        "Who do you imagine buying this?",
        placeholder="Be specific - not just demographics, but their situation",
        height=100,
    )

    customer_conversations = st.text_area(
        "Have you talked to any potential customers yet?",
        placeholder="If yes, what did you learn? What surprised you? If no, that's fine.",
        height=80,
    )

    segments_include_exclude = st.text_input(
        "Any segments to specifically INCLUDE or EXCLUDE?",
        placeholder="e.g., 'Focus on solopreneurs, exclude agencies'",
    )

    # Phase 3: Market Context
    st.markdown(
        """
    <div class="intake-card" style="margin-top: 2rem;">
        <div class="card-header">
            <div class="card-icon">🌍</div>
            <div>
                <p class="card-title">Phase 3: Market Context</p>
                <p class="card-subtitle">Where and who are you competing with?</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        geography = st.text_input(
            "What geographies or markets?",
            placeholder="e.g., United States, UK, Global English-speaking...",
        )

    with col2:
        known_competitors = st.text_input(
            "Competitors you're aware of?",
            placeholder="Comma-separated, e.g., Notion, Asana, Monday.com",
        )

    opportunity_thesis = st.text_area(
        "Why do you believe there's an opportunity here?",
        placeholder="What's your thesis?",
        height=80,
    )

    # Phase 4: Business Reality
    st.markdown(
        """
    <div class="intake-card" style="margin-top: 2rem;">
        <div class="card-header">
            <div class="card-icon">🎯</div>
            <div>
                <p class="card-title">Phase 4: Business Reality</p>
                <p class="card-subtitle">Where are you in your journey?</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        stage = st.selectbox(
            "What stage are you at?",
            options=[
                "",
                "Exploring an idea",
                "Committed to building, figuring out details",
                "Already have something, looking to expand/pivot",
                "Existing business entering new market",
            ],
        )

    with col2:
        resources = st.text_input(
            "Roughly, what resources do you have to execute?",
            placeholder="e.g., 'bootstrapped solo founder', 'funded team of 10'",
        )

    # Phase 5: Research Priorities
    st.markdown(
        """
    <div class="intake-card" style="margin-top: 2rem;">
        <div class="card-header">
            <div class="card-icon">🔬</div>
            <div>
                <p class="card-title">Phase 5: Research Priorities</p>
                <p class="card-subtitle">What do you most need to learn?</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    primary_question = st.text_area(
        "What's the #1 question you need answered?",
        placeholder="If this research only answered one thing well, what should it be?",
        height=80,
    )

    kill_criteria = st.text_area(
        "What would make you decide NOT to proceed?",
        placeholder="What are the kill criteria?",
        height=80,
    )

    already_known = st.text_area(
        "What do you already know that I shouldn't waste time on?",
        placeholder="Any previous research, conversations, or insights?",
        height=80,
    )

    # Depth selection
    st.markdown(
        """
    <div class="intake-card" style="margin-top: 2rem;">
        <div class="card-header">
            <div class="card-icon">⚙️</div>
            <div>
                <p class="card-title">Research Depth</p>
                <p class="card-subtitle">How comprehensive should the analysis be?</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    depth = st.radio(
        "Select research depth:",
        options=[
            ("overview", "🚀 Quick Overview — Key insights and market snapshot"),
            ("thorough", "📊 Thorough Analysis — Comprehensive findings with strategic recommendations"),
            ("deep_dive", "🔬 Deep Dive — Exhaustive research leaving no stone unturned"),
        ],
        format_func=lambda x: x[1],
        index=1,
        label_visibility="collapsed",
    )

    return {
        "offering_what": offering_what,
        "offering_problem": offering_problem,
        "offering_delivery": offering_delivery if offering_delivery else None,
        "offering_pricing_model": offering_pricing if offering_pricing else None,
        "target_customer": target_customer,
        "customer_conversations": customer_conversations if customer_conversations else None,
        "segments_include_exclude": segments_include_exclude if segments_include_exclude else None,
        "geography": geography,
        "known_competitors": [c.strip() for c in known_competitors.split(",") if c.strip()],
        "opportunity_thesis": opportunity_thesis if opportunity_thesis else None,
        "stage": stage if stage else None,
        "resources": resources if resources else None,
        "primary_question": primary_question,
        "kill_criteria": kill_criteria if kill_criteria else None,
        "already_known": already_known if already_known else None,
        "depth": depth[0] if isinstance(depth, tuple) else depth,
    }


def validate_intake(data: dict) -> list[str]:
    """Validate required fields are filled."""
    errors = []
    if not data["offering_what"]:
        errors.append("Please describe what you're building (Question 1)")
    if not data["offering_problem"]:
        errors.append("Please describe the problem it solves (Question 2)")
    if not data["target_customer"]:
        errors.append("Please describe your target customer (Question 5)")
    if not data["geography"]:
        errors.append("Please specify your target geography (Question 8)")
    if not data["primary_question"]:
        errors.append("Please specify your #1 question (Question 13)")
    return errors


def display_progress(wave_index: int, wave_name: str, status: str):
    """Display progress for a wave with modern styling."""
    status_config = {
        "pending": ("⏳", ""),
        "running": ("🔄", "running"),
        "complete": ("✅", "complete"),
        "error": ("❌", "error"),
    }
    icon, css_class = status_config.get(status, ("⏳", ""))

    st.markdown(
        f"""
    <div class="wave-item {css_class}">
        <div class="wave-icon">{icon}</div>
        <div>
            <div style="font-weight: 500; color: #1a1a2e;">{wave_name}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


async def run_research(brief: ResearchBrief) -> dict:
    """Run the research with progress display. Returns results dict."""
    orchestrator = ResearchOrchestrator()

    progress_placeholder = st.empty()
    wave_statuses = ["pending"] * 5

    for wave_idx in range(5):
        wave_statuses[wave_idx] = "running"

        with progress_placeholder.container():
            st.markdown(
                """
            <div class="intake-card">
                <div class="card-header">
                    <div class="card-icon">📊</div>
                    <div>
                        <p class="card-title">Research Progress</p>
                        <p class="card-subtitle">AI agents are analyzing your market</p>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            for idx, status in enumerate(wave_statuses):
                display_progress(idx, orchestrator.get_wave_description(idx), status)

        try:
            await orchestrator.run_wave(wave_idx, brief)
            wave_statuses[wave_idx] = "complete"
        except Exception as e:
            wave_statuses[wave_idx] = "error"
            st.error(f"Error in {orchestrator.get_wave_description(wave_idx)}: {e}")

    return orchestrator.results


def _build_brief(data: dict) -> ResearchBrief:
    """Build a ResearchBrief from intake form data."""
    return ResearchBrief(
        offering_what=data["offering_what"],
        offering_problem=data["offering_problem"],
        target_customer=data["target_customer"],
        geography=data["geography"],
        primary_question=data["primary_question"],
        offering_delivery=data["offering_delivery"],
        offering_pricing_model=data["offering_pricing_model"],
        customer_conversations=data["customer_conversations"],
        segments_include_exclude=data["segments_include_exclude"],
        known_competitors=data["known_competitors"],
        opportunity_thesis=data["opportunity_thesis"],
        stage=data["stage"],
        resources=data["resources"],
        kill_criteria=data["kill_criteria"],
        already_known=data["already_known"],
        depth=data["depth"],
    )


def display_confirmation(brief: ResearchBrief):
    """Show confirmation step before starting research."""
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    st.markdown(
        """
    <div class="intake-card">
        <div class="card-header">
            <div class="card-icon">📋</div>
            <div>
                <p class="card-title">Review Your Research Brief</p>
                <p class="card-subtitle">Please confirm before starting research</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(brief.to_markdown())

    # Estimated time based on depth
    time_estimates = {
        "overview": "2-3 minutes",
        "thorough": "4-6 minutes",
        "deep_dive": "8-12 minutes",
    }
    est_time = time_estimates.get(brief.depth, "4-6 minutes")

    st.info(f"Estimated time: **{est_time}** | Depth: **{brief.depth.replace('_', ' ').title()}**")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Confirm & Start Research", type="primary", use_container_width=True):
            st.session_state.view = "running"
            st.rerun()

    with col2:
        if st.button("Edit Brief", use_container_width=True):
            st.session_state.view = "intake"
            st.rerun()

    with col3:
        if st.button("Cancel", use_container_width=True):
            st.session_state.view = "intake"
            st.session_state.intake_data = None
            st.rerun()


def display_results():
    """Display research results and export options from session state."""
    results = st.session_state.results
    brief = st.session_state.brief

    st.markdown(
        """
    <div class="results-header" role="banner">
        <h2 style="margin: 0; font-size: 1.5rem; color: #ffffff;">Research Complete</h2>
        <p style="margin: 0.5rem 0 0 0; color: #ffffff;">
            Your professional market research report is ready
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='results-body'>", unsafe_allow_html=True)

    if "OpportunitySynthesizer" in results:
        report = results["OpportunitySynthesizer"]
        if isinstance(report, dict) and "report" in report:
            st.markdown(report["report"])
        elif isinstance(report, dict) and "response" in report:
            st.markdown(report["response"])
        else:
            st.json(report)

    if "SourceVerifier" in results:
        verification = results["SourceVerifier"]
        with st.expander("Source Verification Details"):
            st.json(verification)

    st.markdown("</div>", unsafe_allow_html=True)

    # Export section
    st.markdown("---")
    st.markdown("### Export Your Report")

    # Get report content for export
    report_content = ""
    if "OpportunitySynthesizer" in results:
        report = results["OpportunitySynthesizer"]
        if isinstance(report, dict) and "report" in report:
            report_content = report["report"]
        elif isinstance(report, dict) and "response" in report:
            report_content = report["response"]
        else:
            report_content = str(report)

    report_title = f"market-research-{brief.offering_what[:30]}"

    export_col1, export_col2, export_col3, export_col4 = st.columns(4)

    with export_col1:
        try:
            pdf_bytes = export_to_pdf(report_content, report_title)
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=get_filename_from_title(report_title, "pdf"),
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.warning(f"PDF export unavailable: {e}")

    with export_col2:
        try:
            docx_bytes = export_to_docx(report_content, report_title)
            st.download_button(
                label="Download Word",
                data=docx_bytes,
                file_name=get_filename_from_title(report_title, "docx"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as e:
            st.warning(f"Word export unavailable: {e}")

    with export_col3:
        st.download_button(
            label="Download Markdown",
            data=report_content,
            file_name=get_filename_from_title(report_title, "md"),
            mime="text/markdown",
            use_container_width=True,
        )

    with export_col4:
        try:
            zip_bytes = create_asset_bundle(
                report_content,
                raw_findings=results,
                title=report_title,
            )
            st.download_button(
                label="Download All Assets",
                data=zip_bytes,
                file_name=get_filename_from_title(report_title, "zip"),
                mime="application/zip",
                use_container_width=True,
            )
        except Exception as e:
            st.warning(f"Asset bundle unavailable: {e}")

    # Start new research button
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start New Research", type="primary", use_container_width=True):
            for key in ["view", "intake_data", "brief", "results"]:
                st.session_state.pop(key, None)
            st.rerun()


# Main app flow
def main():
    """Main application flow with state machine.

    Views: intake -> confirm -> running -> results
    """

    # Initialize session state
    if "view" not in st.session_state:
        st.session_state.view = "intake"

    view = st.session_state.view

    # Always show hero
    render_hero()

    if view == "intake":
        # Show intake form
        intake_data = create_intake_form()

        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            start_button = st.button(
                "Start Research",
                type="primary",
                use_container_width=True,
            )

        if start_button:
            errors = validate_intake(intake_data)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.session_state.intake_data = intake_data
                st.session_state.brief = _build_brief(intake_data)
                st.session_state.view = "confirm"
                st.rerun()

    elif view == "confirm":
        brief = st.session_state.get("brief")
        if brief is None:
            st.session_state.view = "intake"
            st.rerun()
        display_confirmation(brief)

    elif view == "running":
        brief = st.session_state.get("brief")
        if brief is None:
            st.session_state.view = "intake"
            st.rerun()

        results = asyncio.run(run_research(brief))
        st.session_state.results = results
        st.session_state.view = "results"
        st.rerun()

    elif view == "results":
        if st.session_state.get("results") is None:
            st.session_state.view = "intake"
            st.rerun()
        display_results()


if __name__ == "__main__":
    main()
