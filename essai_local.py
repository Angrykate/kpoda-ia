import json
import sys
import time

from src.decomposition import ErreurDecomposition, decomposer
from src.modeles import modele_ollama

nom = sys.argv[1] if len(sys.argv) > 1 else "llama3.2"
objectif = "Préparer l'examen de statistiques"

debut = time.time()
try:
    plan = decomposer(objectif, modele_ollama(nom))
    print("VALIDE en", round(time.time() - debut), "secondes")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
except ErreurDecomposition as e:
    print("ECHEC après", round(time.time() - debut), "secondes :", e)