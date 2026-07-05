# Five-Minute Demo Script

## 0:00 - Problem

Biomedical researchers spend large amounts of time gathering literature, target,
compound, and trial context from separate trusted databases.

## 0:45 - Solution

PharmaGenie is a multi-agent in silico drug discovery platform that coordinates
specialist agents to generate and prioritize evidence-linked discovery
hypotheses.

## 1:30 - Architecture

Show the Mermaid diagram in the README. Explain Coordinator, Planner, four
domain agents, Evidence Ranking Agent, Report Agent, and MCP tool boundaries.

## 2:30 - Demo Query

Use disease `glioblastoma` and goal `Generate and prioritize in silico target
and candidate hypotheses from biomedical evidence.`

## 3:30 - Safety

Show limitations: not medical advice, not drug discovery, no efficacy claims,
prompt injection screening, environment-based secrets, safe report handling.

## 4:15 - Engineering Quality

Show tests, Dockerfile, GitHub Actions, docs, and Cloud Run compatibility.

## 4:45 - Future Work

Replace placeholder clients with live source APIs, register MCP servers, add
Agents CLI behavioral evals, and deploy to Cloud Run.
