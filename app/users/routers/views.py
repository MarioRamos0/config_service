from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import SQLModel, Session, select
from typing import List, Optional
from app.users.models.user import User
from app.users.models.auth import LoginRequest, Token, TokenData
from app.core.settings import engine
from app.core.jwt import create_access_token, verify_token
from app.core.dependencies import get_session, get_current_active_user, get_current_user
from datetime import timedelta
import hashlib

router = APIRouter()

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def authenticate_user(session: Session, username: str, password: str):
    try:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        if not user:
            return False
        if not verify_password(password, user.password_hash):
            return False
        return user
    except Exception:
        return False

class UserResponse(User):
    pass

class PaginatedUserResponse(SQLModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[UserResponse]

#Inicio de sesion, retorna token
@router.post("/auth/login", response_model=Token, summary="User Login",
          description="Authenticate a user and return a JWT token.")
def login(
    login_request: LoginRequest,
    session: Session = Depends(get_session)
):
    try:
        user = authenticate_user(session, login_request.username, login_request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Muestra la lista de usuarios con paginacion
@router.get("/", response_model=PaginatedUserResponse, summary="List Users", 
         description="Retrieve a paginated list of all users.")
def list_users(
    page: int = 1,
    page_size: int = 10,
    session: Session = Depends(get_session)
):
    try:
        offset = (page - 1) * page_size
        count_statement = select(User)
        total_count = len(session.exec(count_statement).all())
        statement = select(User).offset(offset).limit(page_size)
        users = session.exec(statement).all()
        next_url = None
        previous_url = None
        if page * page_size < total_count:
            next_url = f"/users/?page={page + 1}&page_size={page_size}"
        if page > 1:
            previous_url = f"/users/?page={page - 1}&page_size={page_size}"
        return PaginatedUserResponse(
            count=total_count,
            next=next_url,
            previous=previous_url,
            results=users
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

#Crear usuario
@router.post("/", response_model=UserResponse, summary="Create User",
          description="Create a new user with the provided details.", status_code=status.HTTP_201_CREATED)
def create_user(
    user: User,
    session: Session = Depends(get_session)
):
    try:
        statement = select(User).where(User.username == user.username)
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this username already exists")
        user.password_hash = get_password_hash(user.password_hash)
        user.updated_at = user.created_at
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

#Obtener usuario por id
@router.get("/{user_id}/", response_model=UserResponse, summary="Get User",
         description="Retrieve details of a specific user by its ID.")
def get_user(
    user_id: int,
    session: Session = Depends(get_session)
):
    try:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

#Actualizar usuario por id
@router.put("/{user_id}/", response_model=UserResponse, summary="Update User",
         description="Update an existing user with the provided details.")
def update_user(
    user_id: int,
    user_update: User,
    session: Session = Depends(get_session)
):
    try:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.username = user_update.username
        user.password_hash = get_password_hash(user_update.password_hash)
        user.is_admin = user_update.is_admin
        from datetime import datetime
        user.updated_at = datetime.utcnow()
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )