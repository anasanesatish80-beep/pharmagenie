# Setup Guide

## Prerequisites

- Python 3.12
- Git
- Docker Desktop
- Optional: uv and google-agents-cli for ADK eval/scaffold workflows

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` with any Google, Gemini, NCBI, or deployment values needed for live
API use.

## Verify

```powershell
pytest
ruff check src tests
```
