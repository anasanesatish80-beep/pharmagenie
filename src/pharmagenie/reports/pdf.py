"""PDF export for research dossiers."""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from pharmagenie.models import ResearchDossier


def write_pdf(dossier: ResearchDossier, output_path: Path) -> Path:
    """Write a minimal PDF dossier to a constrained path."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    y = height - 72
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(72, y, f"PharmaGenie Research Dossier: {dossier.disease}")
    y -= 28
    pdf.setFont("Helvetica", 10)
    for line in [dossier.research_goal, dossier.executive_summary, *dossier.limitations]:
        pdf.drawString(72, y, line[:100])
        y -= 16
        if y < 72:
            pdf.showPage()
            y = height - 72
            pdf.setFont("Helvetica", 10)
    pdf.save()
    return output_path
