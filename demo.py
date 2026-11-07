"""Démonstration : décomposition de trois objectifs avec le modèle simulé.

    python demo.py
"""
import json

from src.decomposition import decomposer
from src.modeles import modele_factice

OBJECTIFS = [
    "Préparer l'examen de statistiques",
    "Trouver un stage de deux mois",
    "Reprendre une activité physique régulière",
]

for objectif in OBJECTIFS:
    plan = decomposer(objectif, modele_factice())  # un modèle neuf par objectif
    nb = sum(len(e["taches"]) for e in plan["etapes"])
    print(f"OK : {objectif} -> {len(plan['etapes'])} étape(s), {nb} tâche(s)")
print(json.dumps(plan, ensure_ascii=False, indent=2))
