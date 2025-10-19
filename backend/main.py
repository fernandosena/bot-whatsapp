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

# Importar scheduler
from app.core.scheduler import start_scheduler, stop_scheduler

# Importar rotas
from app.routes.admin import plans as admin_plans_routes
from app.routes.admin import dashboard as admin_dashboard_routes
from app.routes.admin import jobs as admin_jobs_routes
from app.routes.auth import auth as auth_routes
from app.routes.users import profile as profile_routes
from app.routes.payments import mercadopago as mercadopago_routes
from app.routes.payments import stripe as stripe_routes
from app.routes.payments import paypal as paypal_routes
from app.routes.payments import history as payment_history_routes

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    print("🚀 Iniciando aplicação...")
    await connect_to_mongo()

    # Iniciar scheduler (cron jobs)
    enable_scheduler = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
    if enable_scheduler:
        start_scheduler()
    else:
        print("⏸ Scheduler desabilitado (ENABLE_SCHEDULER=false)")

    print("✅ Aplicação pronta!")

    yield

    # Shutdown
    print("🛑 Encerrando aplicação...")

    # Parar scheduler
    if enable_scheduler:
        stop_scheduler()

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
app.include_router(admin_jobs_routes.router, prefix="/api/admin/jobs", tags=["Admin - Jobs"])
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile_routes.router, prefix="/api/profile", tags=["User Profile"])

# Rotas de pagamento
app.include_router(mercadopago_routes.router, prefix="/api/payments/mercadopago", tags=["Payments - Mercado Pago"])
app.include_router(stripe_routes.router, prefix="/api/payments/stripe", tags=["Payments - Stripe"])
app.include_router(paypal_routes.router, prefix="/api/payments/paypal", tags=["Payments - PayPal"])
app.include_router(payment_history_routes.router, prefix="/api/payments", tags=["Payments - History"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
