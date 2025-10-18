"""
WhatsApp Business SaaS - Backend FastAPI
Main Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Importar conexão MongoDB
from app.core.database import connect_to_mongo, close_mongo_connection

# Importar rotas
from app.routes.admin import plans as admin_plans_routes
from app.routes.admin import dashboard as admin_dashboard_routes
from app.routes.auth import auth as auth_routes

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    print("🚀 Iniciando aplicação...")
    await connect_to_mongo()
    print("✅ Aplicação pronta!")

    yield

    # Shutdown
    print("🛑 Encerrando aplicação...")
    await close_mongo_connection()
    print("👋 Aplicação encerrada!")


# Criar instância FastAPI
app = FastAPI(
    title="WhatsApp Business SaaS API",
    description="API completa para gerenciamento de WhatsApp Business com sistema de planos configuráveis",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log de todas as requisições"""
    print(f"📨 {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"📤 Status: {response.status_code}")
    return response


# Health Check
@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "service": "WhatsApp Business SaaS API",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "WhatsApp Business SaaS API",
        "docs": "/docs",
        "health": "/health"
    }


# Exception handler global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global de exceções"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": request.url.path
        }
    )


# Incluir rotas
app.include_router(admin_plans_routes.router, prefix="/api/admin/plans", tags=["Admin - Plans"])
app.include_router(admin_dashboard_routes.router, prefix="/api/admin/dashboard", tags=["Admin - Dashboard"])
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
