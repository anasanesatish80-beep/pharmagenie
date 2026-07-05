"""UniProt source client using UniProt REST."""

import logging

import httpx

from pharmagenie.config import get_settings
from pharmagenie.models import EvidenceItem, SourceName
from pharmagenie.sources.base import BiomedicalSourceClient

logger = logging.getLogger(__name__)


class UniProtClient(BiomedicalSourceClient):
    """Mockable UniProt client boundary for protein and target metadata."""

    async def search(self, disease: str, research_goal: str) -> list[EvidenceItem]:
        """Search UniProtKB and return protein/target context evidence."""

        settings = get_settings()
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                response = await client.get(
                    "https://rest.uniprot.org/uniprotkb/search",
                    params={
                        "query": f"({disease}) AND (organism_id:9606)",
                        "format": "json",
                        "size": "3",
                        "fields": "accession,protein_name,gene_names,organism_name,cc_function",
                    },
                )
                response.raise_for_status()
                results = response.json().get("results", [])

            evidence = []
            for result in results:
                accession = result.get("primaryAccession", "unknown")
                protein = result.get("proteinDescription", {}).get("recommendedName", {})
                protein_name = protein.get("fullName", {}).get("value", f"UniProt entry {accession}")
                genes = result.get("genes", [])
                gene_names = [
                    gene.get("geneName", {}).get("value")
                    for gene in genes
                    if gene.get("geneName", {}).get("value")
                ]
                function_comments = [
                    text.get("value", "")
                    for comment in result.get("comments", [])
                    if comment.get("commentType") == "FUNCTION"
                    for text in comment.get("texts", [])
                ]
                evidence.append(
                    EvidenceItem(
                        source=SourceName.UNIPROT,
                        title=protein_name,
                        url=f"https://www.uniprot.org/uniprotkb/{accession}/entry",
                        summary=(
                            f"Human protein entry {accession}. Genes: "
                            f"{', '.join(gene_names) or 'not listed'}. "
                            f"{function_comments[0][:260] if function_comments else 'Function not summarized.'}"
                        ),
                        confidence=0.68,
                        metadata={"accession": accession, "client": "live"},
                    )
                )
            return evidence or self._fallback(disease, "No UniProt entries found.")
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            logger.warning("UniProt live lookup failed: %s", exc)
            return self._fallback(disease, "UniProt live lookup failed.")

    def _fallback(self, disease: str, reason: str) -> list[EvidenceItem]:
        """Return deterministic fallback evidence when UniProt is unavailable."""

        return [
            EvidenceItem(
                source=SourceName.UNIPROT,
                title=f"Protein target context for {disease}",
                url="https://www.uniprot.org/",
                summary=f"{reason} Fallback protein target context.",
                confidence=0.32,
                metadata={"client": "fallback"},
            )
        ]
