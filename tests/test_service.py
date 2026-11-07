from fastapi.testclient import TestClient

from src.service import app

client = TestClient(app)


def test_sante():
    assert client.get("/sante").json() == {"statut": "ok"}


def test_decomposer():
    r = client.post("/decomposer", json={"objectif": "Préparer un examen"})
    assert r.status_code == 200
    assert r.json()["statut_proposition"] == "propose"


def test_objectif_trop_court_refuse():
    assert client.post("/decomposer", json={"objectif": "a"}).status_code == 422
