from fastapi import APIRouter

from app.api.routes import predictor, auth, items, users, notifications

router = APIRouter()
router.include_router(predictor.router, tags=["predictor"], prefix="/v1")
router.include_router(auth.router, tags=["auth"], prefix="/v1/auth")
router.include_router(users.router, tags=["users"], prefix="/v1/users")
router.include_router(items.router, tags=["items"], prefix="/v1/items")
router.include_router(notifications.router, tags=["notifications"], prefix="/v1/notifications")
