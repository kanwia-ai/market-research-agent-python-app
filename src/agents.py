"""Research sub-agents for market research."""

import json
import os
from dataclasses import dataclass

import anthropic

from src.models import ResearchBrief

# Depth-based search configuration
# Based on Anthropic's deep research protocol: multi-round, iterative, exhaustive
SEARCH_CONFIG = {
    "overview": {
        "min_sources": 10,
        "target_sources": 20,
        "search_rounds": 2,
        "description": "Quick but thorough initial sweep",
    },
    "thorough": {
        "min_sources": 20,
        "target_sources": 50,
        "search_rounds": 4,
        "description": "Comprehensive multi-round investigation",
    },
    "deep_dive": {
        "min_sources": 50,
        "target_sources": 100,
        "search_rounds": 6,
        "description": "Exhaustive investigation leaving no stone unturned",
    },
}


def get_vicious_search_instructions(depth: str, agent_type: str) -> str:
    """Generate aggressive multi-round search instructions based on depth."""
    config = SEARCH_CONFIG.get(depth, SEARCH_CONFIG["thorough"])

    return f"""
## VICIOUS SEARCH PROTOCOL — {config['description'].upper()}

You are conducting {depth.replace('_', ' ').upper()} research. Be RELENTLESS.

### Source Requirements
- **MINIMUM:** {config['min_sources']} unique, verified sources with URLs
- **TARGET:** {config['target_sources']}+ sources for excellence
- **SEARCH ROUNDS:** {config['search_rounds']} iterative rounds

### Multi-Round Search Strategy

**Round 1 — Initial Sweep:**
- Cast wide net with primary search queries
- Document ALL relevant sources found
- Note promising leads for deeper investigation

**Round 2 — Follow the Leads:**
- For EACH promising source from Round 1, investigate further
- Find sources CITED BY your initial sources (source pyramiding)
- Expand query terms based on terminology discovered

**Round 3+ — Exhaustive Coverage:**
- Search variations: synonyms, related terms, regional variations
- Check competitor mentions, industry reports, academic sources
- Mine social platforms: Reddit threads, Twitter discussions, LinkedIn posts
- Find niche forums, Slack communities, Discord servers
- Search in different date ranges to find historical context

### Query Expansion Techniques
- Start: "[main topic] [geography]"
- Expand: "[related term] [geography] [year]"
- Deepen: "[specific company/person mentioned] review"
- Pyramid: Search for sources cited in articles you find

### Source Diversity Requirements
Gather sources from MULTIPLE categories:
- Social media discussions (Reddit, Twitter/X, LinkedIn)
- Review platforms (G2, Capterra, Trustpilot, app stores)
- Industry publications and reports
- News articles and press releases
- Company websites and pricing pages
- Government/institutional data
- Academic papers (if relevant)
- Forum discussions and community posts
- YouTube comments and video descriptions
- Podcast transcripts and show notes

### CRITICAL: No Source = No Claim
- Every single data point needs a URL
- If you can't find a source, DON'T include the claim
- Quality sources only — no guessing, no fabricating
- Include access date for time-sensitive data

### Stopping Criteria
Do NOT stop searching until you have:
✓ At least {config['min_sources']} verified sources with URLs
✓ Sources from at least 5 different platform types
✓ Completed all {config['search_rounds']} search rounds
✓ Exhausted obvious query variations
"""


@dataclass
class SubAgent:
    """Base class for research sub-agents."""

    name: str
    mission: str = ""

    def get_search_config(self, depth: str) -> dict:
        """Get search configuration for the given depth."""
        return SEARCH_CONFIG.get(depth, SEARCH_CONFIG["thorough"])

    def build_prompt(self, brief: ResearchBrief) -> str:
        """Build the prompt for this agent given a research brief."""
        search_instructions = get_vicious_search_instructions(brief.depth, self.name)
        return f"""
You are {self.name}, a specialized research agent.

Mission: {self.mission}

{search_instructions}

Research Brief:
{brief.to_markdown()}

Conduct your research and return structured findings with ALL source URLs.
"""

    async def _call_api(self, prompt: str) -> dict:
        """Call the Anthropic API."""
        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY", "")
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract text from response
        text = response.content[0].text

        # Try to parse as JSON, otherwise wrap in dict
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"response": text}

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
        search_instructions = get_vicious_search_instructions(brief.depth, self.name)
        return f"""
You are CommunityMapper, a specialized research agent.

Mission: {self.mission}

{search_instructions}

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

## CRITICAL: Source Requirements

Every community you mention MUST include:
1. **Direct URL** to the community (e.g., https://reddit.com/r/example)
2. **Specific post/thread URLs** as evidence of relevance
3. **Date accessed** for each source

For each community found, provide:
- Platform and **full URL**
- Community size/activity with source
- Relevance score (1-5)
- **2-3 specific post URLs** showing relevance with quotes
- Key voices to follow with profile URLs

Return structured JSON with your findings. Every claim needs a URL.
"""


