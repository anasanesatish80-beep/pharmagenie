# Kaggle Submission Checklist

## Required

- GitHub repository: `https://github.com/anasanesatish80-beep/pharmagenie`
- Kaggle writeup: `docs/kaggle_writeup.md`
- Demo script: `docs/demo_script.md`
- Public project code with `.env` excluded
- Short demo video showing the app running locally

## Screenshots To Capture

- Streamlit discovery input console
- Agent swarm running state
- Ranked discovery hypotheses
- Evidence matrix
- FastAPI `/docs` page

## Demo Flow

1. Open Streamlit at `http://127.0.0.1:8501`.
2. Use disease `glioblastoma`.
3. Use objective `Generate and prioritize in silico target and candidate hypotheses from biomedical evidence.`
4. Run the discovery workflow.
5. Show agent progress and generated hypotheses.
6. Open FastAPI docs at `http://127.0.0.1:8080/docs`.
7. Briefly show README architecture and safety limitations.

## Final Safety Checks

- Confirm `.env` is ignored by Git.
- Do not commit API keys or logs.
- Rotate the Google API key after the demo if it will be reused elsewhere.
