from fastapi import FastAPI

from auth import router as auth_router
from user import router as users_router, user_repository
from product import router as products_router
from order import router as orders_router
from shipment import router as shipments_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(shipments_router)
