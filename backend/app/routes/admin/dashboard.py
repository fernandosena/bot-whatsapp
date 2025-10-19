"""
Rotas do Dashboard Admin
Fornece métricas e estatísticas gerais do sistema
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import Dict, List, Any
from bson import ObjectId

from app.middleware.auth import get_current_admin_user
from app.core.database import (
    get_users_collection,
    get_plans_collection,
    get_subscriptions_collection,
    get_audit_logs_collection,
    get_security_logs_collection
)
from app.utils.soft_delete import find_active, count_active

router = APIRouter(tags=["Admin Dashboard"])


@router.get("/stats/overview", dependencies=[Depends(get_current_admin_user)])
async def get_overview_stats():
    """
    Retorna estatísticas gerais do sistema

    - Total de usuários
    - Total de planos
    - Total de assinaturas
    - Receita total
    - Novos usuários (últimos 30 dias)
    - Assinaturas ativas
    """
    users_collection = get_users_collection()
    plans_collection = get_plans_collection()
    subscriptions_collection = get_subscriptions_collection()

    # Total de usuários ativos
    total_users = await count_active(users_collection)

    # Total de planos ativos
    total_plans = await count_active(plans_collection)

    # Total de assinaturas (todas)
    all_subscriptions = await subscriptions_collection.count_documents({"flag_del": False})

    # Assinaturas ativas
    active_subscriptions = await subscriptions_collection.count_documents({
        "flag_del": False,
        "status": "active"
    })

    # Novos usuários (últimos 30 dias)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users = await users_collection.count_documents({
        "flag_del": False,
        "created_at": {"$gte": thirty_days_ago}
    })

    # Calcular receita total (soma de todas assinaturas ativas)
    pipeline = [
        {"$match": {"flag_del": False, "status": "active"}},
        {"$lookup": {
            "from": "plans",
            "localField": "plan_id",
            "foreignField": "_id",
            "as": "plan"
        }},
        {"$unwind": "$plan"},
        {"$group": {
            "_id": None,
            "total_monthly": {"$sum": "$plan.price_monthly"},
            "total_yearly": {"$sum": "$plan.price_yearly"}
        }}
    ]

    revenue_result = await subscriptions_collection.aggregate(pipeline).to_list(length=1)
    total_revenue_monthly = revenue_result[0]["total_monthly"] if revenue_result else 0
    total_revenue_yearly = revenue_result[0]["total_yearly"] if revenue_result else 0

    return {
        "total_users": total_users,
        "total_plans": total_plans,
        "total_subscriptions": all_subscriptions,
        "active_subscriptions": active_subscriptions,
        "new_users_last_30_days": new_users,
        "total_revenue_monthly": total_revenue_monthly,  # em centavos
        "total_revenue_yearly": total_revenue_yearly,  # em centavos
    }


@router.get("/stats/users-growth", dependencies=[Depends(get_current_admin_user)])
async def get_users_growth(days: int = 30):
    """
    Retorna o crescimento de usuários nos últimos N dias
    Agrupa por dia
    """
    users_collection = get_users_collection()

    start_date = datetime.utcnow() - timedelta(days=days)

    pipeline = [
        {"$match": {
            "flag_del": False,
            "created_at": {"$gte": start_date}
        }},
        {"$group": {
            "_id": {
                "year": {"$year": "$created_at"},
                "month": {"$month": "$created_at"},
                "day": {"$dayOfMonth": "$created_at"}
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}},
        {"$project": {
            "date": {
                "$dateFromParts": {
                    "year": "$_id.year",
                    "month": "$_id.month",
                    "day": "$_id.day"
                }
            },
            "count": 1,
            "_id": 0
        }}
    ]

    results = await users_collection.aggregate(pipeline).to_list(length=None)

    return {
        "period_days": days,
        "data": results
    }


@router.get("/stats/subscriptions-by-plan", dependencies=[Depends(get_current_admin_user)])
async def get_subscriptions_by_plan():
    """
    Retorna distribuição de assinaturas por plano
    """
    subscriptions_collection = get_subscriptions_collection()

    pipeline = [
        {"$match": {"flag_del": False, "status": "active"}},
        {"$lookup": {
            "from": "plans",
            "localField": "plan_id",
            "foreignField": "_id",
            "as": "plan"
        }},
        {"$unwind": "$plan"},
        {"$group": {
            "_id": "$plan_id",
            "plan_name": {"$first": "$plan.name"},
            "count": {"$sum": 1},
            "revenue_monthly": {"$sum": "$plan.price_monthly"},
            "revenue_yearly": {"$sum": "$plan.price_yearly"}
        }},
        {"$sort": {"count": -1}}
    ]

    results = await subscriptions_collection.aggregate(pipeline).to_list(length=None)

    formatted_results = []
    for item in results:
        formatted_results.append({
            "plan_id": str(item["_id"]),
            "plan_name": item["plan_name"],
            "subscribers": item["count"],
            "revenue_monthly": item["revenue_monthly"],
            "revenue_yearly": item["revenue_yearly"]
        })

    return {"data": formatted_results}


@router.get("/stats/revenue-trend", dependencies=[Depends(get_current_admin_user)])
async def get_revenue_trend(days: int = 30):
    """
    Retorna tendência de receita nos últimos N dias
    (baseado em quando as assinaturas foram criadas)
    """
    subscriptions_collection = get_subscriptions_collection()

    start_date = datetime.utcnow() - timedelta(days=days)

    pipeline = [
        {"$match": {
            "flag_del": False,
            "status": "active",
            "created_at": {"$gte": start_date}
        }},
        {"$lookup": {
            "from": "plans",
            "localField": "plan_id",
            "foreignField": "_id",
            "as": "plan"
        }},
        {"$unwind": "$plan"},
        {"$group": {
            "_id": {
                "year": {"$year": "$created_at"},
                "month": {"$month": "$created_at"},
                "day": {"$dayOfMonth": "$created_at"}
            },
            "revenue_monthly": {"$sum": "$plan.price_monthly"},
            "revenue_yearly": {"$sum": "$plan.price_yearly"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}},
        {"$project": {
            "date": {
                "$dateFromParts": {
                    "year": "$_id.year",
                    "month": "$_id.month",
                    "day": "$_id.day"
                }
            },
            "revenue_monthly": 1,
            "revenue_yearly": 1,
            "subscriptions": "$count",
            "_id": 0
        }}
    ]

    results = await subscriptions_collection.aggregate(pipeline).to_list(length=None)

    return {
        "period_days": days,
        "data": results
    }


@router.get("/stats/recent-activities", dependencies=[Depends(get_current_admin_user)])
async def get_recent_activities(limit: int = 10):
    """
    Retorna atividades recentes do sistema
    (últimos logins, registros, mudanças de planos, etc)
    """
    audit_logs_collection = get_audit_logs_collection()
    security_logs_collection = get_security_logs_collection()

    # Buscar últimos logs de auditoria
    audit_logs = await audit_logs_collection.find(
        {"flag_del": False}
    ).sort("timestamp", -1).limit(limit).to_list(length=limit)

    # Buscar últimos logs de segurança (logins)
    security_logs = await security_logs_collection.find(
        {"flag_del": False, "action": "login_success"}
    ).sort("timestamp", -1).limit(5).to_list(length=5)

    activities = []

    # Formatar logs de auditoria
    for log in audit_logs:
        activities.append({
            "id": str(log["_id"]),
            "type": "audit",
            "action": log.get("action", "unknown"),
            "description": log.get("description", ""),
            "user_id": str(log.get("user_id")) if log.get("user_id") else None,
            "timestamp": log.get("timestamp"),
            "metadata": log.get("metadata", {})
        })

    # Formatar logs de segurança
    for log in security_logs:
        activities.append({
            "id": str(log["_id"]),
            "type": "security",
            "action": log.get("action", "login"),
            "description": f"Login de {log.get('email', 'usuário')}",
            "user_id": str(log.get("user_id")) if log.get("user_id") else None,
            "timestamp": log.get("timestamp"),
            "metadata": {
                "ip": log.get("ip_address"),
                "device": log.get("device_info", {})
            }
        })

    # Ordenar por timestamp
    activities.sort(key=lambda x: x["timestamp"], reverse=True)

    return {
        "activities": activities[:limit]
    }


@router.get("/stats/subscription-status", dependencies=[Depends(get_current_admin_user)])
async def get_subscription_status():
    """
    Retorna distribuição de assinaturas por status
    """
    subscriptions_collection = get_subscriptions_collection()

    pipeline = [
        {"$match": {"flag_del": False}},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]

    results = await subscriptions_collection.aggregate(pipeline).to_list(length=None)

    status_distribution = {}
    for item in results:
        status_distribution[item["_id"]] = item["count"]

    return {
        "active": status_distribution.get("active", 0),
        "pending": status_distribution.get("pending", 0),
        "canceled": status_distribution.get("canceled", 0),
        "expired": status_distribution.get("expired", 0),
        "trial": status_distribution.get("trial", 0)
    }


@router.get("/stats/top-users", dependencies=[Depends(get_current_admin_user)])
async def get_top_users(limit: int = 10):
    """
    Retorna top usuários (por valor de assinatura ou atividade)
    """
    subscriptions_collection = get_subscriptions_collection()
    users_collection = get_users_collection()

    pipeline = [
        {"$match": {"flag_del": False, "status": "active"}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
        }},
        {"$unwind": "$user"},
        {"$lookup": {
            "from": "plans",
            "localField": "plan_id",
            "foreignField": "_id",
            "as": "plan"
        }},
        {"$unwind": "$plan"},
        {"$project": {
            "user_id": "$user._id",
            "user_name": "$user.full_name",
            "user_email": "$user.email",
            "plan_name": "$plan.name",
            "plan_value": "$plan.price_monthly",
            "created_at": "$user.created_at"
        }},
        {"$sort": {"plan_value": -1}},
        {"$limit": limit}
    ]

    results = await subscriptions_collection.aggregate(pipeline).to_list(length=limit)

    formatted_results = []
    for item in results:
        formatted_results.append({
            "user_id": str(item["user_id"]),
            "name": item["user_name"],
            "email": item["user_email"],
            "plan": item["plan_name"],
            "monthly_value": item["plan_value"],
            "member_since": item["created_at"]
        })

    return {"users": formatted_results}
