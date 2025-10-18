"""
Configuração de Conexão MongoDB com Motor (Async Driver)
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Conecta ao MongoDB"""
    mongodb.client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    mongodb.database = mongodb.client[os.getenv("MONGODB_DB", "whatsapp_business")]
    print("✅ Conectado ao MongoDB")

async def close_mongo_connection():
    """Fecha a conexão com MongoDB"""
    if mongodb.client:
        mongodb.client.close()
        print("❌ Desconectado do MongoDB")

def get_database():
    """Retorna a instância do banco de dados"""
    return mongodb.database

# Collections
def get_users_collection():
    return mongodb.database.users

def get_plans_collection():
    return mongodb.database.plans

def get_subscriptions_collection():
    return mongodb.database.subscriptions

def get_sessions_collection():
    return mongodb.database.sessions

def get_activation_keys_collection():
    return mongodb.database.activation_keys

def get_security_logs_collection():
    return mongodb.database.security_logs

def get_audit_logs_collection():
    return mongodb.database.audit_logs

def get_payment_logs_collection():
    return mongodb.database.payment_logs

def get_contacts_collection():
    return mongodb.database.contacts

def get_campaigns_collection():
    return mongodb.database.campaigns

def get_desktop_updates_collection():
    return mongodb.database.desktop_updates

def get_blocked_ips_collection():
    return mongodb.database.blocked_ips
