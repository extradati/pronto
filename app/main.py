from app.api.routes.api import router as api_router
from app.core.config import API_PREFIX, DEBUG, MEMOIZATION_FLAG, PROJECT_NAME, VERSION
from app.core.events import create_start_app_handler
from fastapi import FastAPI
from app.core.database import engine
from app.models.models import Base


def get_application() -> FastAPI:
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)
    application.include_router(api_router, prefix=API_PREFIX)
    if MEMOIZATION_FLAG:
        application.add_event_handler("startup", create_start_app_handler(application))
    return application


app = get_application()
