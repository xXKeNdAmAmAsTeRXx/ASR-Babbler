"""Entry point for the ASR Bubbler API."""

import os

import uvicorn

from config import load_env

load_env()


def main() -> None:
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "false").strip().lower() in {"1", "true", "yes", "on"}

    uvicorn.run("API.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()