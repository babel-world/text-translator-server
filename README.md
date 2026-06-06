# NLP Server

A local, multi-language text translation API powered by Ollama and FastAPI.

## Tech Stack

![Ollama](https://img.shields.io/badge/Ollama-f8f8f8?style=flat&logo=ollama&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-de5fe9?style=flat&logo=uv&logoColor=white)

## Prerequisites & Model Selection

Before running the server, ensure you have the following ready:

1. **Ollama**: Must be [installed](https://ollama.com/download) and running in the background.
2. **uv**: Install the [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager (used for `uv sync` and `uv run` below).
3. **Pull the Translation Model**: You must manually pull your desired [translategemma](https://ollama.com/library/translategemma) model using the Ollama CLI (e.g., `ollama pull translategemma:latest`, `ollama pull translategemma:12b-it-q8_0`, etc.).
   
   > **⚠️ IMPORTANT**: The server will NOT automatically pull or download models for you. Ensure the specific model version you want to use exists locally before starting the server and making API requests.

### Configuration

You can specify which downloaded model the server should use by creating a `.env` file in the root directory. This allows you to easily switch between different model sizes and quantizations (e.g., `4b`, `12b`, `27b`, or `4b-it-q4_K_M`) without changing any code:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and adjust the optional settings as needed:

   - `OLLAMA_MODEL`: The exact tag you pulled via the Ollama CLI. (Default: `translategemma:latest`)
   - `SERVER_PORT`: The port the server listens on. (Default: `19032`)

## Local Deployment

1. Navigate to the project root directory (where `pyproject.toml` is located).
2. Sync the dependencies and start the local development server:

```bash
uv sync
uv run nlp-server
```

The API will now be available locally (default: `http://127.0.0.1:19032`, or the port set in `SERVER_PORT`).

## G2P Japanese Endpoint

Convert Japanese text to phonemes via OpenJTalk (`pyopenjtalk-plus`).

### Request

```json
{
  "text": "こんにちは。",
  "mode": "default"
}
```

- `mode`: `default` (basic `pyopenjtalk.g2p`) or `prosody` (with `^` `$` `[` `]` etc.)

### Response

```json
{
  "phones": ["k", "o", "N", "n", "i", "ch", "i", "w", "a"]
}
```

### API Usage

```bash
curl -X POST "http://127.0.0.1:19032/api/g2p/ja" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"こんにちは。\",\"mode\":\"default\"}"
```

### Local Script Test

```bash
uv run python scripts/test_g2p_ja.py
uv run python scripts/test_g2p_ja.py --mode prosody
uv run python scripts/test_g2p_ja.py --run http --base-url http://127.0.0.1:19032
```

GPT-SoVITS manifest CSV 胶水代码已归档至 `.local/g2p/`，由外部 Prefect 项目负责。

## Project Structure

```text
nlp-server/
├── pyproject.toml
├── README.md
├── scripts/
│   ├── load_ollama_test.py
│   └── test_g2p_ja.py
├── src/
│   └── nlp_server/
│       ├── api/
│       │   ├── deps.py
│       │   ├── router.py
│       │   └── routes/
│       │       ├── g2p.py
│       │       └── ollama.py
│       ├── config/
│       │   └── settings.py
│       ├── main.py
│       ├── schemas/
│       │   ├── g2p.py
│       │   └── translate.py
│       └── services/
│           ├── g2p/
│           │   ├── ja/
│           │   │   ├── default.py
│           │   │   └── prosody.py
│           │   ├── README.md
│           │   └── __init__.py
│           └── ollama.py
└── uv.lock
```
