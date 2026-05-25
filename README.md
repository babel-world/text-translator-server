# Text Translator Server

A local, multi-language text translation API powered by Ollama and FastAPI.

## Tech Stack

![Ollama](https://img.shields.io/badge/Ollama-f8f8f8?style=flat&logo=ollama&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-de5fe9?style=flat&logo=uv&logoColor=white)

## Prerequisites

Before running the server, ensure you have the following ready:

1. **Ollama**: Must be [installed](https://ollama.com/download) and running in the background.
2. **Translation Model**: Pull the [translategemma](https://ollama.com/library/translategemma) model using the Ollama CLI: `ollama pull translategemma:latest` (Note: You can also pull specific sizes like translategemma:4b, depending on your hardware).
3. **uv**: Install the [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager (used for `uv sync` and `uv run` below).

## Local Deployment

1. Navigate to the project root directory (where `pyproject.toml` is located).
2. Sync the dependencies and start the local development server:

```bash
uv sync
uv run text-translator-server
```

The API will now be available locally (default: `http://127.0.0.1:19032`).

## Project Structure

```text
text-translator-server/
├── pyproject.toml
├── README.md
├── src/
│   └── text_translator_server/
│       ├── api/
│       │   ├── deps.py
│       │   ├── router.py
│       │   └── routes/
│       │       └── translate.py
│       ├── config/
│       │   └── settings.py
│       ├── main.py
│       ├── schemas/
│       │   └── translate.py
│       └── services/
│           └── translate.py
└── uv.lock
```
