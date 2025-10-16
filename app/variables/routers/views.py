
from fastapi import APIRouter

router = APIRouter()

router.get("/")(lambda: {"message": "Variables endpoint"})
