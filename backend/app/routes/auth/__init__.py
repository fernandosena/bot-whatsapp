"""
Auth Routes Package

Combina todas as rotas de autenticação
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .password_reset import router as password_reset_router

# Router principal que combina todas as rotas de auth
router = APIRouter()

# Incluir rotas de auth básica
router.include_router(auth_router)

# Incluir rotas de password reset
router.include_router(password_reset_router)
