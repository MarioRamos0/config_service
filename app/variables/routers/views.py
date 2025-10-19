from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session, select
from typing import List
from app.core.dependencies import get_session, get_current_active_user
from app.environments.models.environment import Environment
from app.variables.models.variable import Variable
from app.users.models.user import User

router = APIRouter()

# Listar variables de un entorno
@router.post("/", response_model=Variable, summary="Create a Variable in an Environment", status_code=status.HTTP_201_CREATED)
def create_variable_for_environment(
    variable: Variable,
    env_name: str = Path(..., description="Name of the environment"), 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Crea una nueva variable y la asocia a un entorno existente.
    """
    # Busca si el entorno existe
    env_statement = select(Environment).where(Environment.name == env_name)
    environment = session.exec(env_statement).first()
    if not environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")

    # Verifica que no exista ya una variable con ese nombre en este entorno
    var_statement = select(Variable).where(Variable.name == variable.name, Variable.environment_id == environment.id)
    existing_variable = session.exec(var_statement).first()
    if existing_variable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Variable '{variable.name}' already exists in this environment.")

    # Asocia la variable con el ID del entorno encontrado
    variable.environment_id = environment.id
    
    session.add(variable)
    session.commit()
    session.refresh(variable)
    
    return variable

@router.get("/", response_model=List[Variable], summary="List Variables for an Environment")
def list_variables_for_environment(
    env_name: str = Path(..., description="Name of the environment"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene todas las variables para un entorno específico.
    """
    environment = session.exec(select(Environment).where(Environment.name == env_name)).first()
    if not environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")
    
    # Devuelve solo las variables asociadas a ese entorno
    return environment.variables