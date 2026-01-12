"""Research sub-agents for market research."""

from dataclasses import dataclass

from src.models import ResearchBrief


@dataclass
class SubAgent:
    """Base class for research sub-agents."""

    name: str
    mission: str = ""

    def build_prompt(self, brief: ResearchBrief) -> str:
        """Build the prompt for this agent given a research brief."""
        return f"""
You are {self.name}, a specialized research agent.

Mission: {self.mission}

Research Brief:
{brief.to_markdown()}

Conduct your research and return structured findings.
"""

    async def _call_api(self, prompt: str) -> dict:
        """Call the Anthropic API. Override in subclasses or mock in tests."""
        # This will be implemented with actual API call
        return {}

    async def run(self, brief: ResearchBrief, **kwargs) -> dict:
        """Execute the agent's research task."""
        prompt = self.build_prompt(brief)
        result = await self._call_api(prompt)
        return result


class CommunityMapper(SubAgent):
    """Finds where the target audience hangs out online."""

    def __init__(self):
        super().__init__(
            name="CommunityMapper",
            mission="Find WHERE the target audience hangs out online. Identify specific "
            "communities, platforms, influencers, and gathering places.",
        )

    def build_prompt(self, brief: ResearchBrief) -> str:
        """Build Community Mapper specific prompt."""
        return f"""
You are CommunityMapper, a specialized research agent.

Mission: {self.mission}

## Research Brief

**Target Customer:** {brief.target_customer}
**Geography:** {brief.geography}
**Topic:** {brief.offering_what} - {brief.offering_problem}
**Primary Question:** {brief.primary_question}

## Your Task

Search for platform-specific communities where {brief.target_customer} in {brief.geography} discuss topics related to {brief.offering_what}.

Search:
- Reddit: subreddits
- X/Twitter: hashtags, influential accounts
- Facebook: groups
- LinkedIn: professional groups
- YouTube: channels
- Discord/Telegram: servers/groups
- Niche forums

For each community found, provide:
- Platform and URL
- Community size/activity
- Relevance score (1-5)
- Sample content showing relevance
- Key voices to follow

Return structured JSON with your findings.
"""


class VoiceMiner(SubAgent):
    """Extracts verbatim quotes and language patterns."""

    def __init__(self):
        super().__init__(
            name="VoiceMiner",
            mission="Extract the authentic voice of the target audience. Find verbatim "
            "quotes, pain points, desires, objections, and language patterns.",
        )


class PricingIntel(SubAgent):
    """Researches pricing landscape and willingness-to-pay."""

    def __init__(self):
        super().__init__(
            name="PricingIntel",
            mission="Research pricing landscape, economic context, and willingness-to-pay "
            "signals for the target market.",
        )


class CompetitorProfiler(SubAgent):
    """Deep-dives on competitor offerings and gaps."""

    def __init__(self):
        super().__init__(
            name="CompetitorProfiler",
            mission="Deep-dive analysis of competitors: their offerings, positioning, "
            "strengths, weaknesses, and customer sentiment.",
        )

    def build_prompt(self, brief: ResearchBrief) -> str:
        """Build Competitor Profiler specific prompt with known competitors."""
        competitors_str = ", ".join(brief.known_competitors) if brief.known_competitors else "None specified"

        return f"""
You are CompetitorProfiler, a specialized research agent.

Mission: {self.mission}

## Research Brief

**Offering:** {brief.offering_what}
**Target Customer:** {brief.target_customer}
**Geography:** {brief.geography}
**Known Competitors:** {competitors_str}

## Your Task

Start with the known competitors ({competitors_str}) and find more.

For each competitor, research:
- Company/person background
- Exact offering and features
- Pricing and packaging
- Positioning and messaging
- Target audience
- Reviews and testimonials
- Strengths and weaknesses

Analyze gaps and white space opportunities.

Return structured JSON with your findings.
"""


class LocalContext(SubAgent):
    """Researches geography-specific factors."""

    def __init__(self):
        super().__init__(
            name="LocalContext",
            mission="Research geography-specific and culture-specific factors that "
            "impact go-to-market strategy.",
        )


class TrendDetector(SubAgent):
    """Identifies momentum and timing signals."""

    def __init__(self):
        super().__init__(
            name="TrendDetector",
            mission="Identify momentum, timing signals, and trend data for the "
            "research topic.",
        )


class OpportunitySynthesizer(SubAgent):
    """Synthesizes all findings into final report."""

    def __init__(self):
        super().__init__(
            name="OpportunitySynthesizer",
            mission="Synthesize findings from all sub-agents into a comprehensive, "
            "professional-grade market research report.",
        )

    def build_synthesis_prompt(self, brief: ResearchBrief, findings: dict) -> str:
        """Build the synthesis prompt with all findings."""
        findings_text = []
        for agent_name, data in findings.items():
            findings_text.append(f"### {agent_name}\n{data}")

        return f"""
You are OpportunitySynthesizer, the final research agent.

Mission: {self.mission}

## Research Brief

{brief.to_markdown()}

## Findings from Other Agents

{chr(10).join(findings_text)}

## Your Task

Synthesize all findings into a professional 15-30 page market research report with:

1. Executive Summary
2. Research Methodology
3. Market Landscape
4. Customer Deep Dive
5. Competitive Analysis
6. Pricing & Willingness to Pay
7. Go-to-Market Considerations
8. Strategic Recommendations
9. Appendices

Every claim must be backed by evidence from the findings above.
Focus especially on the primary question: {brief.primary_question}

Return the complete report in markdown format.
"""


class SourceVerifier(SubAgent):
    """Verifies sources and flags unsupported claims."""

    def __init__(self):
        super().__init__(
            name="SourceVerifier",
            mission="Verify every source cited in the research report. Check that "
            "URLs are accessible and sources support the claims made.",
        )
