## Backend (FastAPI)

### Prerequisites
- Python 3.10+

### Setup
1. Create and activate a virtual environment
```bash
python -m venv .venv && source .venv/bin/activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment
```bash
cp .env.example .env
# Edit .env as needed
```

4. Run the server (run from this `backend` directory)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Notes
- Default DB is SQLite at `./data/app.db`. Ensure you run commands from the `backend` directory so the relative path resolves correctly.
- Static files (including uploads) are served at `/static`. Uploads directory is created on startup at `app/static/uploads`.
