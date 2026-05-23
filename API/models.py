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
