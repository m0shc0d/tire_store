from fastapi import APIRouter

import app.user.router
import app.auth.router
from app.api import utils

api_router = APIRouter()
api_router.include_router(app.auth.router.router, prefix="/auth", tags=["login"])
api_router.include_router(app.user.router.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
