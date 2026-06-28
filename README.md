# Cursor Pagination Demo

This project demonstrates three pagination strategies against a large transaction dataset:

- Offset pagination
- Cursor pagination
- Keyset / inner-join pagination

The app is intentionally focused on the pagination experience and leaves the core SQL, timings, and index decisions as TODOs for the accompanying article.

## Setup

1. Create a PostgreSQL database:

   ```bash
   createdb pagination_demo
   ```

2. Copy the environment example:

   ```bash
   cp .env.example .env
   ```

3. Update the database URL in `.env` if needed.

4. Install Python dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

5. Seed the database with 1,000,000 rows:

   ```bash
   python backend/seed.py
   ```

6. Start the API server:

   ```bash
   uvicorn backend.main:app --reload
   ```

7. Open the frontend at `frontend/index.html` in your browser.

## Notes

- The API serves three endpoints:
  - `/api/offset`
  - `/api/cursor`
  - `/api/keyset`
- The frontend fetches response timings and renders a chart for the three strategies.
- The SQL queries and timing logic are left as TODO placeholders for the article author.
