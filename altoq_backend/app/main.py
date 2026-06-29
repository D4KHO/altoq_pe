from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import products, auth, orders, admin_auth, admin_users, admin_stores, categories, users, chat, templates, delivery, seller, metrics, ai_assistant, ai_product_assistant, stores

# Las tablas ahora se crean con Alembic (migraciones).
# Ejecuta: python -m alembic upgrade head
# Ya no se usa: Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ALTOQ API",
    version="1.0.0",
    redirect_slashes=False,  # Disable automatic trailing slash redirects to prevent CORS issues
    swagger_ui_init_oauth={
        "clientId": "altoq-client",
        "appName": "ALTOQ API",
        "usePkceWithAuthorizationCodeGrant": False,
    },
    openapi_security=[
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    ]
)

# Configurar CORS para Angular - DEBE IR ANTES de incluir routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://[::1]:4200",
        "https://altoq-pe.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(orders.router)
# Admin routes
app.include_router(admin_auth.router)
app.include_router(admin_users.router)
app.include_router(admin_stores.router)
# AltoQ features
app.include_router(chat.router)
app.include_router(templates.router)
app.include_router(delivery.router)
app.include_router(seller.router)
app.include_router(ai_assistant.router)
app.include_router(ai_product_assistant.router)
app.include_router(metrics.router)
app.include_router(stores.router)

from fastapi.staticfiles import StaticFiles
import os

os.makedirs("static/uploads/products", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "ALTOQ API - Bienvenido al backend del marketplace"}

@app.get("/health")
def health():
    return {"status": "ok"}
