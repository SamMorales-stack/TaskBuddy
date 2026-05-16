"""TaskBuddy — Dashboard."""
from __future__ import annotations

import streamlit as st

from taskbuddy.db import init_db, session_scope
from taskbuddy import repo

st.set_page_config(page_title="TaskBuddy", page_icon="✅", layout="wide")
init_db()

_PRIORITY_LABEL = {"high": "🔴 High", "med": "🟡 Medium", "low": "🟢 Low"}
_PRIORITY_ICON  = {"high": "🔴", "med": "🟡", "low": "🟢"}

st.title("✅ TaskBuddy")
st.caption("Your personal task tracker")

# ── Metrics ───────────────────────────────────────────────────────────────────
with session_scope() as s:
    overdue_tasks  = repo.list_overdue(s)
    today_tasks    = repo.list_due_today(s)
    upcoming_tasks = repo.list_upcoming(s, days=7)
    active_count   = repo.count_active(s)
    projects       = repo.list_projects(s)
    project_map    = {p.id: p for p in projects}
    project_opts   = {p.name: p.id for p in projects}

c1, c2, c3, c4 = st.columns(4)
c1.metric("🔴 Overdue",       len(overdue_tasks))
c2.metric("📅 Due Today",     len(today_tasks))
c3.metric("📆 Due This Week", len(upcoming_tasks))
c4.metric("⚡ Active",        active_count)

st.divider()

# ── Quick add ─────────────────────────────────────────────────────────────────
st.subheader("Quick Add Task")
with st.form("quick_add", clear_on_submit=True):
    col_t, col_d, col_p, col_proj, col_btn = st.columns([3, 1, 1, 1, 1])
    title    = col_t.text_input("Title", placeholder="What needs to be done?", label_visibility="collapsed")
    due      = col_d.date_input("Due", value=None, label_visibility="collapsed")
    priority = col_p.selectbox("Priority", ["med", "high", "low"], format_func=lambda x: _PRIORITY_LABEL[x], label_visibility="collapsed")
    proj_name = col_proj.selectbox("Project", ["(none)"] + list(project_opts.keys()), label_visibility="collapsed")
    submitted = col_btn.form_submit_button("＋ Add", use_container_width=True)

    if submitted and title.strip():
        pid = project_opts.get(proj_name) if proj_name != "(none)" else None
        with session_scope() as s:
            repo.create_task(s, title=title.strip(), due_date=due, priority=priority, project_id=pid)
        st.success("Task added!")
        st.rerun()
    elif submitted:
        st.warning("Title is required.")

# ── Overdue ───────────────────────────────────────────────────────────────────
if overdue_tasks:
    st.divider()
    st.subheader(f"⚠️ Overdue ({len(overdue_tasks)})")
    for task in overdue_tasks:
        proj = project_map.get(task.project_id)
        c_title, c_due, c_proj, c_done, c_del = st.columns([4, 1, 1, 1, 1])
        c_title.write(f"{_PRIORITY_ICON.get(task.priority, '🟡')} **{task.title}**")
        c_due.write(str(task.due_date))
        c_proj.write(proj.name if proj else "—")
        if c_done.button("✓ Done", key=f"done_{task.id}"):
            with session_scope() as s:
                repo.update_task(s, task.id, status="done")
            st.rerun()
        if c_del.button("🗑️", key=f"del_{task.id}"):
            with session_scope() as s:
                repo.delete_task(s, task.id)
            st.rerun()

# ── Due today ─────────────────────────────────────────────────────────────────
if today_tasks:
    st.divider()
    st.subheader(f"📅 Due Today ({len(today_tasks)})")
    for task in today_tasks:
        proj = project_map.get(task.project_id)
        c_title, c_proj, c_done, c_del = st.columns([5, 1, 1, 1])
        c_title.write(f"{_PRIORITY_ICON.get(task.priority, '🟡')} **{task.title}**")
        c_proj.write(proj.name if proj else "—")
        if c_done.button("✓ Done", key=f"done_today_{task.id}"):
            with session_scope() as s:
                repo.update_task(s, task.id, status="done")
            st.rerun()
        if c_del.button("🗑️", key=f"del_today_{task.id}"):
            with session_scope() as s:
                repo.delete_task(s, task.id)
            st.rerun()

if not overdue_tasks and not today_tasks:
    st.success("You're all caught up! Nothing overdue or due today.")
