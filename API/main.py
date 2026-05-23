from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import os
from typing import Literal
import json
import random
import librosa
import io
import uuid

from API.models import DictionExercise, Audio
app = FastAPI()

# Text variables
path = os.path.join('API',"cwiczenia_dykcja.json" )
DATA_PATH = Path(path)
Trudnosc = Literal["łatwa", "średnia", "trudna", "bardzo trudna"]

# in-memory store: id -> audio data
audio_store = {}


# Getting Text

# Helper for getting text
def load_exercises() -> list[DictionExercise]:
    if not DATA_PATH.exists():
        raise HTTPException(status_code=500, detail=f"Plik {DATA_PATH} nie istnieje.")
    with DATA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return [DictionExercise(**item) for item in data["cwiczenia_dykcja"]]


@app.get("/exercise/random", response_model=DictionExercise)
def get_random_exercise(
        trudnosc: Trudnosc | None = Query(
            default=None,
            description="Filtruj po poziomie trudności: łatwa | średnia | trudna | bardzo trudna",
        )
):
    """Zwraca losowe ćwiczenie dykcji. Opcjonalnie filtruje po trudności."""
    exercises = load_exercises()

    if trudnosc is not None:
        exercises = [e for e in exercises if e.trudnosc == trudnosc]
        if not exercises:
            raise HTTPException(
                status_code=404,
                detail=f"Brak ćwiczeń o poziomie trudności '{trudnosc}'.",
            )

    return random.choice(exercises)

#TODO: Post Transcription Along with audio or in different endpoint (?)

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...), exercise_id: int = Form(...)):
    contents = await file.read()
    try:
        y, sr = librosa.load(io.BytesIO(contents), sr=None, mono=False)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


    exercises = load_exercises()
    exercise = exercises[exercise_id]

    audio_id = str(uuid.uuid4())
    audio_store[audio_id] = Audio(id=audio_id, y=y, sample_rate=int(sr), reference=exercise.tekst)

    return {"audio_id": audio_id}




# TODO: Design API endpoint and Return types

@app.get('/health')
def health():
    return {"status": "ok"}