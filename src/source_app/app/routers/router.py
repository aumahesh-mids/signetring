from fastapi import APIRouter

from source_app.app.routers import app

api_router = APIRouter()
api_router.include_router(app.router, prefix='/app', tags=['app'])

@api_router.get('/')
async def app():
    return {"message": "Hello, World"}
