"""Tests for research sub-agents."""

from unittest.mock import AsyncMock, patch

import pytest

from src.agents import (
    CommunityMapper,
    CompetitorProfiler,
    LocalContext,
    OpportunitySynthesizer,
    PricingIntel,
    SourceVerifier,
    SubAgent,
    TrendDetector,
    VoiceMiner,
)
from src.models import ResearchBrief


@pytest.fixture
def sample_brief():
    """Create a sample research brief for testing."""
    return ResearchBrief(
        offering_what="productivity app",
        offering_problem="designers waste time on admin",
        target_customer="freelance designers",
        geography="United States",
        primary_question="What features matter most?",
        known_competitors=["Notion", "Asana"],
    )


class TestSubAgent:
    """Test the base SubAgent class."""

    def test_subagent_has_name(self):
        """SubAgent must have a name."""
        agent = SubAgent(name="TestAgent")
        assert agent.name == "TestAgent"

    def test_subagent_has_mission(self):
        """SubAgent has a mission description."""
        agent = SubAgent(name="TestAgent", mission="Do something useful")
        assert agent.mission == "Do something useful"

    @pytest.mark.asyncio
    async def test_subagent_run_returns_result(self, sample_brief):
        """SubAgent.run() returns a result dict."""
        agent = SubAgent(name="TestAgent")
        # Mock the API call
        with patch.object(agent, "_call_api", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = {"findings": "test data"}
            result = await agent.run(sample_brief)
            assert isinstance(result, dict)


class TestCommunityMapper:
    """Test the CommunityMapper agent."""

    def test_community_mapper_has_correct_name(self):
        """CommunityMapper has the right identity."""
        agent = CommunityMapper()
        assert agent.name == "CommunityMapper"
        assert "community" in agent.mission.lower() or "audience" in agent.mission.lower()

    def test_community_mapper_builds_prompt(self, sample_brief):
        """CommunityMapper builds appropriate prompt from brief."""
        agent = CommunityMapper()
        prompt = agent.build_prompt(sample_brief)
        assert "freelance designers" in prompt
        assert "United States" in prompt


class TestVoiceMiner:
    """Test the VoiceMiner agent."""

    def test_voice_miner_has_correct_name(self):
        """VoiceMiner has the right identity."""
        agent = VoiceMiner()
        assert agent.name == "VoiceMiner"
        assert "voice" in agent.mission.lower() or "quote" in agent.mission.lower()


class TestPricingIntel:
    """Test the PricingIntel agent."""

    def test_pricing_intel_has_correct_name(self):
        """PricingIntel has the right identity."""
        agent = PricingIntel()
        assert agent.name == "PricingIntel"
        assert "pricing" in agent.mission.lower() or "price" in agent.mission.lower()


class TestCompetitorProfiler:
    """Test the CompetitorProfiler agent."""

    def test_competitor_profiler_has_correct_name(self):
        """CompetitorProfiler has the right identity."""
        agent = CompetitorProfiler()
        assert agent.name == "CompetitorProfiler"

    def test_competitor_profiler_uses_known_competitors(self, sample_brief):
        """CompetitorProfiler includes known competitors in prompt."""
        agent = CompetitorProfiler()
        prompt = agent.build_prompt(sample_brief)
        assert "Notion" in prompt
        assert "Asana" in prompt


class TestLocalContext:
    """Test the LocalContext agent."""

    def test_local_context_has_correct_name(self):
        """LocalContext has the right identity."""
        agent = LocalContext()
        assert agent.name == "LocalContext"


class TestTrendDetector:
    """Test the TrendDetector agent."""

    def test_trend_detector_has_correct_name(self):
        """TrendDetector has the right identity."""
        agent = TrendDetector()
        assert agent.name == "TrendDetector"


class TestOpportunitySynthesizer:
    """Test the OpportunitySynthesizer agent."""

    def test_synthesizer_has_correct_name(self):
        """OpportunitySynthesizer has the right identity."""
        agent = OpportunitySynthesizer()
        assert agent.name == "OpportunitySynthesizer"

    @pytest.mark.asyncio
    async def test_synthesizer_accepts_all_findings(self, sample_brief):
        """Synthesizer can receive findings from all other agents."""
        agent = OpportunitySynthesizer()
        findings = {
            "community_mapper": {"communities": []},
            "voice_miner": {"quotes": []},
            "pricing_intel": {"prices": []},
            "competitor_profiler": {"competitors": []},
            "local_context": {"context": {}},
            "trend_detector": {"trends": []},
        }
        # Just verify it builds a prompt without error
        prompt = agent.build_synthesis_prompt(sample_brief, findings)
        assert isinstance(prompt, str)
        assert len(prompt) > 100


class TestSourceVerifier:
    """Test the SourceVerifier agent."""

    def test_source_verifier_has_correct_name(self):
        """SourceVerifier has the right identity."""
        agent = SourceVerifier()
        assert agent.name == "SourceVerifier"
