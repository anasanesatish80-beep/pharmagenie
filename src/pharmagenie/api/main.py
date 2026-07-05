"""FastAPI application for PharmaGenie."""

from fastapi import FastAPI

from pharmagenie.agents import CoordinatorAgent
from pharmagenie.config import get_settings
from pharmagenie.logging_config import configure_logging
from pharmagenie.models import ResearchResponse
from pharmagenie.reports.markdown import render_markdown
from pharmagenie.safety import ResearchRequest

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="PharmaGenie API",
    description="AI multi-agent in silico drug discovery platform API.",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Return service health."""

    return {"status": "ok", "app": settings.app_name}


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest) -> ResearchResponse:
    """Run the multi-agent research workflow."""

    dossier = await CoordinatorAgent().run(request)
    return ResearchResponse(dossier=dossier, markdown=render_markdown(dossier))


@app.post("/discover", response_model=ResearchResponse)
async def discover(request: ResearchRequest) -> ResearchResponse:
    """Run the drug discovery hypothesis generation workflow."""

    dossier = await CoordinatorAgent().run(request)
    return ResearchResponse(dossier=dossier, markdown=render_markdown(dossier))
