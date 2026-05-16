# Deploy TaskBuddy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy TaskBuddy to Streamlit Cloud with persistent data backed by Neon PostgreSQL.

**Architecture:** The app runs on Streamlit Cloud, connected to the `main` branch of the GitHub repo. Task data is stored in a free Neon PostgreSQL database. The app connects via a `DATABASE_URL` secret configured in Streamlit Cloud — no code changes beyond adding the PostgreSQL driver.

**Tech Stack:** Streamlit Cloud (hosting), Neon (PostgreSQL), psycopg2-binary (SQLAlchemy PostgreSQL driver), GitHub (source of truth)

---

### Task 1: Add PostgreSQL driver to requirements.txt

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add psycopg2-binary**

Edit `requirements.txt` so it reads:

```
streamlit>=1.35.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9
```

- [ ] **Step 2: Verify the file looks correct**

Run:
```bash
cat requirements.txt
```
Expected output:
```
streamlit>=1.35.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9
```

- [ ] **Step 3: Commit and push**

```bash
git add requirements.txt
git commit -m "feat: add psycopg2-binary for PostgreSQL support"
git push origin main
```

Expected: push succeeds, commit appears on GitHub at `https://github.com/SamMorales-stack/TaskBuddy`

---

### Task 2: Create Neon PostgreSQL database (manual)

**This task is performed in a browser — no code changes.**

- [ ] **Step 1: Sign up for Neon**

Go to [https://neon.tech](https://neon.tech) → Sign up (free, no credit card required).

- [ ] **Step 2: Create a project**

After signing in → click **New Project** → give it a name (e.g. `taskbuddy`) → choose the region closest to you → click **Create project**.

- [ ] **Step 3: Copy the connection string**

On the project dashboard → click **Connection Details** → select **psycopg2** from the driver dropdown → copy the connection string. It looks like:

```
postgresql+psycopg2://username:password@ep-xxxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

Save this string — you'll need it in Task 3.

---

### Task 3: Deploy on Streamlit Cloud (manual)

**This task is performed in a browser — no code changes.**

- [ ] **Step 1: Sign in to Streamlit Cloud**

Go to [https://share.streamlit.io](https://share.streamlit.io) → sign in with your GitHub account (`SamMorales-stack`).

- [ ] **Step 2: Create a new app**

Click **New app** → fill in:
- **Repository:** `SamMorales-stack/TaskBuddy`
- **Branch:** `main`
- **Main file path:** `app.py`

Do **not** click Deploy yet.

- [ ] **Step 3: Add the DATABASE_URL secret**

Before deploying, click **Advanced settings** → open the **Secrets** section → paste:

```toml
DATABASE_URL = "postgresql+psycopg2://username:password@ep-xxxx.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

Replace the value with the connection string you copied from Neon in Task 2.

- [ ] **Step 4: Deploy**

Click **Deploy**. Streamlit Cloud will:
1. Pull the code from GitHub
2. Install `requirements.txt` (including `psycopg2-binary`)
3. Start the app — `init_db()` runs on first load and creates the `tasks` and `projects` tables in Neon automatically

- [ ] **Step 5: Verify the app works**

Once the deploy finishes (1-2 minutes), open the public URL (format: `https://sammorales-stack-taskbuddy-app-xxxx.streamlit.app`).

Check:
- Dashboard loads with 0 overdue / 0 due today
- Add a task via Quick Add → it appears on screen
- Refresh the page → the task is still there (confirms PostgreSQL persistence is working)
