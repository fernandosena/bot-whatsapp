"""
Sistema de Soft Delete - NUNCA DELETAR DADOS FISICAMENTE!

Este módulo implementa o padrão de soft delete onde registros são marcados
como deletados (flag_del=True) ao invés de serem removidos do banco.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId


async def find_active(collection, query: Dict = None) -> List[Dict]:
    """
    Busca apenas registros ativos (não deletados)

    Args:
        collection: Collection do MongoDB
        query: Filtros adicionais (opcional)

    Returns:
        Lista de registros ativos
    """
    if query is None:
        query = {}

    query['flag_del'] = False
    return await collection.find(query).to_list(length=None)


async def find_one_active(collection, query: Dict) -> Optional[Dict]:
    """
    Busca um único registro ativo (não deletado)

    Args:
        collection: Collection do MongoDB
        query: Filtros de busca

    Returns:
        Registro encontrado ou None
    """
    query['flag_del'] = False
    return await collection.find_one(query)


async def find_all_including_deleted(collection, query: Dict = None) -> List[Dict]:
    """
    Busca TODOS os registros (incluindo deletados)
    APENAS PARA USO ADMINISTRATIVO!

    Args:
        collection: Collection do MongoDB
        query: Filtros adicionais (opcional)

    Returns:
        Lista de todos os registros
    """
    if query is None:
        query = {}

    return await collection.find(query).to_list(length=None)


async def count_active(collection, query: Dict = None) -> int:
    """
    Conta registros ativos (não deletados)

    Args:
        collection: Collection do MongoDB
        query: Filtros adicionais (opcional)

    Returns:
        Quantidade de registros ativos
    """
    if query is None:
        query = {}

    query['flag_del'] = False
    return await collection.count_documents(query)


async def soft_delete(
    collection,
    record_id: str,
    deleted_by: str,
    reason: str = ""
) -> Dict:
    """
    Marca registro como excluído (soft delete)

    Args:
        collection: Collection do MongoDB
        record_id: ID do registro a ser deletado
        deleted_by: ID do usuário que está deletando
        reason: Motivo da exclusão (opcional)

    Returns:
        Resultado da operação
    """
    result = await collection.update_one(
        {"_id": ObjectId(record_id)},
        {
            "$set": {
                "flag_del": True,
                "deleted_at": datetime.utcnow(),
                "deleted_by": ObjectId(deleted_by) if deleted_by else None,
                "deleted_reason": reason
            }
        }
    )

    return {
        "success": result.modified_count > 0,
        "modified_count": result.modified_count
    }


async def soft_delete_many(
    collection,
    query: Dict,
    deleted_by: str,
    reason: str = ""
) -> Dict:
    """
    Marca múltiplos registros como excluídos (soft delete em massa)

    Args:
        collection: Collection do MongoDB
        query: Filtro para selecionar registros
        deleted_by: ID do usuário que está deletando
        reason: Motivo da exclusão (opcional)

    Returns:
        Resultado da operação
    """
    result = await collection.update_many(
        query,
        {
            "$set": {
                "flag_del": True,
                "deleted_at": datetime.utcnow(),
                "deleted_by": ObjectId(deleted_by) if deleted_by else None,
                "deleted_reason": reason
            }
        }
    )

    return {
        "success": result.modified_count > 0,
        "modified_count": result.modified_count
    }


async def restore_deleted(collection, record_id: str) -> Dict:
    """
    Restaura registro excluído (reverte soft delete)

    Args:
        collection: Collection do MongoDB
        record_id: ID do registro a ser restaurado

    Returns:
        Resultado da operação
    """
    result = await collection.update_one(
        {"_id": ObjectId(record_id)},
        {
            "$set": {
                "flag_del": False,
                "deleted_at": None,
                "deleted_by": None,
                "deleted_reason": None
            }
        }
    )

    return {
        "success": result.modified_count > 0,
        "modified_count": result.modified_count
    }


async def restore_many(collection, query: Dict) -> Dict:
    """
    Restaura múltiplos registros excluídos

    Args:
        collection: Collection do MongoDB
        query: Filtro para selecionar registros

    Returns:
        Resultado da operação
    """
    result = await collection.update_many(
        query,
        {
            "$set": {
                "flag_del": False,
                "deleted_at": None,
                "deleted_by": None,
                "deleted_reason": None
            }
        }
    )

    return {
        "success": result.modified_count > 0,
        "modified_count": result.modified_count
    }


async def find_deleted(collection, query: Dict = None) -> List[Dict]:
    """
    Busca apenas registros deletados
    APENAS PARA USO ADMINISTRATIVO (painel de recuperação)

    Args:
        collection: Collection do MongoDB
        query: Filtros adicionais (opcional)

    Returns:
        Lista de registros deletados
    """
    if query is None:
        query = {}

    query['flag_del'] = True
    return await collection.find(query).to_list(length=None)


def get_base_schema() -> Dict[str, Any]:
    """
    Retorna os campos base que TODOS os schemas devem ter

    Returns:
        Dicionário com campos obrigatórios
    """
    return {
        "flag_del": False,
        "deleted_at": None,
        "deleted_by": None,
        "deleted_reason": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


async def permanent_delete(collection, record_id: str) -> Dict:
    """
    ATENÇÃO: Deleta registro PERMANENTEMENTE do banco de dados!

    ⚠️ USAR APENAS EM CASOS EXTREMOS (LGPD, requisição legal, etc.)
    ⚠️ REQUER APROVAÇÃO DE ADMINISTRADOR NÍVEL 3

    Args:
        collection: Collection do MongoDB
        record_id: ID do registro a ser deletado permanentemente

    Returns:
        Resultado da operação
    """
    # Log de auditoria OBRIGATÓRIO antes de delete permanente
    from backend.app.utils.audit import log_permanent_delete
    await log_permanent_delete(collection.name, record_id)

    result = await collection.delete_one({"_id": ObjectId(record_id)})

    return {
        "success": result.deleted_count > 0,
        "deleted_count": result.deleted_count,
        "warning": "REGISTRO DELETADO PERMANENTEMENTE - AÇÃO IRREVERSÍVEL"
    }
