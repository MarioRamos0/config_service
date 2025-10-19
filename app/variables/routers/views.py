import datetime
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session, select
from typing import List, Optional
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

@router.get("/{var_name}", response_model=Variable, summary="Get a Specific Variable")
def get_variable(
    env_name: str = Path(..., description="Name of the environment"),
    var_name: str = Path(..., description="Name of the variable"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene los detalles de una variable específica dentro de un entorno.
    """
    # asegurar que el entorno existe
    environment = session.exec(select(Environment).where(Environment.name == env_name)).first()
    if not environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")

    # busca la variable por su nombre en ese entorno
    statement = select(Variable).where(Variable.name == var_name, Variable.environment_id == environment.id)
    variable = session.exec(statement).first()
    if not variable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variable not found in this environment")
    
    return variable

class VariableUpdate(SQLModel):
    value: str
    description: Optional[str] = None
    is_sensitive: Optional[bool] = None

@router.put("/{var_name}", response_model=Variable, summary="Update a Variable")
def update_variable(
    variable_update: VariableUpdate,
    env_name: str = Path(..., description="Name of the environment"),
    var_name: str = Path(..., description="Name of the variable to update"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualiza completamente una variable existente en un entorno.
    """
    environment = session.exec(select(Environment).where(Environment.name == env_name)).first()
    if not environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")

    statement = select(Variable).where(Variable.name == var_name, Variable.environment_id == environment.id)
    db_variable = session.exec(statement).first()
    if not db_variable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variable not found")

    # Actualiza los campos del objeto de la BD con los datos del payload
    db_variable.value = variable_update.value
    db_variable.description = variable_update.description
    db_variable.is_sensitive = variable_update.is_sensitive
    db_variable.updated_at = datetime.utcnow()

    session.add(db_variable)
    session.commit()
    session.refresh(db_variable)
    
    return db_variable

class VariablePatch(SQLModel):
    value: Optional[str] = None
    description: Optional[str] = None
    is_sensitive: Optional[bool] = None

@router.patch("/{var_name}", response_model=Variable, summary="Partially Update a Variable")
def patch_variable(
    variable_patch: VariablePatch,
    env_name: str = Path(..., description="Name of the environment"),
    var_name: str = Path(..., description="Name of the variable to update"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualiza parcialmente una variable existente. Solo los campos proporcionados se modificarán.
    """
    environment = session.exec(select(Environment).where(Environment.name == env_name)).first()
    if not environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")

    db_variable = session.exec(select(Variable).where(Variable.name == var_name, Variable.environment_id == environment.id)).first()
    if not db_variable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variable not found")

    # Itera sobre los datos proporcionados y actualiza solo si no son None
    patch_data = variable_patch.model_dump(exclude_unset=True)
    for key, value in patch_data.items():
        setattr(db_variable, key, value)
    
    db_variable.updated_at = datetime.utcnow()

    session.add(db_variable)
    session.commit()
    session.refresh(db_variable)

    return db_variable

@router.delete("/{var_name}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a Variable")
def delete_variable(
    env_name: str = Path(..., description="Name of the environment"),
    var_name: str = Path(..., description="Name of the variable to delete"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Elimina una variable específica de un entorno.
    """
    environment = session.exec(select(Environment).where(Environment.name == env_name)).first()
    if not environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")

    variable_to_delete = session.exec(select(Variable).where(Variable.name == var_name, Variable.environment_id == environment.id)).first()
    if not variable_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variable not found")

    session.delete(variable_to_delete)
    session.commit()
    
    return