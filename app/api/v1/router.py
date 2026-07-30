from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.castles import router as castles_router
from app.api.v1.health import router as health_router
from app.api.v1.journals import public_router as public_journals_router
from app.api.v1.journals import router as journals_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(castles_router)
router.include_router(health_router)
router.include_router(journals_router)
router.include_router(public_journals_router)
