"""Tests for the research orchestrator."""

from unittest.mock import AsyncMock

import pytest

from src.models import ResearchBrief
from src.orchestrator import ResearchOrchestrator


@pytest.fixture
def sample_brief():
    """Create a sample research brief for testing."""
    return ResearchBrief(
        offering_what="productivity app",
        offering_problem="designers waste time on admin",
        target_customer="freelance designers",
        geography="United States",
        primary_question="What features matter most?",
    )


class TestResearchOrchestrator:
    """Test the research orchestrator."""

    def test_orchestrator_has_all_agents(self):
        """Orchestrator initializes with all 8 agents."""
        orchestrator = ResearchOrchestrator()
        assert len(orchestrator.agents) == 8
        agent_names = [a.name for a in orchestrator.agents]
        assert "CommunityMapper" in agent_names
        assert "VoiceMiner" in agent_names
        assert "PricingIntel" in agent_names
        assert "CompetitorProfiler" in agent_names
        assert "LocalContext" in agent_names
        assert "TrendDetector" in agent_names
        assert "OpportunitySynthesizer" in agent_names
        assert "SourceVerifier" in agent_names

    def test_orchestrator_defines_waves(self):
        """Orchestrator defines the 5-wave execution order."""
        orchestrator = ResearchOrchestrator()
        assert len(orchestrator.waves) == 5

        # Wave 1: Community Mapper + Local Context
        assert "CommunityMapper" in orchestrator.waves[0]
        assert "LocalContext" in orchestrator.waves[0]

        # Wave 2: Voice Miner + Competitor Profiler + Pricing Intel
        assert "VoiceMiner" in orchestrator.waves[1]
        assert "CompetitorProfiler" in orchestrator.waves[1]
        assert "PricingIntel" in orchestrator.waves[1]

        # Wave 3: Trend Detector
        assert "TrendDetector" in orchestrator.waves[2]

        # Wave 4: Opportunity Synthesizer
        assert "OpportunitySynthesizer" in orchestrator.waves[3]

        # Wave 5: Source Verifier
        assert "SourceVerifier" in orchestrator.waves[4]

    @pytest.mark.asyncio
    async def test_run_wave_executes_agents_in_parallel(self, sample_brief):
        """Agents within a wave run in parallel."""
        orchestrator = ResearchOrchestrator()

        # Mock all agents
        for agent in orchestrator.agents:
            agent.run = AsyncMock(return_value={"data": f"{agent.name} results"})

        # Run wave 1 (should run CommunityMapper and LocalContext in parallel)
        results = await orchestrator.run_wave(0, sample_brief)

        # Both agents should have been called
        community_mapper = orchestrator.get_agent("CommunityMapper")
        local_context = orchestrator.get_agent("LocalContext")
        community_mapper.run.assert_called_once()
        local_context.run.assert_called_once()

        # Results should have both
        assert "CommunityMapper" in results
        assert "LocalContext" in results

    @pytest.mark.asyncio
    async def test_run_all_waves_sequential(self, sample_brief):
        """Waves execute sequentially, agents within wave parallel."""
        orchestrator = ResearchOrchestrator()
        wave_order = []

        # Track when each agent runs
        async def make_mock_run(agent_name, wave_num):
            async def mock_run(*args, **kwargs):
                wave_order.append((wave_num, agent_name))
                return {"data": f"{agent_name} results"}
            return mock_run

        # Mock all agents
        for wave_idx, wave_agents in enumerate(orchestrator.waves):
            for agent_name in wave_agents:
                agent = orchestrator.get_agent(agent_name)
                agent.run = AsyncMock(side_effect=lambda *a, w=wave_idx, n=agent_name, **k: {"wave": w, "name": n})

        # Run all waves
        all_results = await orchestrator.run_all(sample_brief)

        # Should have results from all agents
        assert "CommunityMapper" in all_results
        assert "SourceVerifier" in all_results

    def test_get_agent_by_name(self):
        """Can retrieve agent by name."""
        orchestrator = ResearchOrchestrator()
        agent = orchestrator.get_agent("VoiceMiner")
        assert agent is not None
        assert agent.name == "VoiceMiner"

    def test_get_agent_returns_none_for_unknown(self):
        """Returns None for unknown agent name."""
        orchestrator = ResearchOrchestrator()
        agent = orchestrator.get_agent("UnknownAgent")
        assert agent is None
