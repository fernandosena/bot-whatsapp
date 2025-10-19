"""
Rate Limiting Middleware

Proteção contra abuso de API usando sliding window algorithm
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio
from collections import defaultdict
import time


class RateLimiter:
    """
    Rate limiter usando sliding window com memória em dict

    Para produção, use Redis para compartilhar entre instâncias
    """

    def __init__(self):
        # requests_log[identifier][endpoint] = [(timestamp, count), ...]
        self.requests_log: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self.cleanup_task: Optional[asyncio.Task] = None

    def _get_identifier(self, request: Request) -> str:
        """
        Obtém identificador único do cliente

        Prioridade:
        1. user_id (se autenticado)
        2. IP address
        """
        # Tentar pegar user do estado (se autenticado)
        user = getattr(request.state, "user", None)
        if user and user.get("_id"):
            return f"user:{user['_id']}"

        # Usar IP
        client_ip = request.client.host
        # Check for proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        return f"ip:{client_ip}"

    def _get_window_size(self, endpoint: str) -> tuple:
        """
        Define janela de tempo e limite por endpoint

        Returns:
            (window_seconds, max_requests)
        """
        # Auth endpoints - mais restritivo
        if "/auth/login" in endpoint or "/auth/register" in endpoint:
            return (60, 5)  # 5 requests por minuto

        # Password reset - muito restritivo
        if "/auth/password-reset" in endpoint:
            return (300, 3)  # 3 requests por 5 minutos

        # Payment endpoints - moderado
        if "/payments/" in endpoint:
            return (60, 20)  # 20 requests por minuto

        # Admin endpoints - liberal (já tem auth)
        if "/admin/" in endpoint:
            return (60, 100)  # 100 requests por minuto

        # Webhooks - sem limite (vêm de gateways)
        if "/webhook" in endpoint:
            return (0, float('inf'))  # Sem limite

        # Health check - sem limite
        if endpoint in ["/health", "/"]:
            return (0, float('inf'))

        # Default - moderado
        return (60, 60)  # 60 requests por minuto

    def is_allowed(self, request: Request) -> tuple:
        """
        Verifica se request é permitido

        Returns:
            (allowed: bool, retry_after: int)
        """
        identifier = self._get_identifier(request)
        endpoint = request.url.path

        window_seconds, max_requests = self._get_window_size(endpoint)

        # Sem limite
        if window_seconds == 0:
            return (True, 0)

        now = time.time()
        window_start = now - window_seconds

        # Limpar requests antigas
        requests = self.requests_log[identifier][endpoint]
        self.requests_log[identifier][endpoint] = [
            (ts, count) for ts, count in requests
            if ts > window_start
        ]

        # Contar requests na janela
        total_requests = sum(count for ts, count in self.requests_log[identifier][endpoint])

        if total_requests >= max_requests:
            # Calcular retry_after
            oldest_request = min(self.requests_log[identifier][endpoint], key=lambda x: x[0])
            retry_after = int(oldest_request[0] + window_seconds - now) + 1
            return (False, retry_after)

        # Adicionar request atual
        self.requests_log[identifier][endpoint].append((now, 1))

        return (True, 0)

    def get_rate_limit_headers(self, request: Request) -> dict:
        """
        Retorna headers de rate limit

        Returns:
            Headers com informações de limite
        """
        identifier = self._get_identifier(request)
        endpoint = request.url.path

        window_seconds, max_requests = self._get_window_size(endpoint)

        # Sem limite
        if window_seconds == 0:
            return {}

        now = time.time()
        window_start = now - window_seconds

        # Contar requests na janela
        requests = [
            (ts, count) for ts, count in self.requests_log[identifier].get(endpoint, [])
            if ts > window_start
        ]
        total_requests = sum(count for ts, count in requests)

        remaining = max(0, max_requests - total_requests)

        # Calcular reset time
        if requests:
            oldest = min(requests, key=lambda x: x[0])
            reset = int(oldest[0] + window_seconds)
        else:
            reset = int(now + window_seconds)

        return {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset),
            "X-RateLimit-Window": str(window_seconds)
        }

    async def cleanup_old_requests(self):
        """
        Task em background para limpar requests antigos
        """
        while True:
            await asyncio.sleep(300)  # A cada 5 minutos

            now = time.time()
            cutoff = now - 3600  # Remove tudo mais velho que 1 hora

            # Limpar logs antigos
            for identifier in list(self.requests_log.keys()):
                for endpoint in list(self.requests_log[identifier].keys()):
                    self.requests_log[identifier][endpoint] = [
                        (ts, count) for ts, count in self.requests_log[identifier][endpoint]
                        if ts > cutoff
                    ]

                    # Remover endpoint vazio
                    if not self.requests_log[identifier][endpoint]:
                        del self.requests_log[identifier][endpoint]

                # Remover identifier vazio
                if not self.requests_log[identifier]:
                    del self.requests_log[identifier]

    def start_cleanup_task(self):
        """Inicia task de limpeza"""
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self.cleanup_old_requests())

    def stop_cleanup_task(self):
        """Para task de limpeza"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            self.cleanup_task = None


# Instância global
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware FastAPI para rate limiting
    """

    async def dispatch(self, request: Request, call_next):
        # Verificar rate limit
        allowed, retry_after = rate_limiter.is_allowed(request)

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "message": "Limite de requisições excedido. Tente novamente mais tarde.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    **rate_limiter.get_rate_limit_headers(request)
                }
            )

        # Processar request
        response = await call_next(request)

        # Adicionar headers de rate limit
        for key, value in rate_limiter.get_rate_limit_headers(request).items():
            response.headers[key] = value

        return response


def start_rate_limiter():
    """Inicia o rate limiter (chamar no startup)"""
    rate_limiter.start_cleanup_task()
    print("✅ Rate Limiter iniciado")


def stop_rate_limiter():
    """Para o rate limiter (chamar no shutdown)"""
    rate_limiter.stop_cleanup_task()
    print("🛑 Rate Limiter parado")


# Dependency para endpoints específicos
async def check_rate_limit(request: Request):
    """
    Dependency para verificar rate limit em endpoints específicos

    Usage:
        @router.post("/endpoint", dependencies=[Depends(check_rate_limit)])
    """
    allowed, retry_after = rate_limiter.is_allowed(request)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Too Many Requests",
                "message": "Limite de requisições excedido.",
                "retry_after": retry_after
            },
            headers={"Retry-After": str(retry_after)}
        )

    return True
