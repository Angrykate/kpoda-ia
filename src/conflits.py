"""Détection des conflits et des programmes irréalistes (tâche 2.4).

Trois règles, vérifiées par du code et non par le modèle :
  - chevauchement : deux sessions se superposent ;
  - surcharge : trop de minutes de travail prévues dans une même journée ;
  - repos : moins de `repos_minutes` entre deux sessions de la même journée.
"""
from datetime import datetime


def _heure(dt):
    return f"{dt.hour} h {dt.minute:02d}"


def _duree(minutes):
    h, m = divmod(int(minutes), 60)
    return f"{h} h {m:02d}" if m else f"{h} h"


def detecter_conflits(sessions, max_minutes_jour=360, repos_minutes=10):
    """Retourne la liste des conflits (liste vide = programme réaliste).

    `sessions` : liste de dictionnaires avec `debut` et `fin` (texte ISO,
    par exemple "2026-11-16T17:00"), et si possible `id` et `titre`.
    """
    items = []
    for i, s in enumerate(sessions, 1):
        items.append({
            "id": s.get("id") or f"S{i}",
            "nom": s.get("titre") or s.get("tache_id") or s.get("id") or f"S{i}",
            "debut": datetime.fromisoformat(s["debut"]),
            "fin": datetime.fromisoformat(s["fin"]),
        })
    items.sort(key=lambda x: (x["debut"], x["fin"]))
    conflits = []

    # 1. chevauchement
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if b["debut"] >= a["fin"]:
                break
            conflits.append({
                "type": "chevauchement",
                "date": a["debut"].date().isoformat(),
                "sessions": [a["id"], b["id"]],
                "message": (f"Le {a['debut']:%d/%m}, « {a['nom']} » ({_heure(a['debut'])}-{_heure(a['fin'])}) "
                            f"et « {b['nom']} » ({_heure(b['debut'])}-{_heure(b['fin'])}) se chevauchent."),
            })

    # 2. surcharge horaire (durées cumulées sur une journée)
    par_jour = {}
    for s in items:
        par_jour.setdefault(s["debut"].date(), []).append(s)
    for jour, lot in sorted(par_jour.items()):
        total = sum((s["fin"] - s["debut"]).total_seconds() / 60 for s in lot)
        if total > max_minutes_jour:
            conflits.append({
                "type": "surcharge",
                "date": jour.isoformat(),
                "sessions": [s["id"] for s in lot],
                "message": (f"Le {jour:%d/%m}, {_duree(total)} de travail sont prévues, "
                            f"au-delà du maximum recommandé ({_duree(max_minutes_jour)})."),
            })

    # 3. repos insuffisant entre deux sessions consécutives
    for a, b in zip(items, items[1:]):
        ecart = (b["debut"] - a["fin"]).total_seconds() / 60
        if a["debut"].date() == b["debut"].date() and 0 <= ecart < repos_minutes:
            conflits.append({
                "type": "repos",
                "date": a["debut"].date().isoformat(),
                "sessions": [a["id"], b["id"]],
                "message": (f"Le {a['debut']:%d/%m}, il n'y a que {int(ecart)} min de repos entre "
                            f"« {a['nom']} » et « {b['nom']} » (minimum conseillé : {repos_minutes} min)."),
            })
    return sorted(conflits, key=lambda c: (c["date"], c["type"]))
