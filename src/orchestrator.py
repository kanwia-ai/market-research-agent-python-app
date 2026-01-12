"""Research orchestrator that coordinates wave-based execution."""

import asyncio
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

    def get_agent(self, name: str) -> Optional[SubAgent]:
        """Get an agent by name."""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

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
                    tasks.append(self._run_synthesizer(agent, brief))
                elif agent_name == "SourceVerifier":
                    tasks.append(self._run_verifier(agent, brief))
                else:
                    tasks.append(self._run_agent(agent, brief))

        # Run all agents in this wave in parallel
        results = await asyncio.gather(*tasks)

        # Map results back to agent names
        wave_results = {}
        for agent_name, result in zip(wave_agents, results):
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

    async def run_all(self, brief: ResearchBrief) -> dict[str, dict]:
        """Run all waves sequentially.

        Args:
            brief: The research brief

        Returns:
            Dict mapping all agent names to their results
        """
        for wave_idx in range(len(self.waves)):
            await self.run_wave(wave_idx, brief)

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
