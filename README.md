# TaskBuddy

Planner for tasks listed down for easy access and time management.

Personal task tracker built with Streamlit and SQLite.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud (free)

1. Push this repo to GitHub (public or private).
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → pick this repo → `app.py`.
3. For persistent storage, add a free PostgreSQL database (e.g. [Neon](https://neon.tech)) and set the connection string in Streamlit Cloud secrets:

```toml
# .streamlit/secrets.toml  (do not commit this file)
DATABASE_URL = "postgresql+psycopg://user:pass@host/dbname"
```

Without a `DATABASE_URL`, the app uses SQLite — data resets on Streamlit Cloud restart.
