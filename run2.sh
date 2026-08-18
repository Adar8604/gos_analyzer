#!/bin/bash

echo "Starting GOS Analyser"

# Initialize conda
source "$(conda info --base)/etc/profile.d/conda.sh"

# Activate the environment
conda activate /Users/adarshkumar/Desktop/gos_analyzer/venv

# Go to the project directory
cd /Users/adarshkumar/Desktop/gos_analyzer

# Run Streamlit
streamlit run frontend/app.py --server.port 8502 &

# Run MkDocs
mkdocs serve --dev-addr 127.0.0.1:8503 --open &

echo "Press Enter to exit..."
read