from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import products, auth, orders, admin_auth, admin_users, admin_stores, categories, users, chat, templates, delivery, seller

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ALTOQ API",
    version="1.0.0",
    redirect_slashes=False  # Disable automatic trailing slash redirects to prevent CORS issues
)

# Configurar CORS para Angular - DEBE IR ANTES de incluir routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
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

@app.get("/")
def root():
    return {"message": "ALTOQ API - Bienvenido al backend del marketplace"}

@app.get("/health")
def health():
    return {"status": "ok"}
