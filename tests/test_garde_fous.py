import pytest

from src.decomposition import ErreurDecomposition, decomposer
from src.garde_fous import controler_sortie, verifier_texte
from src.modeles import modele_factice

INTERDITS = [
    "J’ai déplacé votre planning à demain.",
    "J'ai modifié la règle de limite d'écran.",
    "Votre planning a été mis à jour.",
    "La restriction est maintenant activée.",
    "C'est fait, tout est appliqué.",
    "Il est certain que tu réussiras ton examen.",
    "Résultat garanti en deux semaines.",
]
AUTORISES = [
    "Je te propose de déplacer la tâche à demain, si tu es d'accord.",
    "Il est possible que tu aies besoin de plus de temps.",
    "Appliquer la formule de variance.",
    "Hypothèse : environ 30 minutes disponibles par jour.",
    "Relire le chapitre sur les probabilités.",
]


@pytest.mark.parametrize("texte", INTERDITS)
def test_phrases_interdites_detectees(texte):
    assert verifier_texte(texte) != []


@pytest.mark.parametrize("texte", AUTORISES)
def test_phrases_normales_acceptees(texte):
    assert verifier_texte(texte) == []


def test_controle_recursif_avec_chemin():
    sortie = {"hypotheses": ["Il est certain que ça marche"], "etapes": [{"titre": "ok"}]}
    v = controler_sortie(sortie)
    assert v and v[0]["chemin"] == "sortie.hypotheses[0]"


def _plan(hypothese):
    return {"objectif": "Objectif test", "statut_proposition": "propose", "echeance": None,
            "hypotheses": [hypothese],
            "etapes": [{"id": "E1", "titre": "Étape", "indicateur_progression": "Tâches faites",
                        "taches": [{"id": "T1", "titre": "Tâche", "duree_minutes": 30, "priorite": "haute",
                                    "echeance": None, "statut": "a_faire"}]}]}


def test_decomposer_refuse_puis_accepte():
    import json
    reponses = iter([json.dumps(_plan("J'ai déjà modifié votre planning")),
                     json.dumps(_plan("Environ 30 minutes par jour"))])
    plan = decomposer("Préparer un examen", lambda p: next(reponses))
    assert plan["hypotheses"] == ["Environ 30 minutes par jour"]


def test_decomposer_echoue_si_toujours_interdit():
    import json
    with pytest.raises(ErreurDecomposition):
        decomposer("Préparer un examen", lambda p: json.dumps(_plan("J'ai modifié votre planning")),
                   max_tentatives=2)
