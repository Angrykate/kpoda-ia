"""Squelette du service qui exposera le module (API HTTP)."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .decomposition import ErreurDecomposition, decomposer
from .modeles import modele_factice

app = FastAPI(title="KPODA AI - module IA")
MODELE = modele_factice()  # à remplacer par le modèle retenu


class DemandeDecomposition(BaseModel):
    objectif: str = Field(min_length=3, max_length=500)


@app.get("/sante")
def sante():
    return {"statut": "ok"}


@app.post("/decomposer")
def decomposer_objectif(demande: DemandeDecomposition):
    try:
        return decomposer(demande.objectif, MODELE)
    except ErreurDecomposition as e:
        raise HTTPException(status_code=502, detail=str(e))
