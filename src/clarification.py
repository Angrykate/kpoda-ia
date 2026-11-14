"""Questions de clarification d'un objectif (tâche 2.2).

Règle : on pose une question seulement si une information utile à la
planification manque ; on s'abstient quand l'objectif est déjà assez précis.
Les questions sont posées une à la fois par l'application, trois au maximum.
"""
import re
import unicodedata

MOIS = "janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre"
JOURS = "lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|demain|apres-demain"

SIGNAL_ECHEANCE = re.compile(
    rf"\b(d'ici|avant|pour le|jusqu'au|dans \d+|en \d+ (jours?|semaines?|mois)|cette semaine|"
    rf"ce mois|la semaine|le mois|{JOURS}|\d{{1,2}} ({MOIS})|\d{{1,2}}/\d{{1,2}}|\b({MOIS})\b)")
SIGNAL_DISPONIBILITE = re.compile(
    r"\b(par jour|par semaine|chaque (jour|soir|matin|semaine)|tous les (jours|soirs|matins)|"
    r"\d+ ?(h|heures?|min|minutes?)\b)")

QUESTIONS = {
    "objectif": "Peux-tu préciser ce que tu veux obtenir exactement ?",
    "echeance": "Pour quand veux-tu y arriver ?",
    "disponibilite": "Combien de temps peux-tu y consacrer chaque jour ou chaque semaine ?",
    "reussite": "Qu'est-ce qui te montrerait que c'est réussi ?",
}


def _normaliser(texte):
    texte = texte.replace("’", "'").lower()
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in texte if not unicodedata.combining(c))


def questions_clarification(objectif, max_questions=3):
    """Retourne la liste des questions à poser (liste vide = objectif assez précis)."""
    t = _normaliser(objectif)
    a_echeance = bool(SIGNAL_ECHEANCE.search(t))
    a_dispo = bool(SIGNAL_DISPONIBILITE.search(t))
    a_mesure = bool(re.search(r"\d", t))

    if len(t.split()) < 3:
        return [QUESTIONS["objectif"], QUESTIONS["echeance"], QUESTIONS["disponibilite"]][:max_questions]
    if a_echeance and (a_dispo or a_mesure):
        return []                      # assez précis : on s'abstient
    questions = []
    if not a_echeance:
        questions.append(QUESTIONS["echeance"])
    if not a_dispo:
        questions.append(QUESTIONS["disponibilite"])
    if not a_mesure:
        questions.append(QUESTIONS["reussite"])
    return questions[:max_questions]
