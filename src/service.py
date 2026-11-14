"""Service qui expose le module IA (API HTTP)."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .clarification import questions_clarification
from .conflits import detecter_conflits
from .decomposition import ErreurDecomposition, decomposer
from .modeles import modele_factice
from .planification import planifier
from .validation import valider

app = FastAPI(title="KPODA AI - module IA")
MODELE = modele_factice()  # à remplacer par le modèle retenu


class DemandeDecomposition(BaseModel):
    objectif: str = Field(min_length=3, max_length=500)


class DemandePlanification(BaseModel):
    taches: list[dict] = Field(min_length=1)
    disponibilites: list[dict] = Field(min_length=1)
    session_max: int = Field(default=90, ge=15, le=240)
    pause: int = Field(default=10, ge=0, le=60)
    max_minutes_jour: int = Field(default=360, ge=30, le=720)


class DemandeConflits(BaseModel):
    sessions: list[dict]
    max_minutes_jour: int = Field(default=360, ge=30, le=720)
    repos_minutes: int = Field(default=10, ge=0, le=60)


@app.get("/sante")
def sante():
    return {"statut": "ok"}


@app.post("/decomposer")
def decomposer_objectif(demande: DemandeDecomposition):
    try:
        return decomposer(demande.objectif, MODELE)
    except ErreurDecomposition as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/clarifier")
def clarifier(demande: DemandeDecomposition):
    """Questions à poser avant la décomposition (liste vide = objectif assez précis)."""
    return {"questions": questions_clarification(demande.objectif)}


@app.post("/planifier")
def planifier_taches(demande: DemandePlanification):
    """Planning proposé (statut « en_attente_de_validation », jamais appliqué sans validation)."""
    try:
        planning = planifier(demande.taches, demande.disponibilites, demande.session_max,
                             demande.pause, demande.max_minutes_jour)
    except (KeyError, ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"données invalides : {e}")
    erreurs = valider(planning, "planification")
    if erreurs:
        raise HTTPException(status_code=500, detail="; ".join(erreurs))
    return planning


@app.post("/conflits")
def conflits(demande: DemandeConflits):
    try:
        return {"conflits": detecter_conflits(demande.sessions, demande.max_minutes_jour,
                                              demande.repos_minutes)}
    except (KeyError, ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"données invalides : {e}")
