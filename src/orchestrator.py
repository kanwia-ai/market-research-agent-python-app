"""Research orchestrator that coordinates wave-based execution."""

import asyncio
import logging
import os
from typing import Optional

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
from src.schemas import validate_agent_result

logger = logging.getLogger(__name__)

AGENT_TIMEOUT = 180  # seconds per agent

# Token budget ceiling: 0 means no limit
BUDGET_CEILING = int(os.environ.get("RESEARCH_TOKEN_BUDGET", "0"))

# Pricing estimates (per million tokens, Sonnet pricing)
COST_PER_M_INPUT = 3.0   # ~$3 per 1M input tokens
COST_PER_M_OUTPUT = 15.0  # ~$15 per 1M output tokens


class ResearchOrchestrator:
    """Coordinates the execution of research agents in waves.

    Wave structure:
    - Wave 1: Community Mapper + Local Context (parallel)
    - Wave 2: Voice Miner + Competitor Profiler + Pricing Intel (parallel)
    - Wave 3: Trend Detector
    - Wave 4: Opportunity Synthesizer
    - Wave 5: Source Verifier
    """

    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.agents: list[SubAgent] = [
            CommunityMapper(),
            LocalContext(),
            VoiceMiner(),
            PricingIntel(),
            CompetitorProfiler(),
            TrendDetector(),
            OpportunitySynthesizer(),
            SourceVerifier(),
        ]

        # Define wave execution order
        self.waves: list[list[str]] = [
            ["CommunityMapper", "LocalContext"],  # Wave 1
            ["VoiceMiner", "CompetitorProfiler", "PricingIntel"],  # Wave 2
            ["TrendDetector"],  # Wave 3
            ["OpportunitySynthesizer"],  # Wave 4
            ["SourceVerifier"],  # Wave 5
        ]

        # Store results from each wave
        self.results: dict[str, dict] = {}

        # Track per-agent token usage: {agent_name: {input_tokens, output_tokens}}
        self.token_usage: dict[str, dict] = {}

    def get_agent(self, name: str) -> Optional[SubAgent]:
        """Get an agent by name."""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def get_total_tokens(self) -> int:
        """Return total input + output tokens across all agents."""
        total = 0
        for usage in self.token_usage.values():
            total += usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        return total

    def _extract_token_usage(self, agent_name: str, result: dict) -> dict:
        """Extract and accumulate _token_usage from an agent result.

        Removes the _token_usage key from the result dict and accumulates
        the counts in self.token_usage. Returns the cleaned result.
        """
        usage = result.pop("_token_usage", None)
        if usage:
            if agent_name not in self.token_usage:
                self.token_usage[agent_name] = {"input_tokens": 0, "output_tokens": 0}
            self.token_usage[agent_name]["input_tokens"] += usage.get("input_tokens", 0)
            self.token_usage[agent_name]["output_tokens"] += usage.get("output_tokens", 0)
            logger.info(
                "Token usage for %s: input=%d, output=%d (cumulative total=%d)",
                agent_name,
                usage.get("input_tokens", 0),
                usage.get("output_tokens", 0),
                self.get_total_tokens(),
            )
        return result

    def _check_budget(self) -> bool:
        """Check if accumulated tokens exceed the budget ceiling.

        Returns True if within budget (or no budget set), False if exceeded.
        """
        if BUDGET_CEILING <= 0:
            return True
        total = self.get_total_tokens()
        if total >= BUDGET_CEILING:
            logger.warning(
                "Token budget exceeded! Used %d tokens, budget ceiling is %d. "
                "Stopping research.",
                total,
                BUDGET_CEILING,
            )
            return False
        return True

    async def run_wave(self, wave_index: int, brief: ResearchBrief) -> dict[str, dict]:
        """Run all agents in a wave in parallel.

        Args:
            wave_index: Which wave to run (0-4)
            brief: The research brief

        Returns:
            Dict mapping agent names to their results
        """
        wave_agents = self.waves[wave_index]
        tasks = []

        for agent_name in wave_agents:
            agent = self.get_agent(agent_name)
            if agent:
                # Pass accumulated results for later waves
                if agent_name == "OpportunitySynthesizer":
                    coro = self._run_synthesizer(agent, brief)
                elif agent_name == "SourceVerifier":
                    coro = self._run_verifier(agent, brief)
                else:
                    coro = self._run_agent(agent, brief)

                # Wrap each agent with a timeout
                tasks.append(asyncio.wait_for(coro, timeout=AGENT_TIMEOUT))

        # Run all agents in this wave in parallel, capturing exceptions
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, separating successes from failures
        wave_results = {}
        for agent_name, result in zip(wave_agents, results):
            if isinstance(result, asyncio.TimeoutError):
                logger.error("Agent %s timed out after %ds", agent_name, AGENT_TIMEOUT)
                wave_results[agent_name] = {
                    "error": f"Agent timed out after {AGENT_TIMEOUT}s"
                }
                self.results[agent_name] = wave_results[agent_name]
            elif isinstance(result, Exception):
                logger.error("Agent %s failed: %s", agent_name, result, exc_info=result)
                wave_results[agent_name] = {"error": str(result)}
                self.results[agent_name] = wave_results[agent_name]
            else:
                logger.info("Agent %s completed successfully", agent_name)
                # Extract token usage metadata before storing results
                self._extract_token_usage(agent_name, result)
                # Validate result schema
                validation_warnings = validate_agent_result(agent_name, result)
                for warning in validation_warnings:
                    logger.warning("Schema validation: %s", warning)
                wave_results[agent_name] = result
                self.results[agent_name] = result

        return wave_results

    async def _run_agent(self, agent: SubAgent, brief: ResearchBrief) -> dict:
        """Run a standard agent."""
        return await agent.run(brief)

    async def _run_synthesizer(self, agent: SubAgent, brief: ResearchBrief) -> dict:
        """Run the synthesizer with all previous findings."""
        # Gather findings from waves 1-3
        findings = {k: v for k, v in self.results.items() if k != "OpportunitySynthesizer"}
        return await agent.run(brief, findings=findings)

    async def _run_verifier(self, agent: SubAgent, brief: ResearchBrief) -> dict:
        """Run the source verifier on the synthesized report."""
        synthesizer_result = self.results.get("OpportunitySynthesizer", {})
        return await agent.run(brief, report=synthesizer_result)

    async def run_all(
        self,
        brief: ResearchBrief,
        on_wave_complete=None,
    ) -> dict[str, dict]:
        """Run all waves sequentially.

        Args:
            brief: The research brief
            on_wave_complete: Optional callback(wave_index, results) called after each wave

        Returns:
            Dict mapping all agent names to their results
        """
        for wave_idx in range(len(self.waves)):
            # Check budget before starting each wave
            if not self._check_budget():
                logger.warning(
                    "Stopping before %s due to token budget ceiling (%d)",
                    self.get_wave_description(wave_idx),
                    BUDGET_CEILING,
                )
                break

            logger.info(
                "Starting %s", self.get_wave_description(wave_idx)
            )
            wave_results = await self.run_wave(wave_idx, brief)
            logger.info(
                "Completed %s: %d agents finished",
                self.get_wave_description(wave_idx),
                len(wave_results),
            )
            if on_wave_complete:
                on_wave_complete(wave_idx, wave_results)

        # HTTP source verification on the final report
        synthesizer_result = self.results.get("OpportunitySynthesizer", {})
        report_text = synthesizer_result.get("response", synthesizer_result.get("report", ""))
        if report_text and isinstance(report_text, str):
            try:
                from src.source_checker import verify_report_sources
                source_check = await verify_report_sources(report_text)
                self.results["_source_check"] = source_check
                if source_check.get("dead_urls"):
                    logger.warning(
                        "Found %d dead/invalid URLs in report",
                        len(source_check["dead_urls"]),
                    )
                    for dead in source_check["dead_urls"]:
                        logger.warning("  Dead URL: %s (status=%s)", dead["url"], dead.get("status_code"))
            except Exception as e:
                logger.warning("HTTP source verification failed: %s", e)

        # Log final token usage summary and estimated cost
        total_input = sum(
            u.get("input_tokens", 0) for u in self.token_usage.values()
        )
        total_output = sum(
            u.get("output_tokens", 0) for u in self.token_usage.values()
        )
        total_tokens = total_input + total_output
        estimated_cost = (
            (total_input / 1_000_000) * COST_PER_M_INPUT
            + (total_output / 1_000_000) * COST_PER_M_OUTPUT
        )

        logger.info(
            "Research complete. Token usage: input=%d, output=%d, total=%d. "
            "Estimated cost: $%.4f",
            total_input,
            total_output,
            total_tokens,
            estimated_cost,
        )

        # Log per-agent breakdown
        for agent_name, usage in self.token_usage.items():
            logger.info(
                "  %s: input=%d, output=%d",
                agent_name,
                usage.get("input_tokens", 0),
                usage.get("output_tokens", 0),
            )

        return self.results

    def get_wave_description(self, wave_index: int) -> str:
        """Get a human-readable description of a wave."""
        descriptions = [
            "Wave 1: Foundation - Finding communities and local context",
            "Wave 2: Deep Research - Voice mining, competitor profiling, pricing intel",
            "Wave 3: Trends - Analyzing momentum and timing",
            "Wave 4: Synthesis - Combining all findings into report",
            "Wave 5: Verification - Checking all sources and claims",
        ]
        if 0 <= wave_index < len(descriptions):
            return descriptions[wave_index]
        return f"Wave {wave_index + 1}"
