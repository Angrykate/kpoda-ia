"""Garde-fous sur le texte produit par le modèle (tâche 2.5).

L'IA propose, l'humain valide. Le code refuse toute sortie qui :
  - prétend avoir modifié un planning, une règle ou une restriction ;
  - présente une hypothèse ou une prévision comme une certitude.
"""
import re
import unicodedata

VERBES = ("modifie|deplace|change|supprime|annule|applique|active|desactive|"
          "mis a jour|reporte|replanifie|ajoute|retire|bloque|debloque|valide|enregistre")

MOTIFS = [
    ("action_pretendue", re.compile(rf"\bj'ai (deja |bien |automatiquement )?({VERBES})")),
    ("action_pretendue", re.compile(rf"\b(le|ce|votre|ton|ta|la) (planning|programme|horaire|regle|restriction|limite|tache|session) "
                                    rf"(a ete|est maintenant|est desormais|vient d'etre) ({VERBES}|mis a jour|modifiee?|appliquee?|activee?)")),
    ("action_pretendue", re.compile(r"\b(c'est|voila,? c'est) (fait|applique|modifie|termine)\b")),
    ("certitude", re.compile(r"\b(il est certain|c'est certain|c'est sur|a coup sur|sans aucun doute|"
                             r"je garantis|garanti|vous reussirez|tu reussiras|vous allez reussir|tu vas reussir|"
                             r"il est evident que)\b")),
]


def _normaliser(texte):
    texte = texte.replace("’", "'").replace(" ", " ").lower()
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in texte if not unicodedata.combining(c))


def verifier_texte(texte, chemin="texte"):
    """Retourne la liste des violations trouvées dans un texte."""
    brut = _normaliser(texte)
    violations = []
    for type_, motif in MOTIFS:
        for m in motif.finditer(brut):
            violations.append({"type": type_, "extrait": m.group(0), "chemin": chemin})
    return violations


def controler_sortie(objet, chemin="sortie"):
    """Parcourt une sortie JSON (dict, liste, texte) et retourne toutes les violations."""
    if isinstance(objet, str):
        return verifier_texte(objet, chemin)
    violations = []
    if isinstance(objet, dict):
        for cle, valeur in objet.items():
            violations += controler_sortie(valeur, f"{chemin}.{cle}")
    elif isinstance(objet, list):
        for i, valeur in enumerate(objet):
            violations += controler_sortie(valeur, f"{chemin}[{i}]")
    return violations
