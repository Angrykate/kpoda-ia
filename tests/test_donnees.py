from src.donnees_synthetiques import generer
from src.conflits import detecter_conflits


def test_reproductible():
    assert generer(graine=7, semaines=4) == generer(graine=7, semaines=4)


def test_tailles_et_profils():
    d = generer(semaines=6, par_profil=3)
    assert len(d["utilisateurs"]) == 9
    assert {u["profil"] for u in d["utilisateurs"]} == {"regulier", "irregulier", "surcharge"}
    assert len(d["taches"]) > 300


def test_integrite_referentielle():
    d = generer()
    taches = {t["id"] for t in d["taches"]}
    users = {u["id"] for u in d["utilisateurs"]}
    assert all(s["tache_id"] in taches and s["utilisateur_id"] in users for s in d["sessions"])
    assert all(r["tache_id"] in taches and r["utilisateur_id"] in users for r in d["reports"])
    assert len({t["id"] for t in d["taches"]}) == len(d["taches"])


def test_profils_distincts():
    d = generer(semaines=8, par_profil=5)
    profil = {u["id"]: u["profil"] for u in d["utilisateurs"]}
    taux = {}
    for p in ("regulier", "irregulier", "surcharge"):
        ts = [t for t in d["taches"] if profil[t["utilisateur_id"]] == p]
        taux[p] = sum(t["statut"] == "terminee" for t in ts) / len(ts)
    assert taux["regulier"] > taux["irregulier"] > taux["surcharge"]


def test_aucune_session_avant_le_debut():
    d = generer()
    assert min(s["debut"] for s in d["sessions"]) >= "2026-09-07"


def test_surcharge_contient_des_conflits():
    d = generer(semaines=6, par_profil=3)
    par_user = {}
    for s in d["sessions"]:
        par_user.setdefault(s["utilisateur_id"], []).append(s)
    sur = [detecter_conflits(v) for k, v in par_user.items() if k.startswith("surcharge")]
    reg = [detecter_conflits(v) for k, v in par_user.items() if k.startswith("regulier")]
    assert sum(len(c) for c in sur) > sum(len(c) for c in reg)
