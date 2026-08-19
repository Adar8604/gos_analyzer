#!/bin/bash

echo "Starting GOS Analyser"

# Initialize conda
source "$(conda info --base)/etc/profile.d/conda.sh"

# Activate the environment
conda activate /Users/adarshkumar/Desktop/gos_analyzer/venv

# Go to the project directory
cd /Users/adarshkumar/Desktop/gos_analyzer

# --------------------------------------------------
# Force Hugging Face / Transformers to work offline
# Models must already exist in the local cache.
# --------------------------------------------------
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

echo "Hugging Face offline mode enabled"

# Run Streamlit
streamlit run frontend/app.py --server.port 8502 &

# Run MkDocs
mkdocs serve --dev-addr 127.0.0.1:8503 --open &

echo "GOS Analyser started"
echo "Streamlit: http://localhost:8502"
echo "MkDocs:    http://127.0.0.1:8503"

echo "Press Enter to exit..."
read