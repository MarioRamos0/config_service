from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.core.settings import engine
from app.core.jwt import verify_token
from app.users.models.user import User
from app.users.models.auth import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/auth/login")

def get_session():
    with Session(engine) as session:
        yield session

#Obtener usuario actual
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except Exception:
        raise credentials_exception
    
    statement = select(User).where(User.username == token_data.username)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception
    return user

#Obtener usuario activo
def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user