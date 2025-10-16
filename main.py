from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.environments.routes.views import router as environments_router
from app.users.routers.views import router as users_router
from app.core.settings import init_db

app = FastAPI(
    title="Config Service API",
    description="A configuration management service API for managing environments and variables",
    version="1.0.0",
    swagger_ui_parameters={"syntaxHighlight": False}
)

# Add security scheme for Swagger UI
security = OAuth2PasswordBearer(tokenUrl="users/auth/login")

@app.get("/status/", tags=["Health"], summary="Health Check",
         description="Simple health check endpoint that responds with 'pong'")
def status():
    """Health Check: Responds with pong"""
    return {"message": "pong"}

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(environments_router, prefix="/environments", tags=["Environments"])
app.include_router(users_router, prefix="/users", tags=["Users"])