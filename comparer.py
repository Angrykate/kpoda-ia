"""Compare un modèle sur trois objectifs et écrit un tableau prêt à coller dans la note 1.1.

Exemples :
    python comparer.py llama3.2
    python comparer.py llama3.2 prompts/decomposition_v1.txt
    python comparer.py --simule            # test hors connexion, sans vrai modèle
"""
import json
import sys
import time
from pathlib import Path

from src import decomposition
from src.decomposition import ErreurDecomposition, decomposer
from src.modeles import modele_factice, modele_ollama

OBJECTIFS = [
    "Préparer l'examen de statistiques",
    "Trouver un stage de deux mois",
    "Reprendre une activité physique régulière",
]


def compter(modele):
    """Enveloppe un modèle pour compter ses appels (= nombre de tentatives)."""
    etat = {"appels": 0}

    def appeler(prompt):
        etat["appels"] += 1
        return modele(prompt)

    return appeler, etat


def main():
    args = sys.argv[1:]
    simule = "--simule" in args
    args = [a for a in args if a != "--simule"]
    if simule:
        nom, chemin_prompt = "simule", (args[0] if args else None)
    else:
        nom = args[0] if args else "llama3.2"
        chemin_prompt = args[1] if len(args) > 1 else None
    if chemin_prompt:
        decomposition.PROMPT = Path(chemin_prompt)
    prompt_nom = decomposition.PROMPT.name

    sortie = Path("resultats")
    sortie.mkdir(exist_ok=True)
    base = f"{nom.replace(':', '_')}_{prompt_nom.replace('.txt', '')}"
    lignes = []
    for i, objectif in enumerate(OBJECTIFS, 1):
        modele = modele_factice() if simule else modele_ollama(nom)
        modele, etat = compter(modele)
        debut = time.time()
        try:
            plan = decomposer(objectif, modele)
            (sortie / f"{base}_plan{i}.json").write_text(
                json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
            etapes = len(plan["etapes"])
            taches = sum(len(e["taches"]) for e in plan["etapes"])
            resultat = ("oui", etapes, taches)
        except ErreurDecomposition:
            resultat = ("non", 0, 0)
        duree = round(time.time() - debut)
        lignes.append((objectif, resultat[0], etat["appels"], duree, resultat[1], resultat[2]))
        print(f"{objectif} -> valide : {resultat[0]}, tentatives : {etat['appels']}, "
              f"{duree} s, {resultat[1]} étape(s), {resultat[2]} tâche(s)")

    tableau = [f"Modèle : {nom} | Prompt : {prompt_nom}", "",
               "| Objectif | JSON valide | Tentatives | Temps (s) | Étapes | Tâches | Qualité (1-5) |",
               "|---|---|---|---|---|---|---|"]
    tableau += [f"| {o} | {v} | {t} | {d} | {e} | {k} | |" for o, v, t, d, e, k in lignes]
    fichier = sortie / f"{base}.md"
    fichier.write_text("\n".join(tableau) + "\n", encoding="utf-8")
    print(f"\nTableau enregistré dans {fichier}")


if __name__ == "__main__":
    main()
