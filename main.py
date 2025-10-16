from fastapi import FastAPI
from app.variables.routers.views import router as variables_router
from app.core.settings import init_db
app = FastAPI()

@app.get("/", tags=["health"])
def health():
    return {"status": "pong"}


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(variables_router, prefix="/variables", tags=["Variables"])