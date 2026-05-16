"""Upcoming — tasks due in the next 7 days grouped by date."""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from taskbuddy.db import init_db, session_scope
from taskbuddy import repo

st.set_page_config(page_title="Upcoming · TaskBuddy", page_icon="✅", layout="wide")
init_db()

_PRIORITY_ICON = {"high": "🔴", "med": "🟡", "low": "🟢"}

st.title("Upcoming")
st.caption("Tasks due in the next 7 days")

with session_scope() as s:
    upcoming = repo.list_upcoming(s, days=7)
    projects = {p.id: p for p in repo.list_projects(s)}

if not upcoming:
    st.success("Nothing coming up in the next 7 days.")
else:
    # Group by due_date
    by_date: dict[date, list] = {}
    for task in upcoming:
        by_date.setdefault(task.due_date, []).append(task)

    today = date.today()
    for d in sorted(by_date):
        delta = (d - today).days
        if delta == 1:
            label = "Tomorrow"
        else:
            label = d.strftime("%A, %b %d")
        st.subheader(f"📅 {label}")

        for task in by_date[d]:
            proj = projects.get(task.project_id)
            c_icon, c_title, c_proj, c_done = st.columns([0.3, 5, 1, 1])
            c_icon.write(_PRIORITY_ICON.get(task.priority, "🟡"))
            c_title.write(f"**{task.title}**" + (f"  \n_{task.description}_" if task.description else ""))
            c_proj.write(proj.name if proj else "—")
            if c_done.button("✓ Done", key=f"done_{task.id}"):
                with session_scope() as s:
                    repo.update_task(s, task.id, status="done")
                st.rerun()

        st.divider()
