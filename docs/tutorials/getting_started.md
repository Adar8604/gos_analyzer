# GOS Analyzer — Getting Started

This guide explains how to set up the GOS Analyzer environment and run the application on Windows.

## 1. Prerequisites

Before starting, make sure the following are installed:

* Python 3.10 or later
* Ollama
* Neo4j Desktop

## 2. Create and Activate the Python Environment

Open **Command Prompt** or **PowerShell** in the GOS Analyzer project directory.

### Create the virtual environment

```bat
python -m venv .venv
```

### Activate the environment

```bat
.venv\Scripts\activate
```

After activation, the terminal should show `(.venv)` at the beginning of the prompt.

## 3. Install Python Dependencies

Install the application dependencies:

```bat
pip install -r requirements.txt
```

Install the documentation dependencies:

```bat
pip install -r requirements-docs.txt
```

> Keep the virtual environment activated while installing and running the application.

## 4. Install and Configure Ollama

Download and install Ollama from:

https://ollama.com/download

After installation, verify that Ollama is available:

```bat
ollama --version
```

Download the models required by GOS Analyzer:

```bat
ollama pull qwen3:4b-q4_K_M
ollama pull gemma3:4b
```

Verify the installed models:

```bat
ollama list
```

Ollama must be running before starting GOS Analyzer. The Ollama service should normally be available on:

```text
http://localhost:11434
```

## 5. Install and Configure Neo4j

Download and install **Neo4j Desktop** from:

https://neo4j.com/download/

Create a local Neo4j database instance using the following credentials:

```text
Username: neo4j
Password: 123456789
```

Start the Neo4j instance before launching GOS Analyzer.

Make sure the database is running and accessible from the application.

## 6. Run GOS Analyzer

The project includes a Windows startup script that launches the required services.

From the project directory, run:

```bat
run.bat
```

Alternatively, double-click **`run.bat`** from Windows Explorer.

The script starts the GOS Analyzer application and the associated documentation service using the project's configured environment.

## 7. Verify the Setup

Before using the application, confirm:

```text
[✓] Python virtual environment is activated
[✓] Python dependencies are installed
[✓] Ollama is installed and running
[✓] qwen3:4b-q4_K_M model is available
[✓] gemma3:4b model is available
[✓] Neo4j Desktop is installed
[✓] Neo4j database is running
[✓] run.bat starts successfully
```

## 8. Troubleshooting

### Ollama model not found

Run:

```bat
ollama list
```

If the required model is missing, pull it again:

```bat
ollama pull qwen3:4b-q4_K_M
ollama pull gemma3:4b
```

### Neo4j connection error

Ensure that:

1. Neo4j Desktop is open.
2. The configured database is running.
3. The username and password match the application configuration.
4. No other process is blocking the Neo4j service.

### Python dependency errors

Make sure the virtual environment is activated and reinstall the dependencies:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
```

## 9. Recommended Startup Order

For a reliable startup, use the following order:

```text
1. Start Neo4j Desktop
2. Start the Neo4j database
3. Start Ollama
4. Open the GOS Analyzer project directory
5. Run run.bat
6. Open the application in the browser
```
