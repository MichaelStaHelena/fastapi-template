import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, Path, status

from app.dependencies import get_task_service
from app.schemas import (
    TaskCreate, TaskRead, TaskUpdate,
    PageResponse, PageParams
)
from app.services.task_service import TaskService

# Create routers with tags for better API documentation
task_router = APIRouter(prefix="/tasks", tags=["tasks"])

logger = logging.getLogger(__name__)


# Task Routes
@task_router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    response_description="The created task"
)
async def create_task(
        task: TaskCreate,
        service: TaskService = Depends(get_task_service)
):
    """
    Create a new task.

    Request Fields:
    - **title** (str): The title of the task (1-100 characters, required).
    - **description** (Optional[str]): A detailed description of the task (up to 1000 characters).
    - **due_date** (Optional[datetime]): The deadline for the task.
    - **status** (TaskStatus): The status of the task ("in_progress", "completed", "cancelled", default: "pending").
    - **priority** (TaskPriority): The priority level of the task (default: "medium").

    Response Fields:
    - **id** (int): The unique identifier of the task.
    - **created_at** (datetime): The timestamp when the task was created.
    """
    logger.info(task)
    return service.create(task)


@task_router.get(
    "/",
    response_model=PageResponse,
    summary="Get all tasks",
    response_description="Paginated list of tasks"
)
async def read_tasks(
        page_params: PageParams = Depends(),
        search: Optional[str] = Query(
            None,
            min_length=3,
            max_length=50,
            description="Search tasks by title"
        ),
        service: TaskService = Depends(get_task_service)
):
    """
    Get all tasks with pagination and optional search.

    Query Parameters:
    - **page** (int): The page number (default: 1).
    - **size** (int): The number of tasks per page (default: 10).
    - **search** (Optional[str]): A search term to filter tasks by title.

    Response Fields:
    - **items** (List[TaskRead]): The list of tasks.
    - **total** (int): Total number of tasks.
    - **page** (int): Current page number.
    - **size** (int): Number of items per page.
    - **pages** (int): Total number of pages.
    - **has_next** (bool): Whether there is a next page.
    - **has_prev** (bool): Whether there is a previous page.
    """
    return service.get_all(
        page=page_params.page,
        size=page_params.size,
        search=search
    )


@task_router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get a specific task",
    response_description="The requested task"
)
async def read_task(
        task_id: int = Path(..., ge=1, description="The ID of the task to retrieve"),
        service: TaskService = Depends(get_task_service)
):
    """
    Get a specific task by its ID.

    Path Parameters:
    - **task_id** (int): The ID of the task to retrieve.

    Response Fields:
    - **id** (int): The unique identifier of the task.
    - **title** (str): The title of the task.
    - **description** (Optional[str]): A detailed description of the task.
    - **due_date** (Optional[datetime]): The deadline for the task.
    - **status** (TaskStatus): The status of the task.
    - **priority** (TaskPriority): The priority level of the task.
    - **created_at** (datetime): The timestamp when the task was created.
    """
    return service.get_by_id(task_id)


@task_router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    response_description="The updated task"
)
async def update_task(
        task_update: TaskUpdate,
        task_id: int = Path(..., ge=1, description="The ID of the task to update"),
        service: TaskService = Depends(get_task_service)
):
    """
    Update a task.

    Path Parameters:
    - **task_id** (int): The ID of the task to update.

    Request Fields:
    - **title** (Optional[str]): The updated title of the task (1-100 characters).
    - **description** (Optional[str]): The updated description of the task.
    - **due_date** (Optional[datetime]): The updated deadline for the task.
    - **status** (Optional[TaskStatus]): The updated status of the task.
    - **priority** (Optional[TaskPriority]): The updated priority of the task.

    Response Fields:
    - **id** (int): The unique identifier of the task.
    - **created_at** (datetime): The timestamp when the task was created.
    - **title** (str): The updated title of the task.
    - **description** (Optional[str]): The updated description.
    - **due_date** (Optional[datetime]): The updated deadline.
    - **status** (TaskStatus): The updated status.
    - **priority** (TaskPriority): The updated priority level.
    """
    return service.update(task_id, task_update)


@task_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    response_description="Task successfully deleted"
)
async def delete_task(
        task_id: int = Path(..., ge=1, description="The ID of the task to delete"),
        service: TaskService = Depends(get_task_service)
):
    """
    Delete a specific task by its ID.

    Path Parameters:
    - **task_id** (int): The ID of the task to delete.

    Returns:
        HTTP 204 status code if the task is successfully deleted.
    """
    service.delete(task_id)
