"""Décomposition d'un objectif : prompt, appel du modèle, validation, nouvelle tentative."""
import json
import re
from pathlib import Path

from .confidentialite import donnees_identifiantes, masquer
from .garde_fous import controler_sortie
from .validation import valider

PROMPT = (Path(__file__).resolve().parent.parent / "prompts" / "decomposition_v1.txt")


class ErreurDecomposition(Exception):
    pass


def extraire_json(texte):
    """Extrait un objet JSON d'une réponse, même entourée de texte ou de ```."""
    texte = re.sub(r"```(?:json)?", "", texte)
    debut, fin = texte.find("{"), texte.rfind("}")
    if debut == -1 or fin == -1:
        raise ValueError("aucun objet JSON trouvé")
    return json.loads(texte[debut:fin + 1])


def decomposer(objectif, modele, max_tentatives=3):
    """Retourne un plan validé, ou lève ErreurDecomposition.

    `modele` est une fonction texte -> texte. Les données identifiantes sont
    masquées avant l'envoi. En cas de réponse invalide, on réessaie en
    indiquant l'erreur au modèle.
    """
    if donnees_identifiantes(objectif):
        objectif = masquer(objectif)
    prompt = PROMPT.read_text(encoding="utf-8").replace("{objectif}", objectif)
    derniere_erreur = "aucune réponse"
    for tentative in range(1, max_tentatives + 1):
        reponse = modele(prompt)
        try:
            plan = extraire_json(reponse)
        except ValueError as e:
            derniere_erreur = f"JSON illisible : {e}"
        else:
            erreurs = valider(plan)
            if not erreurs:
                violations = controler_sortie(plan)
                if not violations:
                    return plan
                derniere_erreur = ("affirmation interdite : "
                                   + "; ".join(f"« {v['extrait']} » ({v['chemin']})" for v in violations[:3]))
            else:
                derniere_erreur = "; ".join(erreurs[:5])
        prompt += (f"\n\nTa réponse précédente était invalide ({derniere_erreur}). "
                   "Corrige-la et réponds uniquement par le JSON.")
    raise ErreurDecomposition(f"échec après {max_tentatives} tentatives : {derniere_erreur}")
