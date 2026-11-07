"""Modèles interchangeables : une fonction qui prend un texte et renvoie un texte.

Le reste du code ne sait pas quel modèle est derrière. Quand le choix est fait
(tâche 1.1), on ajoute ici une fonction pour le modèle retenu, par exemple :

    def modele_retenu(prompt: str) -> str:
        ...  # appel à l'API ou au modèle local, renvoie le texte de la réponse
"""
import json


def modele_factice():
    """Modèle simulé pour tester hors connexion : 1re réponse invalide, 2e valide."""
    etat = {"appels": 0}

    def appeler(prompt: str) -> str:
        etat["appels"] += 1
        if etat["appels"] == 1:
            return "Voici le plan : (texte libre, pas du JSON)"
        plan = {
            "objectif": "Objectif de démonstration",
            "statut_proposition": "propose",
            "echeance": None,
            "hypotheses": ["Plan généré par le modèle simulé"],
            "etapes": [{
                "id": "E1", "titre": "Première étape",
                "indicateur_progression": "Tâches terminées",
                "taches": [{"id": "T1", "titre": "Première tâche", "duree_minutes": 30,
                            "priorite": "haute", "echeance": None, "statut": "a_faire"}],
            }],
        }
        return json.dumps(plan, ensure_ascii=False)

    return appeler
