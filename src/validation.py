"""Validation des sorties JSON du module IA."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

RACINE = Path(__file__).resolve().parent.parent


def charger_schema(nom="decomposition"):
    chemin = RACINE / "schemas" / f"{nom}.schema.json"
    return json.loads(chemin.read_text(encoding="utf-8"))


def valider(donnees, nom="decomposition"):
    """Retourne la liste des erreurs (liste vide = JSON valide)."""
    validateur = Draft202012Validator(charger_schema(nom), format_checker=FormatChecker())
    erreurs = [f"{'/'.join(map(str, e.path)) or 'racine'} : {e.message}"
               for e in validateur.iter_errors(donnees)]
    if erreurs or nom != "decomposition":
        return erreurs
    return _verifier_coherence(donnees)


def _verifier_coherence(plan):
    """Règles que le schéma ne peut pas exprimer : ids uniques, dépendances connues."""
    erreurs, ids = [], []
    for etape in plan["etapes"]:
        ids += [t["id"] for t in etape["taches"]]
    doublons = {i for i in ids if ids.count(i) > 1}
    if doublons:
        erreurs.append(f"identifiants de tâches en double : {sorted(doublons)}")
    for etape in plan["etapes"]:
        for t in etape["taches"]:
            for dep in t.get("depend_de", []):
                if dep not in ids:
                    erreurs.append(f"{t['id']} dépend de {dep}, qui n'existe pas")
                if dep == t["id"]:
                    erreurs.append(f"{t['id']} dépend de lui-même")
    return erreurs
