from fastapi import FastAPI, Body, APIRouter, Depends

# from api.v1.endpoints import itemApi, userApi, authApi,  gauth, fbauth, alexApi, shopApi, lineLogin, fileApi, eCouponApi, testApi #genapiApi

from api.v1.endpoints import salepieApi


api_router = APIRouter()


api_router.include_router(salepieApi.router, prefix="/salepie-api")

# api_router.include_router(itemApi.router, prefix="/item")
# api_router.include_router(authApi.router, prefix="/auth")
# api_router.include_router(gauth.router, prefix="/gauth")
# api_router.include_router(fbauth.router, prefix="/fbauth")
# api_router.include_router(userApi.router, prefix="/user")
# api_router.include_router(alexApi.router, prefix="/alex")
# api_router.include_router(genapiApi.router, prefix="/genapi")
# api_router.include_router(shopApi.router, prefix="/shop")
# api_router.include_router(lineLogin.router, prefix="/line")
# api_router.include_router(testApi.router, prefix="/test")

# api_router.include_router(eCouponApi.router, prefix="/ecoupon")