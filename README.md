# KPODA AI — Module IA et Big Data

Module IA de l'assistant KPODA AI : décomposition d'objectifs, aide à la
planification et indicateurs de suivi.

## Principes
- L'IA propose, l'humain valide.
- L'IA ne prétend jamais avoir modifié un plan.
- Les hypothèses sont signalées comme telles.
- Données synthétiques uniquement.

## Structure
- `schemas/` : schémas JSON des sorties de l'IA
- `src/` : code du module
- `tests/` : tests automatiques
- `data/` : exemples et données synthétiques
- `prompts/` : prompts versionnés
- `docs/` : notes (1.1, 1.2) et décisions

## Installation
    python -m venv .venv
    source .venv/bin/activate      # Windows : .venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env           # puis renseigner la clé

## Démonstration
    python demo.py

Le modèle est simulé tant que le choix n'est pas fait (voir `docs/1.1_comparaison_modeles.md`).

## Service
    uvicorn src.service:app --reload
    # http://127.0.0.1:8000/docs

## Tests
    pytest

## Auteur
Illane SIDIBE, Membre 3 (IA et Big Data).
