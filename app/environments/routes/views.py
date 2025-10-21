from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Depends, status, Body
from sqlalchemy import func
from sqlmodel import SQLModel, Session, select
from pydantic import ConfigDict
from app.environments.models.environment import Environment
from app.core.dependencies import get_session, get_current_active_user
from app.users.models.user import User

router = APIRouter()

class EnvironmentResponse(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EnvironmentCreate(SQLModel):
    name: str
    description: Optional[str] = None

class EnvironmentUpdate(SQLModel):
    description: Optional[str] = None

class PaginatedEnvironmentResponse(SQLModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[EnvironmentResponse]


@router.get(
    "/",
    response_model=PaginatedEnvironmentResponse,
    summary="List Environments",
    description="Retrieve a paginated list of all environments."
)
def list_environments(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of environments per page (1-100)"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        offset = (page - 1) * page_size
        res = session.exec(select(func.count()).select_from(Environment)).first()
        total_count = (res[0] if isinstance(res, tuple) else int(res or 0))

        environments = session.exec(
            select(Environment)
            .order_by(Environment.id)  
            .offset(offset)
            .limit(page_size)
        ).all()

        next_url = None
        previous_url = None
        if page * page_size < total_count:
            next_url = f"/environments/?page={page + 1}&page_size={page_size}"
        if page > 1:
            previous_url = f"/environments/?page={page - 1}&page_size={page_size}"

        return PaginatedEnvironmentResponse(
            count=total_count,
            next=next_url,
            previous=previous_url,
            results=environments,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/",
    response_model=EnvironmentResponse,
    summary="Create Environment",
    description="Create a new environment with the provided details.",
    status_code=status.HTTP_201_CREATED
)
def create_environment(
    payload: EnvironmentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        existing_env = session.exec(
            select(Environment).where(Environment.name == payload.name)
        ).first()
        if existing_env:
            raise HTTPException(status_code=400, detail="Environment with this name already exists")

        env = Environment(**payload.model_dump())
        env.updated_at = env.created_at 
        session.add(env)
        session.commit()
        session.refresh(env)
        return env
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/{env_name}/",
    response_model=EnvironmentResponse,
    summary="Get Environment",
    description="Retrieve details of a specific environment by its name."
)
def get_environment(
    env_name: str = Path(..., description="Name of the environment to retrieve"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        environment = session.exec(
            select(Environment).where(Environment.name == env_name)
        ).first()
        if not environment:
            raise HTTPException(status_code=404, detail="Environment not found")
        return environment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put(
    "/{env_name}/",
    response_model=EnvironmentResponse,
    summary="Update Environment",
    description="Update an existing environment with the provided details."
)
def update_environment(
    env_name: str = Path(..., description="Name of the environment to update"),
    payload: EnvironmentUpdate = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        environment = session.exec(
            select(Environment).where(Environment.name == env_name)
        ).first()
        if not environment:
            raise HTTPException(status_code=404, detail="Environment not found")

        data = payload.model_dump(exclude_unset=True)
        if "description" in data:
            environment.description = data["description"]

        environment.updated_at = datetime.utcnow()
        session.add(environment)
        session.commit()
        session.refresh(environment)
        return environment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch(
    "/{env_name}/",
    response_model=EnvironmentResponse,
    summary="Partially Update Environment",
    description="Partially update an existing environment with the provided details."
)
def patch_environment(
    env_name: str = Path(..., description="Name of the environment to update"),
    payload: EnvironmentUpdate = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        environment = session.exec(
            select(Environment).where(Environment.name == env_name)
        ).first()
        if not environment:
            raise HTTPException(status_code=404, detail="Environment not found")

        data = payload.model_dump(exclude_unset=True)
        if "description" in data:
            environment.description = data["description"]

        environment.updated_at = datetime.utcnow()
        session.add(environment)
        session.commit()
        session.refresh(environment)
        return environment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