class VoiceMiner(SubAgent):
    """Extracts verbatim quotes and language patterns."""

    def __init__(self):
        super().__init__(
            name="VoiceMiner",
            mission="Extract the authentic voice of the target audience. Find verbatim "
            "quotes, pain points, desires, objections, and language patterns.",
        )

    def build_prompt(self, brief: ResearchBrief) -> str:
        """Build Voice Miner specific prompt."""
        search_instructions = get_vicious_search_instructions(brief.depth, self.name)
        return f"""
You are VoiceMiner, a specialized research agent.

Mission: {self.mission}

{search_instructions}

## Research Brief

**Target Customer:** {brief.target_customer}
**Geography:** {brief.geography}
**Problem:** {brief.offering_problem}
**Primary Question:** {brief.primary_question}

## Your Task

Find the authentic voice of {brief.target_customer}. Search Reddit, Twitter/X, forums, review sites, and communities for:

1. **Pain Points** - What frustrates them? What do they complain about?
2. **Desires** - What do they wish existed? What would make their life easier?
3. **Objections** - What stops them from buying solutions? Price? Trust? Complexity?
4. **Language** - What words/phrases do they use to describe their problems?

## CRITICAL: Source Requirements

Every quote MUST include:
1. **Direct URL** to the exact post/comment/review
2. **Verbatim quote** in quotation marks
3. **Platform and username** (anonymized if needed)
4. **Date** of the post

Example format:
- "I've tried 5 different apps and none of them understand my workflow"
  - Source: https://reddit.com/r/productivity/comments/abc123
  - User: u/frustrated_designer, Posted: Jan 2024

Find at least 15-20 real quotes with URLs. Do NOT make up quotes or URLs.

Return structured JSON with categorized quotes and their source URLs.
"""


class PricingIntel(SubAgent):
    """Researches pricing landscape and willingness-to-pay."""

    def __init__(self):
        super().__init__(
            name="PricingIntel",
            mission="Research pricing landscape, economic context, and willingness-to-pay "
            "signals for the target market.",
        )

    def build_prompt(self, brief: ResearchBrief) -> str:
        """Build Pricing Intel specific prompt."""
        search_instructions = get_vicious_search_instructions(brief.depth, self.name)
        pricing_model = brief.offering_pricing_model or "Not specified"
        return f"""
You are PricingIntel, a specialized research agent.

Mission: {self.mission}

{search_instructions}

## Research Brief

**Offering:** {brief.offering_what}
**Target Customer:** {brief.target_customer}
**Geography:** {brief.geography}
**Proposed Pricing Model:** {pricing_model}

## Your Task

Research pricing intelligence for {brief.offering_what} targeting {brief.target_customer} in {brief.geography}:

1. **Competitor Pricing** - What do similar solutions cost? Tiers? Features per tier?
2. **Market Rates** - What's the going rate in this category?
3. **Willingness to Pay Signals** - What do customers say about pricing in reviews/forums?
4. **Economic Context** - Average income, spending power, currency considerations
5. **Price Sensitivity** - What makes customers balk? What do they consider "worth it"?

## CRITICAL: Source Requirements

Every data point MUST include:
1. **Direct URL** to pricing page, review, or source
2. **Exact figures** with currency
3. **Date** the pricing was observed

Example format:
- Competitor X charges $29/month for basic, $99/month for pro
  - Source: https://competitorx.com/pricing (accessed Jan 2024)
- "I'd happily pay $50/month if it actually saved me time"
  - Source: https://reddit.com/r/example/comments/xyz

Find real pricing data with URLs. Do NOT estimate or guess prices.

Return structured JSON with pricing data and source URLs.
"""


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
        search_instructions = get_vicious_search_instructions(brief.depth, self.name)
        competitors_str = ", ".join(brief.known_competitors) if brief.known_competitors else "None specified"

        return f"""
You are CompetitorProfiler, a specialized research agent.

Mission: {self.mission}

{search_instructions}

## Research Brief

**Offering:** {brief.offering_what}
**Target Customer:** {brief.target_customer}
**Geography:** {brief.geography}
**Known Competitors:** {competitors_str}

## Your Task

Start with the known competitors ({competitors_str}) and discover additional competitors.

For each competitor, research:
- Company/person background
- Exact offering and features
- Pricing and packaging
- Positioning and messaging
- Target audience
- Reviews and testimonials
- Strengths and weaknesses

## CRITICAL: Source Requirements

Every competitor profile MUST include:
1. **Website URL** - Main site and specific pages referenced
2. **Pricing page URL** - Direct link to their pricing
3. **Review URLs** - Links to G2, Capterra, Trustpilot, Reddit discussions
4. **Social proof URLs** - Case studies, testimonials with links

Example format:
- **Competitor X** (https://competitorx.com)
  - Pricing: $29-99/mo (https://competitorx.com/pricing)
  - G2 Rating: 4.5/5 (https://g2.com/products/competitorx/reviews)
  - Key complaint: "Too complex for beginners" (https://reddit.com/r/...)

Find at least 5-10 competitors with full source documentation.

Return structured JSON with competitor profiles and all source URLs.
"""


