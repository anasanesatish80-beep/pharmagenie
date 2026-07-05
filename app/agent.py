"""Google ADK agent definitions for PharmaGenie."""

from google.adk.agents import Agent, SequentialAgent
from google.genai import types

from pharmagenie.config import get_settings
from pharmagenie.mcp_servers.adk_tools import (
    clinical_trials_tool,
    discovery_tool,
    pubchem_tool,
    pubmed_tool,
    uniprot_tool,
)

settings = get_settings()


literature_agent = Agent(
    name="literature_agent",
    model=settings.gemini_model,
    description="Retrieves and summarizes PubMed literature evidence.",
    instruction=(
        "Use the PubMed tool to retrieve biomedical literature evidence. "
        "Summarize only source-backed findings."
    ),
    tools=[pubmed_tool],
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)

protein_agent = Agent(
    name="protein_agent",
    model=settings.gemini_model,
    description="Retrieves protein and target context from UniProt.",
    instruction="Use the UniProt tool to retrieve target/protein evidence.",
    tools=[uniprot_tool],
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)

compound_agent = Agent(
    name="compound_agent",
    model=settings.gemini_model,
    description="Retrieves compound metadata from PubChem.",
    instruction="Use the PubChem tool to retrieve compound metadata and identifiers.",
    tools=[pubchem_tool],
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)

clinical_trial_agent = Agent(
    name="clinical_trial_agent",
    model=settings.gemini_model,
    description="Retrieves clinical trial landscape evidence.",
    instruction="Use the ClinicalTrials.gov tool to retrieve trial landscape evidence.",
    tools=[clinical_trials_tool],
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)

discovery_agent = Agent(
    name="discovery_agent",
    model=settings.gemini_model,
    description="Generates in silico drug discovery hypotheses from gathered evidence.",
    instruction=(
        "Generate in silico target and candidate hypotheses. Never claim validated "
        "efficacy, safety, clinical utility, or patient-specific treatment advice."
    ),
    tools=[discovery_tool],
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
)

root_agent = SequentialAgent(
    name="pharmagenie",
    description="AI multi-agent in silico drug discovery workflow.",
    sub_agents=[
        literature_agent,
        protein_agent,
        compound_agent,
        clinical_trial_agent,
        discovery_agent,
    ],
)
