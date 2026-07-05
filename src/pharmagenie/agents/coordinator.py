"""Coordinator agent and end-to-end research workflow."""

import logging

from pharmagenie.agents.discovery_agents import CandidatePrioritizationAgent, TargetDiscoveryAgent
from pharmagenie.agents.evidence_ranking import EvidenceRankingAgent
from pharmagenie.agents.planner import PlannerAgent
from pharmagenie.agents.report_agent import ReportAgent
from pharmagenie.models import AgentStep, ResearchDossier
from pharmagenie.safety import ResearchRequest, screen_request

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """Root coordinator for the PharmaGenie multi-agent workflow."""

    name = "Coordinator Agent"

    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.ranker = EvidenceRankingAgent()
        self.target_discovery = TargetDiscoveryAgent()
        self.candidate_prioritization = CandidatePrioritizationAgent()
        self.reporter = ReportAgent()

    async def run(self, request: ResearchRequest) -> ResearchDossier:
        """Validate safety, orchestrate agents, and return a dossier."""

        steps = [
            AgentStep(
                name=self.name,
                status="started",
                detail="Validated request and started research workflow.",
            )
        ]
        decision = screen_request(request)
        if not decision.allowed:
            logger.warning("Blocked unsafe request: %s", decision.reason)
            steps.append(AgentStep(name=self.name, status="blocked", detail=decision.reason))
            return self.reporter.build(request.disease, request.research_goal, [], steps)

        agents, plan_step = self.planner.create_plan(request.disease, request.research_goal)
        steps.append(plan_step)

        evidence = []
        for agent in agents:
            steps.append(agent.step("started", "Running source-specific research task."))
            evidence.extend(await agent.run(request.disease, request.research_goal))
            steps.append(agent.step("completed", "Source-specific research task completed."))

        ranked, ranking_step = self.ranker.rank(evidence)
        steps.append(ranking_step)
        hypotheses = await self.target_discovery.generate(
            request.disease,
            request.research_goal,
            ranked,
        )
        steps.append(
            AgentStep(
                name=self.target_discovery.name,
                status="completed",
                detail=f"Generated {len(hypotheses)} in silico discovery hypotheses.",
            )
        )
        prioritized = self.candidate_prioritization.prioritize(hypotheses)
        steps.append(
            AgentStep(
                name=self.candidate_prioritization.name,
                status="completed",
                detail="Prioritized discovery hypotheses for experimental follow-up.",
            )
        )
        return self.reporter.build(
            request.disease,
            request.research_goal,
            ranked,
            steps,
            discovery_hypotheses=prioritized,
        )
