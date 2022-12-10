from fastapi import APIRouter

from user.app.routers import user, challenge, verify, publish

api_router = APIRouter()
api_router.include_router(user.router, prefix='/user', tags=['user'])
api_router.include_router(publish.router, prefix='/publish', tags=['publication'])
api_router.include_router(challenge.router, prefix='/challenge', tags=['challenge'])
api_router.include_router(verify.router, prefix='/verify', tags=['verification'])

@api_router.get('/')
async def user():
    return {"message": "Hello, World"}
