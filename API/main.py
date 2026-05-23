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

from nemo.collections.asr.parts.mixins import transcription

from API.models import DictionExercise, Audio, Score, Transcription
from API.utils.load_asr_model import load_asr_model
from API.report import report as make_report
app = FastAPI()

# ASR model
asr_model = load_asr_model()

# Text variables
path = os.path.join('API',"cwiczenia_dykcja.json" )
DATA_PATH = Path(path)
Trudnosc = Literal["łatwa", "średnia", "trudna", "bardzo trudna"]

# in-memory store:
#   id -> audio data
#   id -> Score data
audio_store = {}
score_store = {}
cer_visualisation_store = {}
transcriptions = {}

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
    """Return random exercise with option to choose difficulty"""
    exercises = load_exercises()

    if trudnosc is not None:
        exercises = [e for e in exercises if e.trudnosc == trudnosc]
        if not exercises:
            raise HTTPException(
                status_code=404,
                detail=f"Brak ćwiczeń o poziomie trudności '{trudnosc}'.",
            )

    return random.choice(exercises)

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...), exercise_id: int = Form(...)):
    """Upload audio file along with exercise id, adds audio along with reference transcription to audio_store"""
    contents = await file.read()
    try:
        y, sr = librosa.load(io.BytesIO(contents), sr=None, mono=False)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


    # Storing Audio
    exercises = load_exercises()
    exercise = exercises[exercise_id]

    audio_id = str(uuid.uuid4())
    audio_store[audio_id] = Audio(id=audio_id, y=y, sample_rate=int(sr), reference=exercise.tekst)

    #Storing Scores
    hyp = asr_model.transcribe([y], return_hypotheses=True)[0][0]
    report, cer_vis = make_report(ref=exercise.tekst, hyp=hyp, audio=y, sr=int(sr))
    score = Score(id=audio_id, **report)
    score_store[audio_id] = score
    cer_visualisation_store[audio_id] = cer_vis

    #Transcription
    transcriptions[audio_id] = Transcription(reference=exercise.tekst, transcription=hyp.text)

    return {"audio_id": audio_id}




# Get Endpoints
@app.get("/score/{audio_id}")
def get_score(audio_id: str) -> Score:
    """Get report with all scores"""
    return score_store[audio_id]

@app.get("/score/cer_vis/{audio_id}")
def get_cer_vis(audio_id: str) -> str:
    """Get html with CER vizualization"""
    return cer_visualisation_store[audio_id]

@app.get("/transcription/{audio_id}")
def get_transcription(audio_id: str) -> Transcription:
    """Get Transcription and Reference text"""
    return transcriptions[audio_id]


@app.get('/health')
def health():
    return {"status": "ok"}