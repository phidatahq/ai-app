from fastapi import APIRouter

from api.routes.status_routes import status_router
from api.routes.prompt_routes import prompt_router
from api.routes.agent_routes import agent_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(status_router)
v1_router.include_router(prompt_router)
v1_router.include_router(agent_router)
