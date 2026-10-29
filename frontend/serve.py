#!/usr/bin/env python3
"""
Dev server: static frontend + reverse proxy to FastAPI (avoids CORS without changing API code).

Usage (from repo root):
  uv run uvicorn API.main:app --host 127.0.0.1 --port 8000
  uv run python frontend/serve.py

Then open http://127.0.0.1:8080
"""

from __future__ import annotations

import http.server
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import load_env

load_env()

FRONTEND_DIR_ENV = os.getenv("FRONTEND_DIR", "frontend")
FRONTEND_DIR_PATH = Path(FRONTEND_DIR_ENV)
FRONTEND_DIR = (
    FRONTEND_DIR_PATH if FRONTEND_DIR_PATH.is_absolute() else REPO_ROOT / FRONTEND_DIR_PATH
).resolve()

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")
API_ORIGIN = f"http://{API_HOST}:{API_PORT}"
LISTEN = (
    os.getenv("FRONTEND_HOST", "127.0.0.1"),
    int(os.getenv("FRONTEND_PORT", "8080")),
)

PROXY_PREFIXES = (
    "/exercise/",
    "/upload",
    "/score/",
    "/scores/",
    "/transcription/",
    "/audio/",
    "/health",
)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_GET(self):
        if self._should_proxy():
            self._proxy()
        else:
            super().do_GET()

    def do_POST(self):
        if self._should_proxy():
            self._proxy()
        else:
            self.send_error(405)

    def _should_proxy(self) -> bool:
        path = self.path.split("?", 1)[0]
        return any(path.startswith(p) for p in PROXY_PREFIXES)

    def _proxy(self):
        url = f"{API_ORIGIN}{self.path}"
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else None

        headers = {}
        for key in ("Content-Type",):
            if key in self.headers:
                headers[key] = self.headers[key]

        req = urllib.request.Request(
            url, data=body, headers=headers, method=self.command
        )
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = resp.read()
                self.send_response(resp.status)
                for hk, hv in resp.headers.items():
                    if hk.lower() in ("transfer-encoding", "connection"):
                        continue
                    self.send_header(hk, hv)
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "application/json"))
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.URLError as e:
            payload = json.dumps({"detail": f"API unreachable: {e.reason}"}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)


if __name__ == "__main__":
    httpd = http.server.HTTPServer(LISTEN, Handler)
    print(f"Serving frontend at http://{LISTEN[0]}:{LISTEN[1]}")
    print(f"Proxying API paths to {API_ORIGIN}")
    httpd.serve_forever()
