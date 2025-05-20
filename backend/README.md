# AutoDataCleanser Backend

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your Supabase credentials.
3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## Local Development

1. Create a virtual environment (PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

The API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs)

## Structure

- `main.py` — FastAPI app entrypoint
- `api/` — All API endpoints
- `db/supabase_client.py` — Supabase client
- `utils/` — Cleaning, audit, and auth logic
- `schemas/` — Pydantic schemas

## Endpoints (all under `/api` and JWT-protected)
- `POST /upload` — Upload CSV/Excel, returns session_id and preview
- `GET /profile/{session_id}` — Per-column stats
- `POST /clean` — Cleansing (impute, outlier, dedupe)
- `GET /audit/{session_id}` — Get transformation history
- `GET /download/{session_id}` — Download cleaned CSV
- `POST /features` — Feature suggestions

## Security
- All endpoints require Supabase JWT (Bearer token)
- CORS enabled for `http://localhost:3000`

## Notes
- Uploaded files are stored in a temp directory.
- Cleaned files are saved for download.
- Audit logs and session metadata are stored in Supabase. 