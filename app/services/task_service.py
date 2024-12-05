import logging
from typing import Optional
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, PageResponse

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, task: TaskCreate) -> Task:
        try:
            logger.info(task)
            db_task = Task(**task.dict())
            logger.info(db_task)
            self.session.add(db_task)
            self.session.commit()
            self.session.refresh(db_task)
            logger.info(f"Created task: {db_task.title}")
            return db_task
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create task"
            )

    def get_all(
            self,
            page: int = 1,
            size: int = 10,
            search: Optional[str] = None
    ) -> PageResponse:
        try:
            query = select(Task)

            # Apply filters
            if search:
                query = query.where(Task.title.contains(search))

            # Default sorting by ID
            query = query.order_by(Task.id)

            # Count total items
            total = self.session.exec(
                select(func.count()).select_from(query)
            ).one()

            # Calculate pagination
            pages = (total + size - 1) // size
            offset = (page - 1) * size

            # Get items for current page
            items = self.session.exec(
                query.offset(offset).limit(size)
            ).all()

            return PageResponse(
                items=items,
                total=total,
                page=page,
                size=size,
                pages=pages,
                has_next=page < pages,
                has_prev=page > 1
            )
        except Exception as e:
            logger.error(f"Error retrieving tasks: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving tasks"
            )

    def get_by_id(self, task_id: int) -> Task:
        try:
            task = self.session.get(Task, task_id)
            if not task:
                logger.warning(f"Task not found: {task_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
            return task
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving task"
            )

    def update(self, task_id: int, task_update: TaskUpdate) -> Task:
        try:
            db_task = self.get_by_id(task_id)

            update_data = task_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_task, key, value)

            if "status" in update_data:
                if update_data["status"] == "in_progress":
                    db_task.start_date = datetime.now(timezone.utc)
                elif update_data["status"] in ["completed", "canceled"]:
                    db_task.end_date = datetime.now(timezone.utc)

            self.session.add(db_task)
            self.session.commit()
            self.session.refresh(db_task)
            logger.info(f"Updated task: {task_id}")
            return db_task
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not update task"
            )

    def delete(self, task_id: int) -> None:
        try:
            task = self.get_by_id(task_id)
            self.session.delete(task)
            self.session.commit()
            logger.info(f"Deleted task: {task_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not delete task"
            )
