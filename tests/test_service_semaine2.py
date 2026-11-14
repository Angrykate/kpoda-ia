from fastapi.testclient import TestClient

from src.service import app

client = TestClient(app)
DISPO = [{"debut": "2026-11-16T17:00", "fin": "2026-11-16T20:00"}]
TACHES = [{"id": "T1", "titre": "Exercices", "duree_minutes": 90, "priorite": "haute"}]


def test_clarifier_objectif_vague():
    r = client.post("/clarifier", json={"objectif": "Apprendre l'anglais"})
    assert r.status_code == 200 and len(r.json()["questions"]) >= 1


def test_clarifier_objectif_precis():
    r = client.post("/clarifier", json={"objectif": "Réviser 3 chapitres d'ici vendredi"})
    assert r.json() == {"questions": []}


def test_planifier():
    r = client.post("/planifier", json={"taches": TACHES, "disponibilites": DISPO})
    assert r.status_code == 200
    assert r.json()["statut"] == "en_attente_de_validation"


def test_planifier_donnees_invalides():
    r = client.post("/planifier", json={"taches": TACHES, "disponibilites": [{"debut": "demain", "fin": "x"}]})
    assert r.status_code == 422


def test_conflits():
    s = [{"id": "A", "debut": "2026-11-16T17:00", "fin": "2026-11-16T18:30"},
         {"id": "B", "debut": "2026-11-16T18:00", "fin": "2026-11-16T19:00"}]
    r = client.post("/conflits", json={"sessions": s})
    assert r.status_code == 200 and r.json()["conflits"][0]["type"] == "chevauchement"