class LocalContext(SubAgent):
    """Researches geography-specific factors."""

    def __init__(self):
        super().__init__(
            name="LocalContext",
            mission="Research geography-specific and culture-specific factors that "
            "impact go-to-market strategy.",
        )

    def build_prompt(self, brief: ResearchBrief) -> str:
        """Build Local Context specific prompt."""
        search_instructions = get_vicious_search_instructions(brief.depth, self.name)
        return f"""
You are LocalContext, a specialized research agent.

Mission: {self.mission}

{search_instructions}

## Research Brief

**Target Customer:** {brief.target_customer}
**Geography:** {brief.geography}
**Offering:** {brief.offering_what}

## Your Task

Research geography-specific factors for {brief.geography} that impact go-to-market:

1. **Economic Context** - GDP, average income, spending patterns, currency
2. **Digital Landscape** - Internet penetration, popular platforms, payment methods
3. **Cultural Factors** - Business culture, communication preferences, trust signals
4. **Regulatory Environment** - Relevant regulations, compliance requirements
5. **Local Competition** - Region-specific competitors or alternatives
6. **Distribution Channels** - How do people discover/buy similar solutions?

## CRITICAL: Source Requirements

Every insight MUST include:
1. **Direct URL** to the source (World Bank, Statista, news articles, reports)
2. **Publication date** of the data
3. **Specific statistics** with attribution

Example format:
- Internet penetration in {brief.geography}: 45%
  - Source: https://datareportal.com/reports/digital-2024-country
  - Published: January 2024

Use authoritative sources: World Bank, IMF, Statista, government statistics, reputable news.

Return structured JSON with local context data and source URLs.
"""


class TrendDetector(SubAgent):
    """Identifies momentum and timing signals."""

    def __init__(self):
        super().__init__(
            name="TrendDetector",
            mission="Identify momentum, timing signals, and trend data for the "
            "research topic.",
        )

    def build_prompt(self, brief: ResearchBrief) -> str:
        """Build Trend Detector specific prompt."""
        search_instructions = get_vicious_search_instructions(brief.depth, self.name)
        return f"""
You are TrendDetector, a specialized research agent.

Mission: {self.mission}

{search_instructions}

## Research Brief

**Offering:** {brief.offering_what}
**Target Customer:** {brief.target_customer}
**Geography:** {brief.geography}
**Problem:** {brief.offering_problem}

## Your Task

Identify trends and timing signals for {brief.offering_what}:

1. **Search Trends** - Is interest growing, stable, or declining?
2. **Industry Reports** - What do analysts say about this market?
3. **Funding/Investment** - Are VCs investing in this space? Recent raises?
4. **News Momentum** - Recent articles, product launches, acquisitions
5. **Social Signals** - Growing communities, viral discussions, influencer interest
6. **Technology Shifts** - Enabling technologies, platform changes

## CRITICAL: Source Requirements

Every trend MUST include:
1. **Direct URL** to the source
2. **Specific data points** (percentages, numbers, dates)
3. **Publication/observation date**

Example format:
- Search interest for "AI productivity tools" up 150% YoY
  - Source: https://trends.google.com/trends/explore?q=ai+productivity
  - Data as of: January 2024
- Series A funding in productivity space: $2.3B in 2023
  - Source: https://news.crunchbase.com/...

Use: Google Trends, Crunchbase, TechCrunch, industry reports, news sources.

Return structured JSON with trends and source URLs.
"""


