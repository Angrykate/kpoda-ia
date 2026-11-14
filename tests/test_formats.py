import json
from pathlib import Path

import pytest

from src.validation import valider

DATA = Path(__file__).resolve().parent.parent / "data" / "formats_complementaires"
CAS = [("planification", "exemple_planification.json"),
       ("replanification", "exemple_replanification.json"),
       ("recommandation_autonomie", "exemple_recommandation_autonomie.json"),
       ("rapport", "exemple_rapport.json")]


def charge(f):
    return json.loads((DATA / f).read_text(encoding="utf-8"))


@pytest.mark.parametrize("schema,fichier", CAS)
def test_exemple_valide(schema, fichier):
    assert valider(charge(fichier), schema) == []


def test_planning_sans_statut_attente_refuse():
    d = charge("exemple_planification.json")
    d["statut"] = "applique"
    assert valider(d, "planification") != []


def test_recommandation_un_seul_indicateur_refusee():
    d = charge("exemple_recommandation_autonomie.json")
    d["indicateurs"] = d["indicateurs"][:1]
    assert valider(d, "recommandation_autonomie") != []


def test_recommandation_decision_du_parent_obligatoire():
    d = charge("exemple_recommandation_autonomie.json")
    d["decision_par"] = "ia"
    assert valider(d, "recommandation_autonomie") != []


def test_rapport_pourcentage_hors_limites_refuse():
    d = charge("exemple_rapport.json")
    d["indicateurs"]["taches_terminees_pct"] = 140
    assert valider(d, "rapport") != []
