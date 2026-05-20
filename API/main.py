from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import librosa
import io
import uuid

app = FastAPI()

# TODO: Create class for storing audio along with metrics and transcription

# in-memory store: id -> audio data
audio_store = {}


#TODO: Post Transcription Along with audio or in different endpoint (?)

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        y, sr = librosa.load(io.BytesIO(contents), sr=None, mono=False)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    audio_id = str(uuid.uuid4())
    audio_store[audio_id] = {"y": y, "sr": sr, "filename": file.filename}

    return {"audio_id": audio_id}


# TODO: Create Core functions and use them in API endpoints
# TODO: Design API endpoint and Return types

@app.get("/transcription/{audio_id}")
def get_transcription(audio_id: str):
    #TODO: get audio transcription
    pass

@app.get("/reports/{audio_id}")
def get_report(audio_id: str):
    #TODO: get full audio report (diction scores)
    pass

@app.post("/cer/{audio_id}")
def get_cert(audio_id: str):
    #TODO: get CER vizualizations
    pass

@app.get("/sample-rate/{audio_id}")
def get_sample_rate(audio_id: str):
    audio = _get_or_404(audio_id)
    return {"sample_rate_hz": audio["sr"]}



@app.get("/duration/{audio_id}")
def get_duration(audio_id: str):
    audio = _get_or_404(audio_id)
    duration = librosa.get_duration(y=audio["y"], sr=audio["sr"])
    return {"duration_seconds": round(duration, 3)}


def _get_or_404(audio_id: str):
    if audio_id not in audio_store:
        raise HTTPException(status_code=404, detail="Audio ID not found")
    return audio_store[audio_id]