from fastapi import APIRouter

from api.routes.status_routes import status_router
from api.routes.training_routes import training_router
from api.routes.prediction_routes import prediction_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(status_router)
v1_router.include_router(training_router)
v1_router.include_router(prediction_router)
