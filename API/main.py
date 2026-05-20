from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import librosa
import io

app = FastAPI(
    title="Audio Sample Rate API",
    description="Upload an audio file and get its sample rate.",
    version="1.0.0",
)



# TODO: Create Endpoint for Posing Audio and Getting Scores (score function needed) - How to transfer CER visualisation ?


@app.post("/sample-rate")
async def get_sample_rate(file: UploadFile = File(...)):
    """
    This is mock endpoint to test files transfer via API

    Upload an audio file and receive its sample rate in Hz.

    Supported formats: WAV, FLAC, OGG, MP3, and other formats
    supported by librosa.
    """
    contents = await file.read()

    try:
        y, sample_rate = librosa.load(io.BytesIO(contents), sr=None, mono=False)
        channels = 1 if y.ndim == 1 else y.shape[0]
        frames = y.shape[-1]
        duration_seconds = librosa.get_duration(y=y, sr=sample_rate)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Could not read audio file: {str(e)}. "
                   "Make sure the file is a valid audio format (WAV, FLAC, OGG, MP3, etc.).",
        )

    return JSONResponse(content={
        "filename": file.filename,
        "sample_rate_hz": sample_rate,
        "channels": channels,
        "duration_seconds": round(duration_seconds, 3),
        "total_frames": frames,
    })


@app.get("/health")
def health():
    return {"status": "ok"}