@echo off
REM Run the offline document intelligence system (Windows)

REM Ensure data directories exist
if not exist data\documents mkdir data\documents

REM Build index if needed
if not exist data\faiss.index (
    echo No FAISS index found. Building index...
    python src\embed.py
) else if not exist data\chunks.pkl (
    echo No FAISS index found. Building index...
    python src\embed.py
) else (
    echo FAISS index found. Skipping embedding.
)

REM Start Flask app
cd src
set FLASK_ENV=development
python app.py
