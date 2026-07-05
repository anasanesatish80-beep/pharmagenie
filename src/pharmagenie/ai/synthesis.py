"""Gemini-backed discovery hypothesis synthesis with deterministic fallback."""

from __future__ import annotations

import json
import logging
from typing import Any

from google import genai
from google.genai import types

from pharmagenie.config import get_settings
from pharmagenie.models import DiscoveryHypothesis, EvidenceItem

logger = logging.getLogger(__name__)


class DiscoverySynthesisService:
    """Generate structured in silico discovery hypotheses from evidence."""

    async def synthesize(
        self,
        disease: str,
        research_goal: str,
        evidence: list[EvidenceItem],
    ) -> list[DiscoveryHypothesis]:
        """Use Gemini when configured, otherwise return deterministic hypotheses."""

        settings = get_settings()
        if not settings.google_api_key:
            return self.fallback(disease, evidence)

        try:
            client = genai.Client(api_key=settings.google_api_key)
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=self._build_prompt(disease, research_goal, evidence),
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=4096,
                    response_mime_type="application/json",
                    response_schema=list[DiscoveryHypothesis],
                ),
            )
            parsed = getattr(response, "parsed", None)
            if parsed:
                hypotheses = [
                    item if isinstance(item, DiscoveryHypothesis) else self._coerce_hypothesis(item)
                    for item in parsed[:3]
                ]
                return hypotheses or self.fallback(disease, evidence)

            payload = self._loads_json(response.text or "[]")
            items = payload if isinstance(payload, list) else payload.get("hypotheses", [])
            hypotheses = [self._coerce_hypothesis(item) for item in items[:3]]
            return hypotheses or self.fallback(disease, evidence)
        except Exception as exc:  # pragma: no cover - external API behavior
            logger.warning("Gemini discovery synthesis failed: %s", exc)
            return self.fallback(disease, evidence)

    def fallback(self, disease: str, evidence: list[EvidenceItem]) -> list[DiscoveryHypothesis]:
        """Return deterministic discovery hypotheses for offline/demo execution."""

        live_sources = sorted(
            {str(item.source) for item in evidence if item.metadata.get("client") == "live"}
        )
        all_sources = sorted({str(item.source) for item in evidence})
        evidence_score = min(0.75, 0.35 + (0.08 * len(live_sources)) + (0.03 * len(evidence)))
        risk_flags = []
        if not live_sources:
            risk_flags.append("No live source records were available in this run.")
        if any(item.metadata.get("client") == "fallback" for item in evidence):
            risk_flags.append("Some sources used fallback evidence; rerun with full network access.")
        risk_flags.append("Experimental validation is required before any drug development claim.")

        return [
            DiscoveryHypothesis(
                target=f"{disease} evidence-linked target cluster",
                mechanism=(
                    "Prioritize proteins, pathways, and disease mechanisms repeatedly supported "
                    "across retrieved literature, protein, compound, and trial signals."
                ),
                candidate_strategy=(
                    "Generate target-modulating candidate strategies and rank them for in vitro "
                    "assay design, medicinal chemistry review, and safety triage."
                ),
                rationale=(
                    f"The dossier contains {len(evidence)} evidence items across "
                    f"{', '.join(all_sources) or 'no sources'}."
                ),
                evidence_sources=all_sources,
                novelty_score=0.48,
                feasibility_score=0.58,
                evidence_score=round(evidence_score, 2),
                risk_flags=risk_flags,
            )
        ]

    def _build_prompt(self, disease: str, research_goal: str, evidence: list[EvidenceItem]) -> str:
        """Build a compact, source-grounded Gemini prompt."""

        evidence_lines = [
            {
                "source": str(item.source),
                "title": item.title,
                "summary": item.summary,
                "url": item.url,
                "confidence": item.confidence,
            }
            for item in evidence[:12]
        ]
        return json.dumps(
            {
                "task": (
                    "Generate up to 2 concise in silico drug discovery hypotheses. Do not claim "
                    "efficacy, safety, clinical utility, or validated discovery."
                ),
                "disease": disease,
                "research_goal": research_goal,
                "evidence": evidence_lines,
                "output_schema": [
                    {
                        "target": "string",
                        "mechanism": "string",
                        "candidate_strategy": "string",
                        "rationale": "string",
                        "evidence_sources": ["source names"],
                        "novelty_score": "float 0-1",
                        "feasibility_score": "float 0-1",
                        "evidence_score": "float 0-1",
                        "risk_flags": ["string"],
                    }
                ],
            }
        )

    def _coerce_hypothesis(self, item: dict[str, Any]) -> DiscoveryHypothesis:
        """Validate model output as a DiscoveryHypothesis."""

        return DiscoveryHypothesis(
            target=str(item.get("target", "Unspecified target hypothesis"))[:200],
            mechanism=str(item.get("mechanism", "Mechanism not specified."))[:1000],
            candidate_strategy=str(item.get("candidate_strategy", "Strategy not specified."))[:1000],
            rationale=str(item.get("rationale", "Rationale not specified."))[:1000],
            evidence_sources=[str(source) for source in item.get("evidence_sources", [])][:8],
            novelty_score=self._score(item.get("novelty_score", 0.4)),
            feasibility_score=self._score(item.get("feasibility_score", 0.4)),
            evidence_score=self._score(item.get("evidence_score", 0.4)),
            risk_flags=[str(flag) for flag in item.get("risk_flags", [])][:8],
        )

    def _loads_json(self, raw_text: str) -> Any:
        """Load model JSON, tolerating fenced JSON output."""

        text = raw_text.strip()
        if text.startswith("```"):
            text = text.strip("`").removeprefix("json").strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            starts = [index for index in (text.find("["), text.find("{")) if index >= 0]
            if not starts:
                raise
            start = min(starts)
            end = max(text.rfind("]"), text.rfind("}"))
            if end <= start:
                raise
            return json.loads(text[start : end + 1])

    def _score(self, value: Any) -> float:
        """Clamp model-provided scores to the 0-1 range."""

        return max(0.0, min(1.0, float(value)))
