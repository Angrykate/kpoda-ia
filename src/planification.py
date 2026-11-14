"""Génération d'un planning proposé (tâche 2.3).

Le planning est construit par des règles simples et vérifiables :
  - les tâches sont ordonnées par dépendances, puis par priorité, puis par échéance ;
  - chaque tâche est découpée en sessions de `session_max` minutes au plus ;
  - une pause de `pause` minutes sépare deux sessions ;
  - au plus `max_minutes_jour` minutes de travail par jour ;
  - rien n'est placé en dehors des créneaux de disponibilité fournis.

Le résultat porte toujours le statut « en_attente_de_validation » : il n'est
jamais appliqué sans validation de l'utilisateur.
"""
import heapq
from datetime import date, datetime, timedelta

from .conflits import detecter_conflits

RANG = {"haute": 0, "moyenne": 1, "basse": 2}
STATUTS_A_PLANIFIER = ("a_faire", "en_cours")


def _ordonner(taches):
    """Ordre topologique ; à égalité, priorité puis échéance puis ordre d'origine."""
    ids = {t["id"] for t in taches}
    attente = {t["id"]: {d for d in t.get("depend_de", []) if d in ids} for t in taches}
    index = {t["id"]: i for i, t in enumerate(taches)}
    par_id = {t["id"]: t for t in taches}

    def cle(t):
        ech = t.get("echeance") or "9999-12-31"
        return (RANG.get(t.get("priorite"), 1), ech, index[t["id"]], t["id"])

    pret = [cle(t) for t in taches if not attente[t["id"]]]
    heapq.heapify(pret)
    ordre, vus = [], set()
    while pret:
        tid = heapq.heappop(pret)[-1]
        ordre.append(par_id[tid])
        vus.add(tid)
        for autre, deps in attente.items():
            if tid in deps:
                deps.discard(tid)
                if not deps and autre not in vus and all(c[-1] != autre for c in pret):
                    heapq.heappush(pret, cle(par_id[autre]))
    restantes = [t for t in taches if t["id"] not in vus]
    return ordre, restantes


def planifier(taches, disponibilites, session_max=90, pause=10,
              max_minutes_jour=360, bloc_min=15):
    """Propose un planning. `disponibilites` : liste de {"debut", "fin"} (texte ISO)."""
    a_faire = [t for t in taches if t.get("statut", "a_faire") in STATUTS_A_PLANIFIER]
    ordre, circulaires = _ordonner(a_faire)
    creneaux = sorted(
        ([datetime.fromisoformat(c["debut"]), datetime.fromisoformat(c["fin"])] for c in disponibilites),
        key=lambda c: c[0])

    sessions, non_planifiees, avertissements = [], [], []
    place = {}          # id de tâche -> minutes restantes à planifier
    fin_tache = {}
    utilise = {}        # date -> minutes déjà planifiées
    curseur, ci = None, 0

    for t in circulaires:
        non_planifiees.append({"tache_id": t["id"], "reste_minutes": int(t["duree_minutes"]),
                               "raison": "dépendance circulaire ou impossible à résoudre"})

    for t in ordre:
        bloquees = [d for d in t.get("depend_de", [])
                    if d in place and place[d] > 0]
        if bloquees:
            non_planifiees.append({"tache_id": t["id"], "reste_minutes": int(t["duree_minutes"]),
                                   "raison": f"dépend de {', '.join(bloquees)}, non planifiée en entier"})
            place[t["id"]] = int(t["duree_minutes"])
            continue
        reste = int(t["duree_minutes"])
        premiere = None
        while reste > 0 and ci < len(creneaux):
            debut_c, fin_c = creneaux[ci]
            debut = max(debut_c, curseur) if curseur else debut_c
            dispo = int((fin_c - debut).total_seconds() // 60)
            jour = debut.date()
            reste_jour = max_minutes_jour - utilise.get(jour, 0)
            taille = min(reste, session_max, dispo, reste_jour)
            if taille < min(bloc_min, reste):
                ci += 1
                continue
            fin = debut + timedelta(minutes=taille)
            sessions.append({"id": f"S{len(sessions) + 1}", "tache_id": t["id"],
                             "debut": debut.isoformat(timespec="minutes"),
                             "fin": fin.isoformat(timespec="minutes")})
            utilise[jour] = utilise.get(jour, 0) + taille
            reste -= taille
            curseur = fin + timedelta(minutes=pause)
            fin_tache[t["id"]] = fin
            premiere = premiere or debut
        place[t["id"]] = reste
        if reste > 0:
            non_planifiees.append({"tache_id": t["id"], "reste_minutes": reste,
                                   "raison": "pas assez de créneaux disponibles"})
        elif t.get("echeance"):
            limite = date.fromisoformat(t["echeance"])
            if fin_tache[t["id"]].date() > limite:
                avertissements.append(
                    f"« {t.get('titre', t['id'])} » est planifiée le {fin_tache[t['id']]:%d/%m}, "
                    f"après son échéance du {limite:%d/%m}.")

    for c in detecter_conflits(sessions, max_minutes_jour=max_minutes_jour, repos_minutes=pause):
        avertissements.append(c["message"])

    return {"statut": "en_attente_de_validation", "sessions": sessions,
            "non_planifiees": non_planifiees, "avertissements": avertissements}
