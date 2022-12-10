from fastapi import APIRouter

from trustedauthority.app.routers import digital_object, source, user, auth, verify, publish

api_router = APIRouter()
api_router.include_router(digital_object.router, prefix='/objects', tags=['objects'])
api_router.include_router(source.router, prefix='/apps', tags=['apps'])
api_router.include_router(user.router, prefix='/users', tags=['user'])
api_router.include_router(verify.router, prefix='/verify', tags=['verification'])
api_router.include_router(publish.router, prefix='/challenge', tags=['publication'])
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])

@api_router.get('/')
async def trusted_authority():
    return {"message": "Hello, World"}