class OpportunitySynthesizer(SubAgent):
    """Synthesizes all findings into final report."""

    def __init__(self):
        super().__init__(
            name="OpportunitySynthesizer",
            mission="Synthesize findings from all sub-agents into a comprehensive, "
            "professional-grade market research report.",
        )

    async def run(self, brief: ResearchBrief, **kwargs) -> dict:
        """Execute synthesis with findings from other agents."""
        findings = kwargs.get("findings", {})
        prompt = self.build_synthesis_prompt(brief, findings)
        result = await self._call_api(prompt)
        return result

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

Synthesize all findings into a professional market research report with:

1. Executive Summary
2. Research Methodology
3. Market Landscape
4. Customer Deep Dive
5. Competitive Analysis
6. Pricing & Willingness to Pay
7. Go-to-Market Considerations
8. Strategic Recommendations
9. Sources & References

## CRITICAL: Citation Requirements

This report MUST include inline citations throughout:

1. **Inline Citations** - Every claim needs a source reference like [1], [2], etc.
2. **Hyperlinks** - Where possible, make source names clickable: [Source Name](URL)
3. **Verbatim Quotes** - Include actual quotes from customers in "quotation marks" with attribution
4. **Sources Section** - End with a numbered list of ALL sources with full URLs

Example formatting:
- "The market for productivity tools is growing at 15% annually [1]"
- According to [G2 Reviews](https://g2.com/...), users rate competitor X at 4.2/5
- One freelance designer noted: "I spend 3 hours a day on admin tasks" [Reddit](https://reddit.com/...)

**DO NOT make claims without sources from the findings above.**
**DO NOT invent URLs or statistics.**

Focus especially on the primary question: {brief.primary_question}

Return the complete report in markdown format with full citations.
"""


class SourceVerifier(SubAgent):
    """Verifies sources and flags unsupported claims."""

    def __init__(self):
        super().__init__(
            name="SourceVerifier",
            mission="Verify every source cited in the research report. Check that "
            "URLs are accessible and sources support the claims made.",
        )

    async def run(self, brief: ResearchBrief, **kwargs) -> dict:
        """Execute verification on the synthesized report."""
        report = kwargs.get("report", {})
        prompt = self.build_verification_prompt(brief, report)
        result = await self._call_api(prompt)
        return result

    def build_verification_prompt(self, brief: ResearchBrief, report: dict) -> str:
        """Build the verification prompt."""
        report_text = report.get("response", report.get("report", str(report)))

        return f"""
You are SourceVerifier, a specialized verification agent.

Mission: {self.mission}

## The Report to Verify

{report_text}

## Your Task

Review the report above and verify its sources:

1. **Extract all URLs** mentioned in the report
2. **Categorize each source**:
   - VERIFIED: URL format is valid and claim matches likely source content
   - QUESTIONABLE: URL format looks suspicious or claim seems unsupported
   - MISSING: Important claims without any source citation

3. **Flag unsupported claims** - Any statistics, quotes, or facts without sources

4. **Provide a verification score** (0-100) based on:
   - Percentage of claims with sources
   - Quality and diversity of sources
   - Specificity of citations

## Output Format

Return JSON with:
{{
  "verification_score": 85,
  "total_sources_found": 25,
  "sources": [
    {{
      "url": "https://example.com/...",
      "claim": "The claim this supports",
      "status": "VERIFIED|QUESTIONABLE|MISSING",
      "notes": "Any concerns or validation notes"
    }}
  ],
  "unsupported_claims": [
    "List of claims that need sources"
  ],
  "recommendations": [
    "Suggestions for improving source quality"
  ]
}}
"""
