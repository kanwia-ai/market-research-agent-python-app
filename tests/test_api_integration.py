"""Tests for Anthropic API integration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents import CommunityMapper, SubAgent
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
    )


class TestAPIIntegration:
    """Test the Anthropic API integration."""

    @pytest.mark.asyncio
    async def test_call_api_returns_dict(self, sample_brief):
        """API call should return a dictionary."""
        agent = SubAgent(name="TestAgent")

        # Mock the Anthropic client
        with patch("src.agents.anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.Anthropic.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content = [MagicMock(text='{"findings": "test data"}')]
            mock_client.messages.create.return_value = mock_response

            result = await agent._call_api("test prompt")
            assert isinstance(result, dict)
            assert "findings" in result

    @pytest.mark.asyncio
    async def test_call_api_handles_non_json_response(self, sample_brief):
        """API call should handle non-JSON text response."""
        agent = SubAgent(name="TestAgent")

        with patch("src.agents.anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.Anthropic.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="This is plain text response")]
            mock_client.messages.create.return_value = mock_response

            result = await agent._call_api("test prompt")
            assert isinstance(result, dict)
            assert "response" in result

    @pytest.mark.asyncio
    async def test_agent_run_calls_api(self, sample_brief):
        """Agent.run should call the API with built prompt."""
        agent = CommunityMapper()

        with patch.object(agent, "_call_api", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = {"communities": ["reddit.com/r/designers"]}

            await agent.run(sample_brief)

            mock_api.assert_called_once()
            call_args = mock_api.call_args[0][0]
            assert "freelance designers" in call_args
            assert "United States" in call_args

    @pytest.mark.asyncio
    async def test_api_uses_claude_model(self, sample_brief):
        """API should use Claude Sonnet model."""
        agent = SubAgent(name="TestAgent")

        with patch("src.agents.anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.Anthropic.return_value = mock_client

            mock_response = MagicMock()
            mock_response.content = [MagicMock(text='{"data": "test"}')]
            mock_client.messages.create.return_value = mock_response

            await agent._call_api("test prompt")

            call_kwargs = mock_client.messages.create.call_args[1]
            assert "claude" in call_kwargs["model"].lower()
