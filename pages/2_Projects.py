"""Projects — manage projects and view tasks by project."""
from __future__ import annotations

import streamlit as st

from taskbuddy.db import init_db, session_scope
from taskbuddy import repo

st.set_page_config(page_title="Projects · TaskBuddy", page_icon="✅", layout="wide")
init_db()

st.title("Projects")

# ── Create project ─────────────────────────────────────────────────────────────
with st.expander("＋ New project", expanded=False):
    with st.form("new_project", clear_on_submit=True):
        c1, c2, c3 = st.columns([3, 1, 1])
        name  = c1.text_input("Project name *")
        color = c2.color_picker("Color", value="#4A90D9")
        if c3.form_submit_button("Create", use_container_width=True):
            if name.strip():
                with session_scope() as s:
                    repo.create_project(s, name=name.strip(), color=color)
                st.success(f'Project "{name}" created!')
                st.rerun()
            else:
                st.warning("Name is required.")

st.divider()

# ── Project cards ──────────────────────────────────────────────────────────────
with session_scope() as s:
    projects = repo.list_projects(s)
    counts = {
        p.id: {
            "total":       len(p.tasks),
            "todo":        sum(1 for t in p.tasks if t.status == "todo"),
            "in_progress": sum(1 for t in p.tasks if t.status == "in_progress"),
            "done":        sum(1 for t in p.tasks if t.status == "done"),
        }
        for p in projects
    }

if not projects:
    st.info("No projects yet. Create one above.")
else:
    cols = st.columns(3)
    for i, project in enumerate(projects):
        c = counts[project.id]
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(
                    f"<span style='display:inline-block;width:12px;height:12px;"
                    f"border-radius:50%;background:{project.color};margin-right:6px'></span>"
                    f"**{project.name}**",
                    unsafe_allow_html=True,
                )
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("To Do",      c["todo"])
                mc2.metric("In Progress", c["in_progress"])
                mc3.metric("Done",        c["done"])

                if st.button("View tasks", key=f"view_{project.id}", use_container_width=True):
                    st.session_state["filter_project"] = project.id
                    st.switch_page("pages/1_All_Tasks.py")

                if st.button("🗑️ Delete project", key=f"del_{project.id}", use_container_width=True, type="secondary"):
                    with session_scope() as s:
                        repo.delete_project(s, project.id)
                    st.rerun()
