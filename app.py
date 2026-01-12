"""Streamlit UI for the Market Research Agent."""

import asyncio

import streamlit as st

from src.models import ResearchBrief
from src.orchestrator import ResearchOrchestrator

# Page config
st.set_page_config(
    page_title="Market Research Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for Quantilope-inspired design
st.markdown(
    """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    /* Apply Inter font globally */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    /* Main theme colors - WCAG 2.1 AA compliant */
    :root {
        --primary-teal: #007A75;  /* Darkened for better contrast */
        --primary-dark: #006560;
        --text-dark: #1a1a2e;
        --text-secondary: #4a5568;  /* 7:1 contrast on white */
        --bg-light: #f8fafa;
        --white: #ffffff;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Force light theme with subtle gradient background */
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #ffffff 0%, #f0fdf9 50%, #ecfdf5 100%) !important;
        background-attachment: fixed !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f8fafa !important;
    }

    /* Decorative background pattern */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        right: 0;
        width: 600px;
        height: 600px;
        background: radial-gradient(circle at center, rgba(0, 122, 117, 0.08) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    .stApp::after {
        content: '';
        position: fixed;
        bottom: 0;
        left: 0;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle at center, rgba(0, 150, 144, 0.06) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    /* Force text colors on all elements */
    .stApp, .main, p, span, div, label, h1, h2, h3, h4, h5, h6 {
        color: #1a1a2e !important;
    }

    /* Override Streamlit's default label styling */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stRadio label {
        color: #1a1a2e !important;
        font-weight: 500 !important;
    }

    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        background-color: #ffffff !important;
    }

    /* Hero section */
    .hero-title {
        font-size: 3.25rem;
        font-weight: 700;
        color: #1a1a2e !important;
        margin-bottom: 0.75rem;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        font-size: 1.25rem;
        color: #4a5568 !important;
        margin-bottom: 2rem;
        font-weight: 400;
        line-height: 1.6;
    }

    .teal-accent {
        color: #007A75 !important;
        background: linear-gradient(135deg, #007A75 0%, #00a896 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Card styling - elevated with depth */
    .intake-card {
        background: linear-gradient(145deg, #ffffff 0%, #fafffe 100%);
        border-radius: 20px;
        padding: 2rem;
        box-shadow:
            0 4px 6px rgba(0, 122, 117, 0.04),
            0 10px 40px rgba(0, 122, 117, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 122, 117, 0.1);
        position: relative;
        overflow: hidden;
    }

    .intake-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #007A75, #00a896, #007A75);
        background-size: 200% 100%;
    }

    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(0, 122, 117, 0.1);
    }

    .card-icon {
        width: 52px;
        height: 52px;
        background: linear-gradient(135deg, #007A75 0%, #00a896 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 122, 117, 0.3);
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a1a2e;
        margin: 0;
    }

    .card-subtitle {
        font-size: 0.875rem;
        color: #5a6777;  /* WCAG AA compliant - 5.5:1 contrast on white */
        margin: 0;
    }

    /* Stats section */
    .stats-container {
        display: flex;
        gap: 2rem;
        margin: 2rem 0;
    }

    .stat-box {
        background: linear-gradient(135deg, #007A75 0%, #009690 100%);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        text-align: center;
        flex: 1;
        color: #ffffff;
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .stat-label {
        font-size: 0.875rem;
        color: #ffffff;  /* Full white for accessibility */
    }

    /* Progress wave styling */
    .wave-item {
        display: flex;
        align-items: center;
        padding: 1.125rem 1.5rem;
        background: linear-gradient(145deg, #ffffff 0%, #fafffe 100%);
        border-radius: 14px;
        margin-bottom: 0.75rem;
        border-left: 5px solid #e0e7e6;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .wave-item.running {
        border-left-color: #007A75;
        background: linear-gradient(145deg, #e8f7f6 0%, #d8f3f1 100%);
        box-shadow: 0 4px 15px rgba(0, 122, 117, 0.15);
        animation: pulse-border 2s ease-in-out infinite;
    }

    @keyframes pulse-border {
        0%, 100% { border-left-color: #007A75; }
        50% { border-left-color: #00a896; }
    }

    .wave-item.complete {
        border-left-color: #007A75;
        background: linear-gradient(145deg, #f0fdf9 0%, #e8f7f6 100%);
    }

    .wave-item.error {
        border-left-color: #dc2626;
        background: linear-gradient(145deg, #fef2f2 0%, #fee2e2 100%);
    }

    .wave-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.125rem;
    }

    /* Button styling - WCAG AA compliant with polish */
    .stButton > button {
        background: linear-gradient(135deg, #007A75 0%, #00a896 100%);
        color: #ffffff !important;
        border: none;
        border-radius: 14px;
        padding: 1rem 3rem;
        font-size: 1.1rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow:
            0 4px 15px rgba(0, 122, 117, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow:
            0 8px 25px rgba(0, 122, 117, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        background: linear-gradient(135deg, #006963 0%, #007A75 100%);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:focus {
        outline: 3px solid #007A75;
        outline-offset: 3px;
    }

    .stButton > button:active {
        transform: translateY(-1px);
    }

    /* Input styling - force light backgrounds */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 10px;
        border: 2px solid #d1d5db !important;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        background-color: #ffffff !important;
        color: #1a1a2e !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #007A75 !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 117, 0.2);
        outline: none;
    }

    /* Selectbox dropdown styling */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
    }

    .stSelectbox [data-baseweb="select"] {
        background-color: #ffffff !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
    }

    /* Section divider */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, rgba(0, 122, 117, 0.2) 25%, rgba(0, 122, 117, 0.3) 50%, rgba(0, 122, 117, 0.2) 75%, transparent 100%);
        margin: 3rem 0;
        border-radius: 2px;
    }

    /* Feature badges - WCAG AA compliant with flair */
    .feature-badge {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #e0f7f5 0%, #d0f0ed 100%);
        color: #005a52 !important;
        padding: 0.625rem 1.125rem;
        border-radius: 100px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(0, 122, 117, 0.15);
        box-shadow: 0 2px 8px rgba(0, 122, 117, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .feature-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 122, 117, 0.15);
    }

    /* Results section */
    .results-header {
        background: linear-gradient(135deg, #007A75 0%, #00a896 100%);
        color: #ffffff;
        padding: 2.5rem;
        border-radius: 20px 20px 0 0;
        margin-bottom: 0;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 122, 117, 0.3);
    }

    .results-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -25%;
        width: 50%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    }

    .results-body {
        background: linear-gradient(180deg, #ffffff 0%, #fafffe 100%);
        padding: 2.5rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 122, 117, 0.1);
        border-top: none;
    }

    /* Decorative dots */
    .decorative-dots {
        position: fixed;
        top: 100px;
        right: 50px;
        width: 200px;
        height: 200px;
        opacity: 0.1;
        z-index: -1;
    }

    /* Phase label */
    .phase-label {
        background: #007A75;
        color: #ffffff;
        padding: 0.25rem 0.75rem;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Radio button styling */
    .stRadio > div {
        background: #ffffff !important;
        border-radius: 12px;
        padding: 1rem;
    }

    .stRadio label {
        color: #1a1a2e !important;
    }

    .stRadio [data-testid="stMarkdownContainer"] p {
        color: #1a1a2e !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: #ffffff !important;
        border-radius: 12px;
        color: #1a1a2e !important;
    }

    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
    }

    /* Help text / tooltips */
    .stTooltipIcon {
        color: #4a5568 !important;
    }

    /* Placeholder text */
    input::placeholder, textarea::placeholder {
        color: #6b7280 !important;
        opacity: 1 !important;
    }

    /* Accessibility enhancements */
    /* Ensure focus is visible on all interactive elements */
    a:focus, button:focus, input:focus, textarea:focus, select:focus {
        outline: 3px solid #007A75;
        outline-offset: 2px;
    }

    /* Ensure sufficient line height for readability */
    p, li, label {
        line-height: 1.6;
    }

    /* Skip link for keyboard navigation */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 0;
        background: #007A75;
        color: #ffffff;
        padding: 8px 16px;
        z-index: 100;
        text-decoration: none;
        font-weight: 600;
    }

    .skip-link:focus {
        top: 0;
    }

    /* Ensure placeholder text has sufficient contrast */
    ::placeholder {
        color: #6b7280;  /* 4.5:1 contrast ratio */
        opacity: 1;
    }

    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .intake-card {
            border: 2px solid #1a1a2e;
        }
        .wave-item {
            border-left-width: 6px;
        }
    }

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        .stButton > button,
        .wave-item {
            transition: none;
        }
        .stButton > button:hover {
            transform: none;
        }
    }
</style>
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


async def run_research(brief: ResearchBrief):
    """Run the research and display progress."""
    orchestrator = ResearchOrchestrator()

    progress_placeholder = st.empty()
    results_placeholder = st.empty()

    wave_statuses = ["pending"] * 5

    for wave_idx in range(5):
        # Update status to running
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

        # Run the wave
        try:
            await orchestrator.run_wave(wave_idx, brief)
            wave_statuses[wave_idx] = "complete"
        except Exception as e:
            wave_statuses[wave_idx] = "error"
            st.error(f"Error in {orchestrator.get_wave_description(wave_idx)}: {e}")

    # Display final results
    with results_placeholder.container():
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

        if "OpportunitySynthesizer" in orchestrator.results:
            report = orchestrator.results["OpportunitySynthesizer"]
            if isinstance(report, dict) and "report" in report:
                st.markdown(report["report"])
            elif isinstance(report, dict) and "response" in report:
                st.markdown(report["response"])
            else:
                st.json(report)

        if "SourceVerifier" in orchestrator.results:
            verification = orchestrator.results["SourceVerifier"]
            with st.expander("🔍 Source Verification Details"):
                st.json(verification)

        st.markdown("</div>", unsafe_allow_html=True)

    return orchestrator.results


# Main app flow
def main():
    """Main application flow."""

    # Initialize session state
    if "research_started" not in st.session_state:
        st.session_state.research_started = False
    if "results" not in st.session_state:
        st.session_state.results = None

    # Hero section
    render_hero()

    # Intake form
    intake_data = create_intake_form()

    # Confirmation section
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        start_button = st.button(
            "🚀 Start Research",
            type="primary",
            use_container_width=True,
        )

    if start_button:
        errors = validate_intake(intake_data)
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Create brief
            brief = ResearchBrief(
                offering_what=intake_data["offering_what"],
                offering_problem=intake_data["offering_problem"],
                target_customer=intake_data["target_customer"],
                geography=intake_data["geography"],
                primary_question=intake_data["primary_question"],
                offering_delivery=intake_data["offering_delivery"],
                offering_pricing_model=intake_data["offering_pricing_model"],
                customer_conversations=intake_data["customer_conversations"],
                segments_include_exclude=intake_data["segments_include_exclude"],
                known_competitors=intake_data["known_competitors"],
                opportunity_thesis=intake_data["opportunity_thesis"],
                stage=intake_data["stage"],
                resources=intake_data["resources"],
                kill_criteria=intake_data["kill_criteria"],
                already_known=intake_data["already_known"],
                depth=intake_data["depth"],
            )

            # Show brief summary
            with st.expander("📋 Research Brief Summary", expanded=False):
                st.markdown(brief.to_markdown())

            # Run the research
            st.session_state.research_started = True
            st.session_state.results = asyncio.run(run_research(brief))


if __name__ == "__main__":
    main()
