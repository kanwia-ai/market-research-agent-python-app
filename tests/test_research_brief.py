"""Tests for ResearchBrief data structure."""

import pytest
from src.models import ResearchBrief


class TestResearchBrief:
    """Test the ResearchBrief data class."""

    def test_create_brief_with_required_fields(self):
        """Brief can be created with minimum required fields."""
        brief = ResearchBrief(
            offering_what="productivity app for freelance designers",
            offering_problem="designers waste time on admin tasks",
            target_customer="freelance designers making $50-150k/year",
            geography="United States",
            primary_question="What features matter most?",
        )
        assert brief.offering_what == "productivity app for freelance designers"
        assert brief.primary_question == "What features matter most?"

    def test_brief_has_all_intake_fields(self):
        """Brief captures all 15 intake questions."""
        brief = ResearchBrief(
            # Required fields
            offering_what="productivity app",
            offering_problem="time wasted on admin",
            target_customer="freelance designers",
            geography="US",
            primary_question="what features matter?",
            # Optional fields
            offering_delivery="SaaS web app",
            offering_pricing_model="subscription",
            customer_conversations="talked to 5 designers",
            segments_include_exclude="exclude agencies",
            known_competitors=["Notion", "Asana"],
            opportunity_thesis="designers underserved by generic tools",
            stage="committed",
            resources="bootstrapped solo founder",
            kill_criteria="if WTP < $20/month",
            already_known="designers hate complex UIs",
        )
        assert brief.offering_delivery == "SaaS web app"
        assert brief.known_competitors == ["Notion", "Asana"]
        assert brief.kill_criteria == "if WTP < $20/month"

    def test_brief_to_dict(self):
        """Brief can be serialized to dict for passing to agents."""
        brief = ResearchBrief(
            offering_what="app",
            offering_problem="problem",
            target_customer="customer",
            geography="US",
            primary_question="question",
        )
        data = brief.to_dict()
        assert isinstance(data, dict)
        assert data["offering_what"] == "app"
        assert data["primary_question"] == "question"

    def test_brief_to_markdown(self):
        """Brief can be rendered as markdown for saving."""
        brief = ResearchBrief(
            offering_what="app",
            offering_problem="problem",
            target_customer="customer",
            geography="US",
            primary_question="question",
        )
        md = brief.to_markdown()
        assert "# Research Brief" in md
        assert "app" in md
        assert "question" in md
