import json

import pytest

from src.decomposition import ErreurDecomposition, decomposer, extraire_json
from src.confidentialite import donnees_identifiantes, masquer
from src.modeles import modele_factice


def test_nouvelle_tentative_apres_reponse_invalide():
    plan = decomposer("Préparer un examen", modele_factice())
    assert plan["statut_proposition"] == "propose"


def test_echec_apres_max_tentatives():
    with pytest.raises(ErreurDecomposition):
        decomposer("Préparer un examen", lambda p: "pas du json", max_tentatives=2)


def test_extraction_json_entoure_de_texte():
    assert extraire_json('Voici :\n```json\n{"a": 1}\n```') == {"a": 1}


def test_donnees_identifiantes_masquees_avant_envoi():
    vus = []

    def espion(prompt):
        vus.append(prompt)
        return modele_factice()(prompt)

    objectif = "Contacter jean@exemple.com ou +228 90 12 34 56"
    assert set(donnees_identifiantes(objectif)) == {"email", "telephone"}
    assert "jean@exemple.com" not in masquer(objectif)
    try:
        decomposer(objectif, espion, max_tentatives=1)
    except ErreurDecomposition:
        pass
    assert "jean@exemple.com" not in vus[0] and "90 12 34 56" not in vus[0]
