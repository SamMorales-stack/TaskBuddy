from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from taskbuddy.models import Project, Task


# ── Projects ──────────────────────────────────────────────────────────────────

def list_projects(s: Session) -> list[Project]:
    return s.query(Project).order_by(Project.name).all()


def get_project(s: Session, project_id: str) -> Project | None:
    return s.get(Project, project_id)


def create_project(s: Session, *, name: str, color: str = "#4A90D9") -> Project:
    p = Project(name=name, color=color)
    s.add(p)
    s.flush()
    return p


def delete_project(s: Session, project_id: str) -> None:
    p = s.get(Project, project_id)
    if p:
        s.delete(p)


# ── Tasks ──────────────────────────────────────────────────────────────────────

def list_tasks(
    s: Session,
    *,
    project_id: str | None = None,
    status: str | None = None,
    priority: str | None = None,
) -> list[Task]:
    q = s.query(Task)
    if project_id:
        q = q.filter(Task.project_id == project_id)
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == priority)
    return q.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()


def list_overdue(s: Session) -> list[Task]:
    today = date.today()
    return (
        s.query(Task)
        .filter(Task.due_date < today, Task.status != "done")
        .order_by(Task.due_date.asc())
        .all()
    )


def list_due_today(s: Session) -> list[Task]:
    return (
        s.query(Task)
        .filter(Task.due_date == date.today(), Task.status != "done")
        .all()
    )


def list_upcoming(s: Session, *, days: int = 7) -> list[Task]:
    today = date.today()
    end = today + timedelta(days=days)
    return (
        s.query(Task)
        .filter(Task.due_date > today, Task.due_date <= end, Task.status != "done")
        .order_by(Task.due_date.asc())
        .all()
    )


def count_active(s: Session) -> int:
    return s.query(Task).filter(Task.status != "done").count()


def create_task(
    s: Session,
    *,
    title: str,
    description: str = "",
    due_date: date | None = None,
    priority: str = "med",
    status: str = "todo",
    project_id: str | None = None,
) -> Task:
    t = Task(
        title=title,
        description=description or None,
        due_date=due_date,
        priority=priority,
        status=status,
        project_id=project_id or None,
    )
    s.add(t)
    s.flush()
    return t


def update_task(s: Session, task_id: str, **fields) -> Task | None:
    t = s.get(Task, task_id)
    if t is None:
        return None
    for k, v in fields.items():
        setattr(t, k, v)
    return t


def delete_task(s: Session, task_id: str) -> None:
    t = s.get(Task, task_id)
    if t:
        s.delete(t)
