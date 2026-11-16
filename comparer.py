"""Compare des modèles sur trois objectifs et écrit un tableau prêt à coller dans la note 1.1.

Exemples :
    python comparer.py llama3.2                          # modèle local (Ollama)
    python comparer.py qwen2.5:3b prompts/decomposition_v1.txt
    python comparer.py gemini:gemini-3.8-flash prompts/decomposition_v1.txt   # API Gemini
    python comparer.py --simule                          # test hors connexion
    python comparer.py --resume                          # tableau de synthèse de tous les essais
"""
import json
import sys
import time
from pathlib import Path

from src import decomposition
from src.decomposition import ErreurDecomposition, decomposer
from src.modeles import ErreurModele, modele_factice, modele_gemini, modele_ollama

OBJECTIFS = [
    "Préparer l'examen de statistiques",
    "Trouver un stage de deux mois",
    "Reprendre une activité physique régulière",
]
DOSSIER = Path("resultats")


def compter(modele):
    """Enveloppe un modèle pour compter ses appels (= nombre de tentatives)."""
    etat = {"appels": 0}

    def appeler(prompt):
        etat["appels"] += 1
        return modele(prompt)

    return appeler, etat


def choisir_modele(nom):
    if nom.startswith("gemini:"):
        return modele_gemini(nom.split(":", 1)[1])
    return modele_ollama(nom)


def lire_resultats(dossier=DOSSIER):
    """Relit les tableaux enregistrés. Retourne une liste de (modèle, consigne, lignes)."""
    essais = []
    for fichier in sorted(Path(dossier).glob("*.md")):
        if fichier.name == "comparaison.md":
            continue
        lignes = fichier.read_text(encoding="utf-8").splitlines()
        if not lignes or not lignes[0].startswith("Modèle :"):
            continue
        modele, consigne = [x.split(":", 1)[1].strip() for x in lignes[0].split("|")]
        lignes_tab = []
        for l in lignes:
            cases = [c.strip() for c in l.strip().strip("|").split("|")]
            if l.startswith("|") and len(cases) == 7 and cases[0] not in ("Objectif", "---"):
                lignes_tab.append(cases)
        essais.append((modele, consigne, lignes_tab))
    return essais


def synthese(essais):
    """Construit le tableau de comparaison de tous les essais."""
    sortie = ["| Modèle | Consigne | Valide dès la 1re tentative | Temps moyen (s) | Étapes (moy.) | Tâches (moy.) | Qualité (moy.) |",
              "|---|---|---|---|---|---|---|"]
    for modele, consigne, lignes in essais:
        n = len(lignes)
        ok = sum(1 for c in lignes if c[1] == "oui" and c[2] == "1")
        nombres = lambda i: [float(c[i]) for c in lignes if c[i].replace(".", "", 1).isdigit()]
        moy = lambda v: f"{sum(v) / len(v):.1f}" if v else "-"
        sortie.append(f"| {modele} | {consigne} | {ok} sur {n} | {moy(nombres(3))} | "
                      f"{moy(nombres(4))} | {moy(nombres(5))} | {moy(nombres(6))} |")
    return "\n".join(sortie)


def main():
    args = sys.argv[1:]
    if "--resume" in args:
        essais = lire_resultats()
        if not essais:
            print("Aucun résultat dans le dossier resultats/ : lancez d'abord comparer.py sur un modèle.")
            return
        tableau = synthese(essais)
        DOSSIER.mkdir(exist_ok=True)
        (DOSSIER / "comparaison.md").write_text(tableau + "\n", encoding="utf-8")
        print(tableau)
        print(f"\nTableau enregistré dans {DOSSIER / 'comparaison.md'}")
        return

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

    if not simule:
        try:
            choisir_modele(nom)                     # vérifie tout de suite la clé ou le nom
        except ErreurModele as e:
            print(f"Impossible de commencer : {e}")
            return

    DOSSIER.mkdir(exist_ok=True)
    base = f"{nom.replace(':', '_')}_{prompt_nom.replace('.txt', '')}"
    lignes = []
    for i, objectif in enumerate(OBJECTIFS, 1):
        modele = modele_factice() if simule else choisir_modele(nom)
        modele, etat = compter(modele)
        debut = time.time()
        try:
            plan = decomposer(objectif, modele)
            (DOSSIER / f"{base}_plan{i}.json").write_text(
                json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
            resultat = ("oui", len(plan["etapes"]), sum(len(e["taches"]) for e in plan["etapes"]))
        except ErreurDecomposition:
            resultat = ("non", 0, 0)
        except Exception as e:                      # connexion, clé, limite d'utilisation...
            print(f"{objectif} -> ERREUR : {e}")
            resultat = ("erreur", 0, 0)
        duree = round(time.time() - debut)
        lignes.append((objectif, resultat[0], etat["appels"], duree, resultat[1], resultat[2]))
        print(f"{objectif} -> valide : {resultat[0]}, tentatives : {etat['appels']}, "
              f"{duree} s, {resultat[1]} étape(s), {resultat[2]} tâche(s)")

    tableau = [f"Modèle : {nom} | Prompt : {prompt_nom}", "",
               "| Objectif | JSON valide | Tentatives | Temps (s) | Étapes | Tâches | Qualité (1-5) |",
               "|---|---|---|---|---|---|---|"]
    tableau += [f"| {o} | {v} | {t} | {d} | {e} | {k} | |" for o, v, t, d, e, k in lignes]
    fichier = DOSSIER / f"{base}.md"
    fichier.write_text("\n".join(tableau) + "\n", encoding="utf-8")
    print(f"\nTableau enregistré dans {fichier}")
    print("Remplissez la colonne « Qualité » dans ce fichier, puis lancez : python comparer.py --resume")


if __name__ == "__main__":
    main()
