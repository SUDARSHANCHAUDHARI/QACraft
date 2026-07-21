#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
host = "127.0.0.1"
port = 8000
print(f"Serving QA Everyday Skill Pack at http://{host}:{port}/docs/index.html")
ThreadingHTTPServer((host, port), SimpleHTTPRequestHandler).serve_forever()
