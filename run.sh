#!/bin/bash
# Run the offline document intelligence system (Linux/Mac)
set -e

# Ensure data directories exist
mkdir -p data/documents

# Build index if needed
if [ ! -f data/faiss.index ] || [ ! -f data/chunks.pkl ]; then
  echo "No FAISS index found. Building index..."
  python3 src/embed.py
else
  echo "FAISS index found. Skipping embedding."
fi

# Start Flask app
cd src
export FLASK_ENV=development
python3 app.py
