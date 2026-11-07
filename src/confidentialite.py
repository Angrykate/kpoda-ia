"""Contrôle minimal : empêcher l'envoi de données identifiantes au fournisseur IA."""
import re

MOTIFS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "telephone": re.compile(r"(?<!\d)(?:\+?\d[\s.-]?){8,}(?!\d)"),
}


def donnees_identifiantes(texte):
    """Retourne les types de données identifiantes détectées dans le texte."""
    return [nom for nom, motif in MOTIFS.items() if motif.search(texte)]


def masquer(texte):
    """Remplace e-mails et numéros par des marqueurs avant envoi."""
    for nom, motif in MOTIFS.items():
        texte = motif.sub(f"[{nom} masqué]", texte)
    return texte
