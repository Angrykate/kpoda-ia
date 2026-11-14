"""Jeu de données synthétiques (tâche 2.1).

Données entièrement inventées : aucune personne réelle. Trois profils types :
  - regulier   : travaille souvent aux mêmes heures, termine presque tout ;
  - irregulier : horaires variables, reporte souvent ;
  - surcharge  : beaucoup de tâches, sessions qui se chevauchent, abandons.

Les NOMS DE CHAMPS sont PROVISOIRES : ils seront alignés sur le modèle de
données du Membre 2. Pour les changer, modifier les listes CHAMPS_* ci-dessous.

    python -m src.donnees_synthetiques --sortie data/synthetique --semaines 6 --graine 42
"""
import argparse
import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

CHAMPS_UTILISATEURS = ["id", "profil", "date_debut"]
CHAMPS_TACHES = ["id", "utilisateur_id", "titre", "priorite", "duree_minutes",
                 "echeance", "statut", "semaine"]
CHAMPS_SESSIONS = ["id", "tache_id", "utilisateur_id", "debut", "fin", "statut",
                   "duree_prevue_min", "duree_reelle_min"]
CHAMPS_REPORTS = ["id", "tache_id", "utilisateur_id", "ancienne_date", "nouvelle_date", "motif"]

PROFILS = {
    #            tâches/sem  p_terminee  p_report  créneau (début, fin)  p_chevauchement
    "regulier":   {"n": 6,  "p_ok": 0.90, "p_report": 0.60, "heures": (17, 19), "p_chev": 0.00},
    "irregulier": {"n": 6,  "p_ok": 0.60, "p_report": 0.60, "heures": (8, 21),  "p_chev": 0.03},
    "surcharge":  {"n": 12, "p_ok": 0.45, "p_report": 0.50, "heures": (17, 22), "p_chev": 0.20},
}
TITRES = ["Réviser un chapitre", "Faire des exercices", "Rédiger un compte rendu", "Lire un article",
          "Préparer un exposé", "Relire ses notes", "Travailler un projet", "Faire un quiz",
          "Organiser ses fiches", "Revoir une correction"]
MOTIFS = ["fatigue", "imprévu", "surcharge", "oubli", "autre"]
DUREES = [30, 45, 60, 90, 120]


def generer(graine=42, semaines=6, par_profil=3, debut="2026-09-07"):
    """Retourne un dictionnaire de listes : utilisateurs, taches, sessions, reports."""
    rng = random.Random(graine)
    lundi = date.fromisoformat(debut)
    d = {"utilisateurs": [], "taches": [], "sessions": [], "reports": []}
    n_t = n_s = n_r = 0

    def ajoute_session(tache, utilisateur, jour, p, statut_force=None):
        nonlocal n_s
        h0, h1 = p["heures"]
        heure = rng.randint(h0, max(h0, h1 - 1))
        minute = rng.choice([0, 15, 30, 45])
        debut_s = datetime(jour.year, jour.month, jour.day, heure, minute)
        prevue = tache["duree_minutes"]
        statut = statut_force
        if statut == "terminee":
            reelle = int(prevue * rng.uniform(0.8, 1.1))
        elif statut == "interrompue":
            reelle = int(prevue * rng.uniform(0.3, 0.7))
        else:
            reelle = 0
        n_s += 1
        d["sessions"].append({
            "id": f"S{n_s:04d}", "tache_id": tache["id"], "utilisateur_id": utilisateur,
            "debut": debut_s.isoformat(timespec="minutes"),
            "fin": (debut_s + timedelta(minutes=prevue)).isoformat(timespec="minutes"),
            "statut": statut, "duree_prevue_min": prevue, "duree_reelle_min": reelle})
        return debut_s

    for profil, p in PROFILS.items():
        for k in range(1, par_profil + 1):
            uid = f"{profil}_{k:02d}"
            d["utilisateurs"].append({"id": uid, "profil": profil, "date_debut": lundi.isoformat()})
            for w in range(semaines):
                debut_sem = lundi + timedelta(weeks=w)
                for _ in range(max(2, p["n"] + rng.randint(-2, 2))):
                    n_t += 1
                    jour_ech = debut_sem + timedelta(days=rng.randint(1, 6))
                    tache = {"id": f"T{n_t:04d}", "utilisateur_id": uid,
                             "titre": rng.choice(TITRES),
                             "priorite": rng.choices(["haute", "moyenne", "basse"], [3, 4, 3])[0],
                             "duree_minutes": rng.choice(DUREES), "echeance": jour_ech.isoformat(),
                             "statut": "a_faire", "semaine": w + 1}
                    jour_prevu = max(debut_sem, jour_ech - timedelta(days=rng.randint(0, 2)))
                    if rng.random() < p["p_chev"] and d["sessions"]:
                        # chevauchement volontaire avec une session récente du même utilisateur
                        recents = [s for s in d["sessions"][-8:] if s["utilisateur_id"] == uid]
                        if recents:
                            cible = rng.choice(recents)
                            tache["duree_minutes"] = min(tache["duree_minutes"], 60)
                            deb = datetime.fromisoformat(cible["debut"]) + timedelta(minutes=15)
                            jour_prevu = deb.date()
                    if rng.random() < p["p_ok"]:
                        ajoute_session(tache, uid, jour_prevu, p, "terminee")
                        tache["statut"] = "terminee"
                    else:
                        if rng.random() < p["p_report"]:
                            ajoute_session(tache, uid, jour_prevu, p, "manquee")
                            nouvelle = jour_prevu + timedelta(days=rng.randint(1, 3))
                            n_r += 1
                            d["reports"].append({
                                "id": f"R{n_r:04d}", "tache_id": tache["id"], "utilisateur_id": uid,
                                "ancienne_date": jour_prevu.isoformat(), "nouvelle_date": nouvelle.isoformat(),
                                "motif": rng.choice(MOTIFS)})
                            if rng.random() < 0.6:
                                ajoute_session(tache, uid, nouvelle, p, "terminee")
                                tache["statut"] = "terminee"
                            else:
                                tache["statut"] = "abandonnee" if rng.random() < 0.4 else "a_faire"
                        else:
                            ajoute_session(tache, uid, jour_prevu, p, "interrompue")
                            tache["statut"] = "a_faire"
                    d["taches"].append(tache)
    return d


def ecrire(donnees, dossier):
    """Écrit un fichier CSV par table et un fichier JSON unique."""
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    champs = {"utilisateurs": CHAMPS_UTILISATEURS, "taches": CHAMPS_TACHES,
              "sessions": CHAMPS_SESSIONS, "reports": CHAMPS_REPORTS}
    for nom, lignes in donnees.items():
        with open(dossier / f"{nom}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=champs[nom])
            w.writeheader()
            w.writerows(lignes)
    (dossier / "jeu_donnees.json").write_text(
        json.dumps(donnees, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sortie", default="data/synthetique")
    ap.add_argument("--semaines", type=int, default=6)
    ap.add_argument("--par-profil", type=int, default=3)
    ap.add_argument("--graine", type=int, default=42)
    a = ap.parse_args()
    jeu = generer(a.graine, a.semaines, a.par_profil)
    ecrire(jeu, a.sortie)
    print({k: len(v) for k, v in jeu.items()}, "->", a.sortie)
