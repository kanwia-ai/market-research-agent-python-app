"""Streamlit UI for the Market Research Agent."""

import asyncio
import streamlit as st

from src.models import ResearchBrief
from src.orchestrator import ResearchOrchestrator


# Page config
st.set_page_config(
    page_title="Market Research Agent",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Market Research Agent")
st.markdown("*Professional-grade market research powered by 8 specialized AI agents*")


def create_intake_form():
    """Create the 15-question intake form."""

    st.header("Research Intake")
    st.markdown(
        "Before I start researching, I need to understand your situation well enough "
        "to give you $25K-quality insights."
    )

    # Phase 1: The Offering
    st.subheader("Phase 1: The Offering")

    offering_what = st.text_input(
        "1. What is it?",
        placeholder="e.g., productivity app, online course, SaaS platform...",
        help="Product, service, course, marketplace, etc.",
    )

    offering_problem = st.text_area(
        "2. What problem does it solve?",
        placeholder="In one sentence, what pain point does this address?",
        height=80,
    )

    offering_delivery = st.selectbox(
        "3. How would it be delivered?",
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

    offering_pricing = st.selectbox(
        "4. Pricing model in mind?",
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
    st.subheader("Phase 2: Customer Hypothesis")

    target_customer = st.text_area(
        "5. Who do you imagine buying this?",
        placeholder="Be specific - not just demographics, but their situation",
        height=100,
    )

    customer_conversations = st.text_area(
        "6. Have you talked to any potential customers yet?",
        placeholder="If yes, what did you learn? What surprised you? If no, that's fine.",
        height=80,
    )

    segments_include_exclude = st.text_input(
        "7. Any segments to specifically INCLUDE or EXCLUDE?",
        placeholder="e.g., 'Focus on solopreneurs, exclude agencies'",
    )

    # Phase 3: Market Context
    st.subheader("Phase 3: Market Context")

    geography = st.text_input(
        "8. What geographies or markets?",
        placeholder="e.g., United States, UK, Global English-speaking...",
    )

    known_competitors = st.text_input(
        "9. Competitors you're aware of?",
        placeholder="Comma-separated, e.g., Notion, Asana, Monday.com",
    )

    opportunity_thesis = st.text_area(
        "10. Why do you believe there's an opportunity here?",
        placeholder="What's your thesis?",
        height=80,
    )

    # Phase 4: Business Reality
    st.subheader("Phase 4: Business Reality")

    stage = st.selectbox(
        "11. What stage are you at?",
        options=[
            "",
            "Exploring an idea",
            "Committed to building, figuring out details",
            "Already have something, looking to expand/pivot",
            "Existing business entering new market",
        ],
    )

    resources = st.text_input(
        "12. Roughly, what resources do you have to execute?",
        placeholder="e.g., 'bootstrapped solo founder', 'funded team of 10'",
    )

    # Phase 5: Research Priorities
    st.subheader("Phase 5: Research Priorities")

    primary_question = st.text_area(
        "13. What's the #1 question you need answered?",
        placeholder="If this research only answered one thing well, what should it be?",
        height=80,
    )

    kill_criteria = st.text_area(
        "14. What would make you decide NOT to proceed?",
        placeholder="What are the kill criteria?",
        height=80,
    )

    already_known = st.text_area(
        "15. What do you already know that I shouldn't waste time on?",
        placeholder="Any previous research, conversations, or insights?",
        height=80,
    )

    # Depth selection
    st.subheader("Research Depth")

    depth = st.radio(
        "How deep should I go?",
        options=[
            ("overview", "Solid overview (~20 min) - Good for early-stage exploration"),
            ("thorough", "Thorough analysis (~45 min) - Comprehensive with recommendations"),
            ("deep_dive", "Leave no stone unturned (~90 min) - Deep dive with extensive sourcing"),
        ],
        format_func=lambda x: x[1],
        index=1,
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
    """Display progress for a wave."""
    icons = {
        "pending": "⏳",
        "running": "🔄",
        "complete": "✅",
        "error": "❌",
    }
    st.write(f"{icons.get(status, '⏳')} {wave_name}")


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
            st.subheader("Research Progress")
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
        st.header("Research Complete")

        if "OpportunitySynthesizer" in orchestrator.results:
            report = orchestrator.results["OpportunitySynthesizer"]
            if isinstance(report, dict) and "report" in report:
                st.markdown(report["report"])
            else:
                st.json(report)

        if "SourceVerifier" in orchestrator.results:
            verification = orchestrator.results["SourceVerifier"]
            with st.expander("Source Verification Details"):
                st.json(verification)

    return orchestrator.results


# Main app flow
def main():
    """Main application flow."""

    # Initialize session state
    if "research_started" not in st.session_state:
        st.session_state.research_started = False
    if "results" not in st.session_state:
        st.session_state.results = None

    # Intake form
    intake_data = create_intake_form()

    # Confirmation section
    st.markdown("---")

    col1, col2 = st.columns([1, 4])

    with col1:
        start_button = st.button("🚀 Start Research", type="primary", use_container_width=True)

    with col2:
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

                # Show confirmation
                with st.expander("Research Brief (Click to review)", expanded=True):
                    st.markdown(brief.to_markdown())

                st.info("Research would start here. (API integration pending)")
                # TODO: Uncomment when API is connected
                # asyncio.run(run_research(brief))


if __name__ == "__main__":
    main()
