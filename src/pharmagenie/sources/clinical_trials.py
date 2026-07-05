"""ClinicalTrials.gov source client using API v2."""

import logging

import httpx

from pharmagenie.config import get_settings
from pharmagenie.models import EvidenceItem, SourceName
from pharmagenie.sources.base import BiomedicalSourceClient

logger = logging.getLogger(__name__)


class ClinicalTrialsClient(BiomedicalSourceClient):
    """Mockable ClinicalTrials.gov client boundary."""

    async def search(self, disease: str, research_goal: str) -> list[EvidenceItem]:
        """Search ClinicalTrials.gov and return trial landscape evidence."""

        settings = get_settings()
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                response = await client.get(
                    "https://clinicaltrials.gov/api/v2/studies",
                    params={
                        "query.cond": disease,
                        "query.term": research_goal,
                        "pageSize": "5",
                        "format": "json",
                    },
                )
                response.raise_for_status()
                studies = response.json().get("studies", [])

            evidence = []
            for study in studies[:3]:
                protocol = study.get("protocolSection", {})
                identification = protocol.get("identificationModule", {})
                status = protocol.get("statusModule", {})
                design = protocol.get("designModule", {})
                nct_id = identification.get("nctId", "unknown")
                title = identification.get("briefTitle") or f"Clinical trial {nct_id}"
                phases = design.get("phases") or []
                evidence.append(
                    EvidenceItem(
                        source=SourceName.CLINICAL_TRIALS,
                        title=title,
                        url=f"https://clinicaltrials.gov/study/{nct_id}",
                        summary=(
                            f"NCT ID: {nct_id}; status: "
                            f"{status.get('overallStatus', 'unknown')}; phases: "
                            f"{', '.join(phases) if phases else 'not listed'}."
                        ),
                        confidence=0.66,
                        metadata={"nct_id": nct_id, "client": "live"},
                    )
                )
            return evidence or self._fallback(disease, "No ClinicalTrials.gov studies found.")
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            logger.warning("ClinicalTrials.gov live lookup failed: %s", exc)
            return self._fallback(disease, "ClinicalTrials.gov live lookup failed.")

    def _fallback(self, disease: str, reason: str) -> list[EvidenceItem]:
        """Return deterministic fallback evidence when ClinicalTrials.gov is unavailable."""

        return [
            EvidenceItem(
                source=SourceName.CLINICAL_TRIALS,
                title=f"Clinical trial landscape for {disease}",
                url="https://clinicaltrials.gov/",
                summary=f"{reason} Fallback trial landscape.",
                confidence=0.33,
                metadata={"client": "fallback"},
            )
        ]
