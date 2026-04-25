# img-cdn

Ekonomi image CDN proxy built on FastAPI.

## Setup

```bash
uv sync
cp .env.example .env   # set API_URL, HOST, PORT, DEBUG
```

## Run

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 5000
```

OpenAPI docs: `http://<host>:<port>/docs`
