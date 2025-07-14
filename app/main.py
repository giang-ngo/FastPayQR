from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, orders

app = FastAPI()

app.include_router(auth.router)
app.include_router(orders.router)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
