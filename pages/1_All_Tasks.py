"""All Tasks — full list with filters, edit and delete."""
from __future__ import annotations

from datetime import date

import streamlit as st

from taskbuddy.db import init_db, session_scope
from taskbuddy import repo

st.set_page_config(page_title="All Tasks · TaskBuddy", page_icon="✅", layout="wide")
init_db()

_PRIORITY_ICON  = {"high": "🔴", "med": "🟡", "low": "🟢"}
_PRIORITY_LABEL = {"high": "🔴 High", "med": "🟡 Medium", "low": "🟢 Low"}
_STATUS_LABEL   = {"todo": "To Do", "in_progress": "In Progress", "done": "✓ Done"}

st.title("All Tasks")

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    with session_scope() as s:
        projects = repo.list_projects(s)
    project_opts = {"All projects": None} | {p.name: p.id for p in projects}

    filter_proj   = st.selectbox("Project",  list(project_opts.keys()))
    filter_status = st.selectbox("Status",   ["All", "To Do", "In Progress", "Done"])
    filter_prio   = st.selectbox("Priority", ["All", "🔴 High", "🟡 Medium", "🟢 Low"])

_STATUS_MAP = {"All": None, "To Do": "todo", "In Progress": "in_progress", "Done": "done"}
_PRIO_MAP   = {"All": None, "🔴 High": "high", "🟡 Medium": "med", "🟢 Low": "low"}

# ── Add task form ──────────────────────────────────────────────────────────────
with st.expander("＋ Add new task", expanded=False):
    with st.form("add_task", clear_on_submit=True):
        title = st.text_input("Title *")
        desc  = st.text_area("Description", height=80)
        c1, c2, c3, c4 = st.columns(4)
        due      = c1.date_input("Due date", value=None)
        priority = c2.selectbox("Priority", ["med", "high", "low"], format_func=lambda x: _PRIORITY_LABEL[x])
        status   = c3.selectbox("Status",   ["todo", "in_progress"], format_func=lambda x: _STATUS_LABEL[x])
        proj_name = c4.selectbox("Project", ["(none)"] + [p.name for p in projects])
        if st.form_submit_button("Add Task"):
            if title.strip():
                pid = {p.name: p.id for p in projects}.get(proj_name) if proj_name != "(none)" else None
                with session_scope() as s:
                    repo.create_task(s, title=title.strip(), description=desc, due_date=due, priority=priority, status=status, project_id=pid)
                st.success("Task added!")
                st.rerun()
            else:
                st.warning("Title is required.")

st.divider()

# ── Task list ──────────────────────────────────────────────────────────────────
with session_scope() as s:
    tasks    = repo.list_tasks(s, project_id=project_opts[filter_proj], status=_STATUS_MAP[filter_status], priority=_PRIO_MAP[filter_prio])
    proj_map = {p.id: p for p in projects}

if not tasks:
    st.info("No tasks match the current filters.")
else:
    st.caption(f"{len(tasks)} task(s)")
    # Header row
    hc = st.columns([4, 1, 1, 1, 1, 1])
    for col, label in zip(hc, ["Title", "Due", "Priority", "Status", "Project", ""]):
        col.markdown(f"**{label}**")
    st.divider()

    for task in tasks:
        proj = proj_map.get(task.project_id)
        c_title, c_due, c_prio, c_status, c_proj, c_del = st.columns([4, 1, 1, 1, 1, 1])

        c_title.write(f"**{task.title}**" + (f"\n\n_{task.description}_" if task.description else ""))
        c_due.write(str(task.due_date) if task.due_date else "—")
        c_prio.write(_PRIORITY_ICON.get(task.priority, "🟡"))
        new_status = c_status.selectbox(
            "", list(_STATUS_LABEL.keys()),
            index=list(_STATUS_LABEL.keys()).index(task.status),
            format_func=lambda x: _STATUS_LABEL[x],
            key=f"s_{task.id}",
            label_visibility="collapsed",
        )
        if new_status != task.status:
            with session_scope() as s:
                repo.update_task(s, task.id, status=new_status)
            st.rerun()

        c_proj.write(proj.name if proj else "—")
        if c_del.button("🗑️", key=f"del_{task.id}", help="Delete task"):
            with session_scope() as s:
                repo.delete_task(s, task.id)
            st.rerun()
