from pharmagenie.ai.synthesis import DiscoverySynthesisService
from pharmagenie.models import EvidenceItem, SourceName


def test_synthesis_fallback_scores_from_evidence() -> None:
    service = DiscoverySynthesisService()
    evidence = [
        EvidenceItem(
            source=SourceName.UNIPROT,
            title="PTEN",
            summary="Protein target context.",
            confidence=0.68,
            metadata={"client": "live"},
        ),
        EvidenceItem(
            source=SourceName.PUBMED,
            title="Literature",
            summary="Literature context.",
            confidence=0.35,
            metadata={"client": "fallback"},
        ),
    ]

    hypotheses = service.fallback("glioblastoma", evidence)

    assert hypotheses[0].evidence_score > 0.35
    assert "UniProt" in hypotheses[0].evidence_sources
    assert hypotheses[0].risk_flags
