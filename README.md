# GOS Analyzer

GOS Analyzer is designed to run locally using Ollama and Neo4j. After the initial setup and model downloads, the application can be used **without an internet connection**.

## Setup

### 1. Create a Python virtual environment

#### Windows

```bat
python -m venv .venv
.venv\Scripts\activate
```

#### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Ollama

Download and install Ollama from:

https://ollama.com/download

Download the required models:

```bash
ollama pull qwen3:4b-q4_K_M
ollama pull gemma3:4b
```

Make sure Ollama is running before starting GOS Analyzer.

### 3. Install Neo4j Desktop

Download and install Neo4j Desktop from:

https://neo4j.com/download/

Create a local Neo4j instance with:

```text
Username: neo4j
Password: 123456789
```

Start the Neo4j instance before running GOS Analyzer.

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-docs.txt
```

## Run GOS Analyzer

### Windows

```bat
run.bat
```

### macOS

```bash
bash run2.sh
```

## First-Time Setup

For the **first run**, keep the computer connected to the internet.

After the required resources and models have been downloaded and the initial setup is complete:

> **GOS Analyzer can be used offline.**

Make sure Ollama is installed, the required models are downloaded, and the Neo4j instance is running.

## Required Ollama Models

```text
qwen3:4b-q4_K_M
gemma3:4b
```

## Neo4j Credentials

```text
Username: neo4j
Password: 123456789
```

::: 
