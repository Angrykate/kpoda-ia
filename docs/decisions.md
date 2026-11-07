# Décisions

| Date | Décision | Raison |
|---|---|---|
| 2026-11-06 | Sortie de l'IA en JSON validé par schéma | Contrat clair avec les autres modules |
| 2026-11-06 | `statut_proposition` toujours « propose » | L'IA propose, l'humain valide |
| 2026-11-06 | Durée d'une tâche : 5 à 480 minutes | Éviter les tâches irréalistes |
| 2026-11-06 | Modèle appelé via une fonction texte → texte | Changer de modèle sans toucher au reste |
| 2026-11-06 | Échéance à `null` si inconnue | Ne pas inventer de dates |

## À valider avec les Membres 1 et 2 (au plus tard à J5)
- Noms des champs communs (statuts des tâches : `a_faire`, `en_cours`, `terminee`, `abandonnee`).
- Format des dates (AAAA-MM-JJ) et des durées (minutes).
- Identifiants : texte `E1`/`T1`, ou numériques côté base de données.
