import numpy as np
from pydantic import BaseModel
from dataclasses import dataclass


# Responses
class DictionExercise(BaseModel):
    id: int
    nazwa: str
    typ: str
    trudnosc: str
    fokus: list[str]
    tekst: str
    wskazowka: str



# Data classes
@dataclass
class Audio:
    id:str
    y: np.ndarray
    sample_rate: int
    reference:str

class Score(BaseModel):
    id:str
    confidence: float
    cer_score: float
    rms_stability: float
    zcr_score: float
    spectral_centroid_score: float
    speaking_rate_wpm: float
    speaking_rate_score: float

class Transcription(BaseModel):
    reference: str
    transcription: str