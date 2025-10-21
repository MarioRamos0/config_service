from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.environments.routes.views import router as environments_router
from app.users.routers.views import router as users_router
from app.core.settings import init_db
from app.variables.routers.views import router as variables_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    print("App shutting down...")

app = FastAPI(
    title="Config Service API",
    description="A configuration management service API for managing environments and variables",
    version="1.0.0",
    swagger_ui_parameters={"syntaxHighlight": False},
    lifespan=lifespan,
)

security = OAuth2PasswordBearer(tokenUrl="users/auth/login")

@app.get("/status/", tags=["Health"], summary="Health Check",
         description="Simple health check endpoint that responds with 'pong'")
def status():
    return {"message": "pong"}


app.include_router(environments_router, prefix="/environments", tags=["Environments"])
app.include_router(variables_router, prefix="/environments/{env_name}/variables", tags=["Variables"])
app.include_router(users_router, prefix="/users", tags=["Users"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)