"""
Scheduler - APScheduler Configuration
Sistema de agendamento de tarefas automáticas
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Instância global do scheduler
scheduler = AsyncIOScheduler()


def start_scheduler():
    """
    Inicia o scheduler e registra todos os jobs
    """
    if scheduler.running:
        logger.warning("Scheduler já está rodando")
        return

    logger.info("🕐 Iniciando scheduler...")

    # Importar jobs (evitar import circular)
    from app.jobs.subscription_jobs import (
        check_expiring_subscriptions,
        process_expired_subscriptions,
        renew_subscriptions
    )
    from app.jobs.cleanup_jobs import (
        cleanup_old_sessions,
        cleanup_pending_payments
    )

    # ===== RENOVAÇÃO DE ASSINATURAS =====

    # Verificar assinaturas expirando (avisar 3 dias antes)
    scheduler.add_job(
        check_expiring_subscriptions,
        trigger=CronTrigger(hour=9, minute=0),  # Todo dia às 9h
        id='check_expiring_subscriptions',
        name='Verificar assinaturas expirando',
        replace_existing=True,
        max_instances=1
    )
    logger.info("✓ Job registrado: check_expiring_subscriptions (diário 9h)")

    # Processar assinaturas expiradas
    scheduler.add_job(
        process_expired_subscriptions,
        trigger=CronTrigger(hour=0, minute=30),  # Todo dia às 00:30
        id='process_expired_subscriptions',
        name='Processar assinaturas expiradas',
        replace_existing=True,
        max_instances=1
    )
    logger.info("✓ Job registrado: process_expired_subscriptions (diário 00:30)")

    # Renovar assinaturas automaticamente (Stripe)
    scheduler.add_job(
        renew_subscriptions,
        trigger=CronTrigger(hour=2, minute=0),  # Todo dia às 2h
        id='renew_subscriptions',
        name='Renovar assinaturas automáticas',
        replace_existing=True,
        max_instances=1
    )
    logger.info("✓ Job registrado: renew_subscriptions (diário 2h)")

    # ===== LIMPEZA =====

    # Limpar sessões antigas (expiradas há mais de 30 dias)
    scheduler.add_job(
        cleanup_old_sessions,
        trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),  # Domingo às 3h
        id='cleanup_old_sessions',
        name='Limpar sessões antigas',
        replace_existing=True,
        max_instances=1
    )
    logger.info("✓ Job registrado: cleanup_old_sessions (semanal domingo 3h)")

    # Limpar pagamentos pendentes antigos (>7 dias)
    scheduler.add_job(
        cleanup_pending_payments,
        trigger=CronTrigger(day=1, hour=4, minute=0),  # Dia 1 de cada mês às 4h
        id='cleanup_pending_payments',
        name='Limpar pagamentos pendentes antigos',
        replace_existing=True,
        max_instances=1
    )
    logger.info("✓ Job registrado: cleanup_pending_payments (mensal dia 1)")

    # Iniciar scheduler
    scheduler.start()
    logger.info("✅ Scheduler iniciado com sucesso!")
    logger.info(f"📋 Total de jobs registrados: {len(scheduler.get_jobs())}")


def stop_scheduler():
    """
    Para o scheduler gracefully
    """
    if not scheduler.running:
        logger.warning("Scheduler não está rodando")
        return

    logger.info("⏹ Parando scheduler...")
    scheduler.shutdown(wait=True)
    logger.info("✅ Scheduler parado com sucesso!")


def list_jobs():
    """
    Lista todos os jobs registrados

    Returns:
        List de dicts com informações dos jobs
    """
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
            'trigger': str(job.trigger)
        })
    return jobs


def get_job_info(job_id: str):
    """
    Obtém informações de um job específico

    Args:
        job_id: ID do job

    Returns:
        Dict com informações ou None
    """
    job = scheduler.get_job(job_id)
    if not job:
        return None

    return {
        'id': job.id,
        'name': job.name,
        'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
        'trigger': str(job.trigger),
        'max_instances': job.max_instances,
        'pending': job.pending
    }


def pause_job(job_id: str):
    """
    Pausa um job específico
    """
    job = scheduler.get_job(job_id)
    if job:
        scheduler.pause_job(job_id)
        logger.info(f"⏸ Job pausado: {job_id}")
        return True
    return False


def resume_job(job_id: str):
    """
    Resume um job pausado
    """
    job = scheduler.get_job(job_id)
    if job:
        scheduler.resume_job(job_id)
        logger.info(f"▶ Job resumido: {job_id}")
        return True
    return False


def trigger_job_now(job_id: str):
    """
    Executa um job imediatamente (fora do schedule)

    Args:
        job_id: ID do job

    Returns:
        bool: True se sucesso
    """
    job = scheduler.get_job(job_id)
    if job:
        job.modify(next_run_time=datetime.now())
        logger.info(f"🚀 Job disparado manualmente: {job_id}")
        return True
    return False
