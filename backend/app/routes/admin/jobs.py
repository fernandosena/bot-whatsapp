"""
Admin Jobs Routes - Gerenciamento de Cron Jobs

Endpoints para visualizar e controlar jobs agendados
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from datetime import datetime

from app.core.scheduler import (
    list_jobs,
    get_job_info,
    pause_job,
    resume_job,
    trigger_job_now
)
from app.middleware.auth import get_current_user, require_admin

router = APIRouter()


@router.get("/jobs", dependencies=[Depends(require_admin)])
async def get_all_jobs():
    """
    Lista todos os jobs agendados

    Requer: Admin

    Returns:
        Lista de jobs com informações
    """
    try:
        jobs = list_jobs()

        return {
            "total": len(jobs),
            "jobs": jobs
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar jobs: {str(e)}"
        )


@router.get("/jobs/{job_id}", dependencies=[Depends(require_admin)])
async def get_job(job_id: str):
    """
    Obtém informações detalhadas de um job

    Args:
        job_id: ID do job

    Requer: Admin

    Returns:
        Informações do job
    """
    try:
        job_info = get_job_info(job_id)

        if not job_info:
            raise HTTPException(
                status_code=404,
                detail=f"Job não encontrado: {job_id}"
            )

        return job_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter job: {str(e)}"
        )


@router.post("/jobs/{job_id}/pause", dependencies=[Depends(require_admin)])
async def pause_job_endpoint(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Pausa um job agendado

    Args:
        job_id: ID do job

    Requer: Admin

    Returns:
        Confirmação
    """
    try:
        success = pause_job(job_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Job não encontrado: {job_id}"
            )

        return {
            "success": True,
            "message": f"Job '{job_id}' pausado com sucesso",
            "paused_by": current_user.get("email"),
            "paused_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao pausar job: {str(e)}"
        )


@router.post("/jobs/{job_id}/resume", dependencies=[Depends(require_admin)])
async def resume_job_endpoint(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Resume um job pausado

    Args:
        job_id: ID do job

    Requer: Admin

    Returns:
        Confirmação
    """
    try:
        success = resume_job(job_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Job não encontrado: {job_id}"
            )

        return {
            "success": True,
            "message": f"Job '{job_id}' resumido com sucesso",
            "resumed_by": current_user.get("email"),
            "resumed_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao resumir job: {str(e)}"
        )


@router.post("/jobs/{job_id}/trigger", dependencies=[Depends(require_admin)])
async def trigger_job_endpoint(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Executa um job manualmente (fora do schedule)

    Args:
        job_id: ID do job

    Requer: Admin

    Returns:
        Confirmação
    """
    try:
        success = trigger_job_now(job_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Job não encontrado: {job_id}"
            )

        return {
            "success": True,
            "message": f"Job '{job_id}' disparado manualmente",
            "triggered_by": current_user.get("email"),
            "triggered_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao disparar job: {str(e)}"
        )


@router.get("/jobs/stats/summary", dependencies=[Depends(require_admin)])
async def get_jobs_summary():
    """
    Resumo dos jobs agendados

    Requer: Admin

    Returns:
        Estatísticas dos jobs
    """
    try:
        jobs = list_jobs()

        # Calcular próxima execução mais próxima
        next_runs = [
            datetime.fromisoformat(job["next_run"])
            for job in jobs
            if job["next_run"]
        ]

        next_run = min(next_runs) if next_runs else None

        return {
            "total_jobs": len(jobs),
            "next_execution": next_run.isoformat() if next_run else None,
            "jobs_by_type": {
                "subscription_jobs": len([j for j in jobs if "subscription" in j["id"]]),
                "cleanup_jobs": len([j for j in jobs if "cleanup" in j["id"]])
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter resumo: {str(e)}"
        )
