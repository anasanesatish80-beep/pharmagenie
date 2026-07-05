from fastapi.testclient import TestClient

from pharmagenie.api.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_research_endpoint() -> None:
    client = TestClient(app)

    response = client.post(
        "/research",
        json={
            "disease": "glioblastoma",
            "research_goal": "Summarize early-stage biomedical research evidence.",
        },
    )

    assert response.status_code == 200
    assert "markdown" in response.json()


def test_discover_endpoint() -> None:
    client = TestClient(app)

    response = client.post(
        "/discover",
        json={
            "disease": "glioblastoma",
            "research_goal": "Generate and prioritize in silico discovery hypotheses.",
        },
    )

    assert response.status_code == 200
    assert response.json()["dossier"]["discovery_hypotheses"]
