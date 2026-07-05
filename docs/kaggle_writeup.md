# Kaggle Writeup: PharmaGenie

PharmaGenie is an AI multi-agent in silico drug discovery platform built for the
Kaggle AI Agents: Intensive Vibe Coding Capstone in the Agents for Good track.
Its goal is to help biomedical researchers generate and prioritize early-stage
drug discovery hypotheses by gathering and synthesizing information from trusted
scientific sources. PharmaGenie does not claim to validate efficacy, recommend
treatments, provide medical advice, or make patient-specific clinical decisions.

The problem is practical: early biomedical research often requires searching
multiple disconnected systems. A researcher may need recent literature from
PubMed, protein and target context from UniProt, compound metadata from PubChem,
and clinical development signals from ClinicalTrials.gov. PharmaGenie organizes
that process as a multi-agent workflow.

The architecture uses a Coordinator Agent as the user-facing root. It validates
the request, applies safety framing, and delegates to a Planner Agent. The
Planner decomposes the task into domain-specific subtasks. A Literature Agent,
Protein Agent, Compound Agent, and Clinical Trial Agent each use MCP-style tool
boundaries to retrieve source-specific evidence. An Evidence Ranking Agent then
orders and reconciles the retrieved evidence. A Target Discovery Agent generates
in silico target and mechanism hypotheses, and a Candidate Prioritization Agent
ranks them by novelty, feasibility, evidence strength, and risk. A Report Agent
generates a structured discovery dossier with source attribution, uncertainty,
and explicit limitations.

The current implementation is a production-oriented prototype. It includes a
FastAPI backend, Streamlit frontend, typed Pydantic schemas, structured logging,
environment-based configuration, safety checks, Docker packaging, GitHub Actions
CI, pytest coverage, markdown report rendering, and PDF export hooks. The source
clients are mockable and attempt live retrieval from PubMed, UniProt, PubChem,
and ClinicalTrials.gov, with explicit fallback evidence when a source is
unavailable.

Security and safety are central to the design. User inputs are validated before
agent execution. Prompt-injection and secret-seeking requests are blocked.
Retrieved source text is treated as untrusted data rather than instructions.
Secrets are loaded from environment variables and excluded from source control.
Generated outputs are constrained to safe report paths. Biomedical responses
include limitations and avoid clinical recommendations.

For deployment, the project includes a Dockerfile and docker-compose setup. The
API container binds to the Cloud Run `$PORT` environment variable and can be
extended for managed deployment. The intended next steps are to install Google
Agents CLI, run the prepared behavioral evals, activate Gemini synthesis with a
configured API key, capture screenshots, and deploy the service.

PharmaGenie demonstrates how agentic systems can support drug discovery in a
responsible way: by generating evidence-linked in silico hypotheses for human
review and experimental validation, rather than making unsupported clinical
claims.
