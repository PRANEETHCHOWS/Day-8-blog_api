from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.openapi.utils import get_openapi

from auth.auth import create_access_token
from database import Base, engine
from routers.post import router as post_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Blog REST API",
    version="1.0.0",
    description="Production-ready FastAPI Blog API with JWT auth",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


@app.post("/auth/token", tags=["auth"])
def issue_token(username: str = Query(..., min_length=1)):
    token = create_access_token(username=username)
    return {"access_token": token, "token_type": "bearer"}


app.include_router(post_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "HTTPBearer": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    schema["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

