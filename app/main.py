from fastapi import FastAPI
from app.config import settings
from app.routes import auth as auth_routes

app = FastAPI(title=settings.app_name)


app.include_router(auth_routes.router)
