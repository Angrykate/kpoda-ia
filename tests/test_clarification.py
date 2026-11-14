import pytest

from src.clarification import questions_clarification

VAGUES = ["Apprendre l'anglais", "Préparer l'examen de statistiques", "Faire du sport", "Réussir"]
PRECIS = ["Réviser 3 chapitres de statistiques d'ici vendredi",
          "Finir mon rapport avant le 20/11 en 2 heures par jour",
          "Courir 5 km trois fois par semaine pendant un mois, dès lundi"]


@pytest.mark.parametrize("o", VAGUES)
def test_objectif_vague_pose_des_questions(o):
    q = questions_clarification(o)
    assert 1 <= len(q) <= 3


@pytest.mark.parametrize("o", PRECIS)
def test_objectif_precis_sans_question(o):
    assert questions_clarification(o) == []


def test_une_seule_info_manquante():
    q = questions_clarification("Réviser 3 chapitres de statistiques")
    assert len(q) == 2 and "Pour quand" in q[0]


def test_maximum_respecte():
    assert len(questions_clarification("Réussir", max_questions=2)) == 2
