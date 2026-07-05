"""Markdown dossier rendering."""

from pharmagenie.models import ResearchDossier


def render_markdown(dossier: ResearchDossier) -> str:
    """Render a research dossier as markdown."""

    lines = [
        f"# PharmaGenie Research Dossier: {dossier.disease}",
        "",
        f"**Research goal:** {dossier.research_goal}",
        "",
        "## Executive Summary",
        dossier.executive_summary,
        "",
        "## Discovery Hypotheses",
    ]
    if dossier.discovery_hypotheses:
        for hypothesis in dossier.discovery_hypotheses:
            lines.extend(
                [
                    f"### {hypothesis.target}",
                    f"- Overall score: {hypothesis.overall_score:.3f}",
                    f"- Mechanism: {hypothesis.mechanism}",
                    f"- Candidate strategy: {hypothesis.candidate_strategy}",
                    f"- Rationale: {hypothesis.rationale}",
                    f"- Evidence sources: {', '.join(hypothesis.evidence_sources)}",
                    f"- Risk flags: {', '.join(hypothesis.risk_flags)}",
                    "",
                ]
            )
    else:
        lines.extend(["No discovery hypotheses were generated.", ""])
    lines.extend(
        [
        "## Evidence",
        ]
    )
    for item in dossier.evidence:
        url = f" [{item.url}]({item.url})" if item.url else ""
        lines.extend(
            [
                f"### {item.title}",
                f"- Source: {item.source}{url}",
                f"- Confidence: {item.confidence:.2f}",
                f"- Summary: {item.summary}",
                "",
            ]
        )
    lines.extend(["## Limitations", *[f"- {limitation}" for limitation in dossier.limitations]])
    return "\n".join(lines) + "\n"
