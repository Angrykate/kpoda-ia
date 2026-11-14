from datetime import datetime

from src.conflits import detecter_conflits
from src.planification import planifier
from src.validation import valider

DISPO = [{"debut": "2026-11-16T17:00", "fin": "2026-11-16T20:00"},
         {"debut": "2026-11-17T17:00", "fin": "2026-11-17T20:00"}]


def tache(i, duree=60, priorite="moyenne", **kw):
    return {"id": f"T{i}", "titre": f"Tâche {i}", "duree_minutes": duree, "priorite": priorite, **kw}


def test_statut_en_attente_de_validation_et_schema():
    p = planifier([tache(1), tache(2)], DISPO)
    assert p["statut"] == "en_attente_de_validation"
    assert valider(p, "planification") == []


def test_priorite_haute_en_premier():
    p = planifier([tache(1, priorite="basse"), tache(2, priorite="haute")], DISPO)
    assert p["sessions"][0]["tache_id"] == "T2"


def test_dependance_respectee():
    p = planifier([tache(1, priorite="basse"), tache(2, priorite="haute", depend_de=["T1"])], DISPO)
    ordre = [s["tache_id"] for s in p["sessions"]]
    assert ordre.index("T1") < ordre.index("T2")


def test_aucune_session_hors_disponibilites():
    p = planifier([tache(i, 120) for i in range(1, 4)], DISPO)
    for s in p["sessions"]:
        d, f = datetime.fromisoformat(s["debut"]), datetime.fromisoformat(s["fin"])
        assert any(datetime.fromisoformat(c["debut"]) <= d and f <= datetime.fromisoformat(c["fin"]) for c in DISPO)


def test_planning_sans_conflit():
    p = planifier([tache(i, 90) for i in range(1, 5)], DISPO)
    assert detecter_conflits(p["sessions"]) == []


def test_tache_longue_decoupee_avec_pause():
    p = planifier([tache(1, 150)], DISPO, session_max=90, pause=10)
    s = p["sessions"]
    assert len(s) == 2
    assert (datetime.fromisoformat(s[1]["debut"]) - datetime.fromisoformat(s[0]["fin"])).seconds == 600


def test_creneaux_insuffisants_signales():
    p = planifier([tache(1, 400)], DISPO)
    assert p["non_planifiees"] and p["non_planifiees"][0]["reste_minutes"] > 0
    assert valider(p, "planification") == []


def test_limite_journaliere():
    p = planifier([tache(i, 90) for i in range(1, 5)], DISPO, max_minutes_jour=180)
    par_jour = {}
    for s in p["sessions"]:
        d = datetime.fromisoformat(s["debut"])
        par_jour[d.date()] = par_jour.get(d.date(), 0) + (datetime.fromisoformat(s["fin"]) - d).seconds // 60
    assert max(par_jour.values()) <= 180


def test_echeance_depassee_signalee():
    p = planifier([tache(1, 60, echeance="2026-11-15")], DISPO)
    assert any("échéance" in a for a in p["avertissements"])


def test_taches_terminees_ignorees():
    p = planifier([tache(1, statut="terminee"), tache(2)], DISPO)
    assert {s["tache_id"] for s in p["sessions"]} == {"T2"}


def test_dependance_circulaire_sans_plantage():
    p = planifier([tache(1, depend_de=["T2"]), tache(2, depend_de=["T1"])], DISPO)
    assert len(p["non_planifiees"]) == 2
