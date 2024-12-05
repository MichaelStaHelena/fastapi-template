from fastapi import Depends
from sqlmodel import Session

from app.database import get_session
from app.services.task_service import TaskService


def get_task_service(
        session: Session = Depends(get_session)
) -> TaskService:
    return TaskService(session)
