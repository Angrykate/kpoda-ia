# Semaine 2 — Récapitulatif

| Tâche | Livrable | Fichiers principaux |
|---|---|---|
| 2.1 | Jeu de données synthétiques (champs provisoires) | `src/donnees_synthetiques.py`, `data/synthetique/`, `docs/2.1_jeu_donnees.md` |
| 2.2 | Questions de clarification | `src/clarification.py`, `prompts/clarification.txt`, `docs/2.2_questions_clarification.md` |
| 2.3 | Génération de planning | `src/planification.py`, `POST /planifier` |
| 2.4 | Détection des conflits | `src/conflits.py`, `POST /conflits` |
| 2.5 | Garde-fous | `src/garde_fous.py`, `prompts/garde_fous.txt` |
| 2.6 | Formats JSON complémentaires | `schemas/`, `data/formats_complementaires/` |

Points d'accès du service : `/decomposer`, `/clarifier`, `/planifier`, `/conflits`, `/sante`.
Lancement : `uvicorn src.service:app --reload`, puis http://127.0.0.1:8000/docs.

## En attente
- Noms de champs du Membre 2 et format d'injection du Membre 1 (2.1).
- Validation des formats complémentaires par les Membres 1 et 2 (2.6).
- Modèle d'IA choisi : le service utilise encore le modèle simulé pour `/decomposer`.
