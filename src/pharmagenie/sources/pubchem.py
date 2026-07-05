"""PubChem source client using PUG REST."""

import logging
from urllib.parse import quote

import httpx

from pharmagenie.config import get_settings
from pharmagenie.models import EvidenceItem, SourceName
from pharmagenie.sources.base import BiomedicalSourceClient

logger = logging.getLogger(__name__)


class PubChemClient(BiomedicalSourceClient):
    """Mockable PubChem client boundary for compound metadata."""

    async def search(self, disease: str, research_goal: str) -> list[EvidenceItem]:
        """Search PubChem for compound metadata related to request terms."""

        settings = get_settings()
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                for term in self._candidate_terms(disease, research_goal):
                    cid_response = await client.get(
                        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
                        f"{quote(term)}/cids/JSON"
                    )
                    if cid_response.status_code == 404:
                        continue
                    cid_response.raise_for_status()
                    cids = cid_response.json().get("IdentifierList", {}).get("CID", [])[:3]
                    if not cids:
                        continue
                    props_response = await client.get(
                        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
                        f"{','.join(str(cid) for cid in cids)}/property/"
                        "Title,MolecularFormula,MolecularWeight,CanonicalSMILES/JSON"
                    )
                    props_response.raise_for_status()
                    compounds = props_response.json().get("PropertyTable", {}).get("Properties", [])
                    evidence = [
                        EvidenceItem(
                            source=SourceName.PUBCHEM,
                            title=compound.get("Title") or f"PubChem CID {compound.get('CID')}",
                            url=f"https://pubchem.ncbi.nlm.nih.gov/compound/{compound.get('CID')}",
                            summary=(
                                f"Formula: {compound.get('MolecularFormula', 'unknown')}; "
                                f"MW: {compound.get('MolecularWeight', 'unknown')}; "
                                f"SMILES: {compound.get('CanonicalSMILES', 'not available')[:120]}."
                            ),
                            confidence=0.62,
                            metadata={"cid": str(compound.get("CID")), "client": "live"},
                        )
                        for compound in compounds
                    ]
                    if evidence:
                        return evidence
            return self._fallback(disease, "No PubChem compounds found for request terms.")
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            logger.warning("PubChem live lookup failed: %s", exc)
            return self._fallback(disease, "PubChem live lookup failed.")

    def _candidate_terms(self, disease: str, research_goal: str) -> list[str]:
        """Pick conservative possible compound-name terms from the request."""

        terms = [disease]
        stopwords = {"target", "candidate", "candidates", "hypothesis", "hypotheses", "discovery"}
        for token in research_goal.replace(",", " ").replace(".", " ").split():
            cleaned = token.strip("()[]{}:;").lower()
            if len(cleaned) >= 5 and cleaned not in stopwords:
                terms.append(cleaned)
        return list(dict.fromkeys(terms))[:8]

    def _fallback(self, disease: str, reason: str) -> list[EvidenceItem]:
        """Return deterministic fallback evidence when PubChem is unavailable."""

        return [
            EvidenceItem(
                source=SourceName.PUBCHEM,
                title=f"Compound context related to {disease}",
                url="https://pubchem.ncbi.nlm.nih.gov/",
                summary=f"{reason} Fallback compound context.",
                confidence=0.3,
                metadata={"client": "fallback"},
            )
        ]
