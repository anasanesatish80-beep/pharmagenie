"""PubMed source client using NCBI E-utilities."""

import logging

import httpx

from pharmagenie.config import get_settings
from pharmagenie.models import EvidenceItem, SourceName
from pharmagenie.sources.base import BiomedicalSourceClient

logger = logging.getLogger(__name__)


class PubMedClient(BiomedicalSourceClient):
    """Mockable PubMed client boundary for NCBI E-utilities integration."""

    async def search(self, disease: str, research_goal: str) -> list[EvidenceItem]:
        """Search PubMed and return normalized literature evidence."""

        settings = get_settings()
        params = {
            "db": "pubmed",
            "term": f"({disease}) AND ({research_goal})",
            "retmode": "json",
            "retmax": "5",
            "sort": "relevance",
            "tool": "PharmaGenie",
        }
        if settings.ncbi_email:
            params["email"] = settings.ncbi_email
        if settings.ncbi_api_key:
            params["api_key"] = settings.ncbi_api_key

        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                search_response = await client.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                    params=params,
                )
                search_response.raise_for_status()
                ids = search_response.json().get("esearchresult", {}).get("idlist", [])
                if not ids:
                    return self._fallback(disease, research_goal, "No PubMed records found.")

                summary_response = await client.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                    params={
                        "db": "pubmed",
                        "id": ",".join(ids),
                        "retmode": "json",
                        "tool": "PharmaGenie",
                    },
                )
                summary_response.raise_for_status()
                result = summary_response.json().get("result", {})

            evidence = []
            for pmid in ids[:3]:
                item = result.get(pmid, {})
                title = item.get("title") or f"PubMed record {pmid}"
                journal = item.get("fulljournalname") or item.get("source") or "PubMed"
                pubdate = item.get("pubdate", "unknown date")
                evidence.append(
                    EvidenceItem(
                        source=SourceName.PUBMED,
                        title=title,
                        url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        summary=f"{journal}; published {pubdate}. PMID {pmid}.",
                        confidence=0.72,
                        metadata={"pmid": pmid, "client": "live"},
                    )
                )
            return evidence or self._fallback(disease, research_goal, "No PubMed summaries parsed.")
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            logger.warning("PubMed live lookup failed: %s", exc)
            return self._fallback(disease, research_goal, "PubMed live lookup failed.")

    def _fallback(self, disease: str, research_goal: str, reason: str) -> list[EvidenceItem]:
        """Return deterministic fallback evidence when PubMed is unavailable."""

        return [
            EvidenceItem(
                source=SourceName.PUBMED,
                title=f"Literature landscape for {disease}",
                url="https://pubmed.ncbi.nlm.nih.gov/",
                summary=(
                    f"{reason} Fallback PubMed summary for '{research_goal}'."
                ),
                confidence=0.35,
                metadata={"client": "fallback"},
            )
        ]
