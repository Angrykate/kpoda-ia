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


import urllib.request


def modele_ollama(nom="llama3.2", url="http://localhost:11434/api/generate", delai=900):
    """Appelle un modèle local via Ollama (adresse locale par défaut)."""
    def appeler(prompt: str) -> str:
        corps = json.dumps({"model": nom, "prompt": prompt, "stream": False,
                            "format": "json", "options": {"temperature": 0.2}}).encode("utf-8")
        requete = urllib.request.Request(url, data=corps,
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(requete, timeout=delai) as reponse:
            return json.loads(reponse.read().decode("utf-8"))["response"]
    return appeler



class ErreurModele(Exception):
    """Erreur lors de l'appel à un modèle (connexion, clé refusée, limite atteinte...)."""


def modele_gemini(nom, cle=None, delai=180,
                  url_base="https://generativelanguage.googleapis.com/v1beta"):
    """Appelle l'API Gemini (offre gratuite possible, limites à vérifier chez Google).

    La clé est lue dans la variable d'environnement GEMINI_API_KEY ou dans le fichier .env.
    `nom` est l'identifiant du modèle indiqué dans Google AI Studio, par exemple "gemini-3.8-flash".
    Seules des données synthétiques doivent être envoyées avec une clé gratuite.
    """
    import os
    import urllib.error
    if cle is None:
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        cle = os.environ.get("GEMINI_API_KEY")
    if not cle:
        raise ErreurModele("clé introuvable : ajoutez GEMINI_API_KEY=... dans le fichier .env")

    def appeler(prompt: str) -> str:
        corps = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {"maxOutputTokens": 4096}}).encode("utf-8")
        requete = urllib.request.Request(
            f"{url_base}/models/{nom}:generateContent", data=corps,
            headers={"Content-Type": "application/json", "x-goog-api-key": cle})
        try:
            with urllib.request.urlopen(requete, timeout=delai) as reponse:
                donnees = json.loads(reponse.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raisons = {400: "demande refusée (vérifiez le nom du modèle)",
                       403: "clé refusée ou accès interdit",
                       404: "modèle introuvable (vérifiez son nom dans AI Studio)",
                       429: "limite d'utilisation atteinte : attendez une minute et recommencez"}
            raise ErreurModele(f"erreur {e.code} : {raisons.get(e.code, 'erreur du service')}") from None
        except urllib.error.URLError as e:
            raise ErreurModele(f"connexion impossible : {e.reason}") from None
        try:
            return donnees["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise ErreurModele("réponse vide ou bloquée par le service") from None

    return appeler
