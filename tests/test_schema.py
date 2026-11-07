import json
from pathlib import Path

import pytest

from src.validation import valider

DATA = Path(__file__).resolve().parent.parent / "data"
EXEMPLES = sorted(DATA.glob("exemple_*.json"))


def charger(chemin):
    return json.loads(chemin.read_text(encoding="utf-8"))


def test_trois_exemples_presents():
    assert len(EXEMPLES) == 3


@pytest.mark.parametrize("chemin", EXEMPLES, ids=lambda p: p.name)
def test_exemple_valide(chemin):
    assert valider(charger(chemin)) == []


def test_priorite_inconnue_refusee():
    d = charger(EXEMPLES[0])
    d["etapes"][0]["taches"][0]["priorite"] = "urgente"
    assert valider(d) != []


def test_duree_hors_limites_refusee():
    d = charger(EXEMPLES[0])
    d["etapes"][0]["taches"][0]["duree_minutes"] = 1000
    assert valider(d) != []


def test_date_invalide_refusee():
    d = charger(EXEMPLES[0])
    d["etapes"][0]["taches"][0]["echeance"] = "demain"
    assert valider(d) != []


def test_id_en_double_refuse():
    d = charger(EXEMPLES[0])
    d["etapes"][1]["taches"][0]["id"] = "T1"
    assert any("double" in e for e in valider(d))


def test_dependance_inconnue_refusee():
    d = charger(EXEMPLES[0])
    d["etapes"][0]["taches"][0]["depend_de"] = ["T99"]
    assert any("T99" in e for e in valider(d))
