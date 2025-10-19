"""
Rotas Admin - Gerenciamento de Planos
CRUD completo para planos configuráveis
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from datetime import datetime

from app.models.plan import PlanCreate, PlanUpdate, PlanResponse, PlanInDB
from app.models.subscription import SubscriptionInDB
from app.core.database import get_plans_collection, get_subscriptions_collection
from app.utils.soft_delete import (
    find_active,
    find_one_active,
    soft_delete,
    restore_deleted,
    find_deleted,
    count_active
)
from app.utils.audit import (
    log_plan_created,
    log_plan_updated,
    log_plan_deleted,
    log_data_restored
)

router = APIRouter()


def slugify(text: str) -> str:
    """Converte texto para slug"""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


# TODO: Implementar middleware de autenticação
# def get_current_admin_user():
#     """Verifica se usuário é admin"""
#     pass


@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(plan: PlanCreate):
    """
    Cria novo plano (apenas admin)

    - **name**: Nome do plano
    - **description**: Descrição do plano
    - **price_monthly**: Preço mensal em centavos
    - **price_yearly**: Preço anual em centavos (opcional)
    - **features**: Funcionalidades do plano
    """
    plans_collection = get_plans_collection()

    # Gera slug automaticamente
    plan_slug = slugify(plan.name)

    # Verifica se já existe plano com mesmo slug
    existing = await find_one_active(plans_collection, {"slug": plan_slug})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um plano com o nome '{plan.name}'"
        )

    # Cria plano
    plan_dict = plan.model_dump()
    plan_dict["slug"] = plan_slug
    plan_dict["flag_del"] = False
    plan_dict["created_at"] = datetime.utcnow()
    plan_dict["updated_at"] = datetime.utcnow()
    plan_dict["deleted_at"] = None
    plan_dict["deleted_by"] = None
    plan_dict["deleted_reason"] = None
    # plan_dict["created_by"] = current_admin_id  # TODO: pegar do auth

    result = await plans_collection.insert_one(plan_dict)
    plan_dict["_id"] = result.inserted_id

    # Log de auditoria
    await log_plan_created(
        admin_id=str(result.inserted_id),  # TODO: usar admin real
        plan_id=str(result.inserted_id),
        plan_name=plan.name
    )

    # Converte ObjectId para string para retornar
    plan_dict["_id"] = str(plan_dict["_id"])
    if "created_by" in plan_dict and plan_dict["created_by"]:
        plan_dict["created_by"] = str(plan_dict["created_by"])

    return plan_dict


@router.get("/", response_model=List[PlanResponse])
async def list_plans(
    include_inactive: bool = False,
    include_deleted: bool = False
):
    """
    Lista todos os planos

    - **include_inactive**: Incluir planos inativos
    - **include_deleted**: Incluir planos deletados (apenas admin)
    """
    plans_collection = get_plans_collection()

    if include_deleted:
        # Busca TODOS (incluindo deletados) - apenas admin
        query = {}
        plans = await plans_collection.find(query).to_list(length=None)
    else:
        # Busca apenas ativos
        query = {"flag_del": False}
        if not include_inactive:
            query["status"] = "active"
        plans = await plans_collection.find(query).to_list(length=None)

    # Converte ObjectId para string
    for plan in plans:
        plan["_id"] = str(plan["_id"])
        if "created_by" in plan and plan["created_by"]:
            plan["created_by"] = str(plan["created_by"])

    return plans


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str):
    """Busca plano por ID"""
    plans_collection = get_plans_collection()

    if not ObjectId.is_valid(plan_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )

    plan = await find_one_active(plans_collection, {"_id": ObjectId(plan_id)})

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )

    # Converte ObjectId para string
    plan["_id"] = str(plan["_id"])
    if "created_by" in plan and plan["created_by"]:
        plan["created_by"] = str(plan["created_by"])

    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(plan_id: str, plan_update: PlanUpdate):
    """
    Atualiza plano existente (apenas admin)
    """
    plans_collection = get_plans_collection()

    if not ObjectId.is_valid(plan_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )

    # Verifica se plano existe
    existing_plan = await find_one_active(plans_collection, {"_id": ObjectId(plan_id)})
    if not existing_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )

    # Prepara dados para atualização
    update_data = plan_update.model_dump(exclude_unset=True)

    # Se mudar o nome, atualiza o slug também
    if "name" in update_data:
        update_data["slug"] = slugify(update_data["name"])

    update_data["updated_at"] = datetime.utcnow()

    # Atualiza
    await plans_collection.update_one(
        {"_id": ObjectId(plan_id)},
        {"$set": update_data}
    )

    # Log de auditoria
    await log_plan_updated(
        admin_id=plan_id,  # TODO: usar admin real
        plan_id=plan_id,
        changes=update_data
    )

    # Busca plano atualizado
    updated_plan = await find_one_active(plans_collection, {"_id": ObjectId(plan_id)})
    updated_plan["_id"] = str(updated_plan["_id"])
    if "created_by" in updated_plan and updated_plan["created_by"]:
        updated_plan["created_by"] = str(updated_plan["created_by"])

    return updated_plan


@router.post("/{plan_id}/toggle-status")
async def toggle_plan_status(plan_id: str):
    """
    Ativa/Desativa plano
    """
    plans_collection = get_plans_collection()

    if not ObjectId.is_valid(plan_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )

    plan = await find_one_active(plans_collection, {"_id": ObjectId(plan_id)})
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )

    new_status = "inactive" if plan["status"] == "active" else "active"

    await plans_collection.update_one(
        {"_id": ObjectId(plan_id)},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
    )

    return {
        "success": True,
        "new_status": new_status,
        "message": f"Plano {new_status}"
    }


@router.delete("/{plan_id}")
async def delete_plan(plan_id: str, reason: str = ""):
    """
    "Exclui" plano (soft delete)

    ⚠️ Não permite exclusão se houver assinaturas ativas
    """
    plans_collection = get_plans_collection()
    subscriptions_collection = get_subscriptions_collection()

    if not ObjectId.is_valid(plan_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )

    # Verifica se plano existe
    plan = await find_one_active(plans_collection, {"_id": ObjectId(plan_id)})
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )

    # Verifica se há assinaturas ativas usando este plano
    active_subs = await count_active(
        subscriptions_collection,
        {"plan_id": ObjectId(plan_id), "status": "active"}
    )

    if active_subs > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível excluir. {active_subs} assinatura(s) ativa(s) usam este plano."
        )

    # Soft delete
    await soft_delete(
        plans_collection,
        plan_id,
        deleted_by=plan_id,  # TODO: usar admin real
        reason=reason
    )

    # Log de auditoria
    await log_plan_deleted(
        admin_id=plan_id,  # TODO: usar admin real
        plan_id=plan_id,
        reason=reason
    )

    return {
        "success": True,
        "message": "Plano arquivado com sucesso"
    }


@router.get("/deleted/list", response_model=List[PlanResponse])
async def list_deleted_plans():
    """
    Lista planos deletados (soft delete)
    Apenas para admin - painel de recuperação
    """
    plans_collection = get_plans_collection()

    deleted_plans = await find_deleted(plans_collection)

    # Converte ObjectId para string
    for plan in deleted_plans:
        plan["_id"] = str(plan["_id"])
        if "created_by" in plan and plan["created_by"]:
            plan["created_by"] = str(plan["created_by"])
        if "deleted_by" in plan and plan["deleted_by"]:
            plan["deleted_by"] = str(plan["deleted_by"])

    return deleted_plans


@router.post("/deleted/{plan_id}/restore")
async def restore_plan(plan_id: str):
    """
    Restaura plano deletado
    Apenas para admin
    """
    plans_collection = get_plans_collection()

    if not ObjectId.is_valid(plan_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )

    result = await restore_deleted(plans_collection, plan_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )

    # Log de auditoria
    await log_data_restored(
        admin_id=plan_id,  # TODO: usar admin real
        collection="plans",
        record_id=plan_id
    )

    return {
        "success": True,
        "message": "Plano restaurado com sucesso"
    }


@router.get("/stats/summary")
async def get_plans_stats():
    """
    Estatísticas de planos
    """
    plans_collection = get_plans_collection()
    subscriptions_collection = get_subscriptions_collection()

    total_active = await count_active(plans_collection, {"status": "active"})
    total_inactive = await count_active(plans_collection, {"status": "inactive"})
    total_deleted = await plans_collection.count_documents({"flag_del": True})

    # Planos mais populares (com mais assinaturas)
    pipeline = [
        {"$match": {"flag_del": False, "status": "active"}},
        {
            "$lookup": {
                "from": "subscriptions",
                "let": {"plan_id": "$_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$plan_id", "$$plan_id"]},
                                    {"$eq": ["$flag_del", False]},
                                    {"$eq": ["$status", "active"]}
                                ]
                            }
                        }
                    }
                ],
                "as": "subscriptions"
            }
        },
        {
            "$project": {
                "name": 1,
                "slug": 1,
                "subscribers_count": {"$size": "$subscriptions"}
            }
        },
        {"$sort": {"subscribers_count": -1}},
        {"$limit": 5}
    ]

    popular_plans = await plans_collection.aggregate(pipeline).to_list(length=5)

    # Converte ObjectId para string
    for plan in popular_plans:
        plan["_id"] = str(plan["_id"])

    return {
        "total_active": total_active,
        "total_inactive": total_inactive,
        "total_deleted": total_deleted,
        "popular_plans": popular_plans
    }
