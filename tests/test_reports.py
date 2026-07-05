from pharmagenie.models import EvidenceItem, ResearchDossier, SourceName
from pharmagenie.reports.markdown import render_markdown


def test_render_markdown_contains_limitations() -> None:
    dossier = ResearchDossier(
        disease="glioblastoma",
        research_goal="Summarize evidence.",
        executive_summary="Research summary.",
        evidence=[
            EvidenceItem(
                source=SourceName.PUBMED,
                title="Example paper",
                summary="Example summary.",
                confidence=0.8,
            )
        ],
        limitations=["Not medical advice."],
        agent_steps=[],
    )

    markdown = render_markdown(dossier)

    assert "# PharmaGenie Research Dossier: glioblastoma" in markdown
    assert "Not medical advice." in markdown
