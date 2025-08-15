from fastapi import FastAPI
from backend.app.database import engine, Base
from backend.app.routers import auth, orders, payment, wallet, ws
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
import os
import asyncio

from backend.app.ai_chat_init import init_ai

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Static file setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(orders.router, prefix="/orders")
app.include_router(payment.router, prefix="/payment")
app.include_router(wallet.router, prefix="/wallet")
app.include_router(ws.router, prefix="/ws")



@app.on_event("startup")
async def on_startup():
    # Khởi tạo database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Load AI model async
    asyncio.create_task(init_ai())



def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Admin API",
        version="1.0.0",
        description="API Docs for Admin",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/docs", include_in_schema=False, response_class=HTMLResponse)
async def custom_docs():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Admin API Docs"
    )


@app.get("/openapi.json", include_in_schema=False)
async def openapi():
    return app.openapi()