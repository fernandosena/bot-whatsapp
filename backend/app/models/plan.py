"""
Model: Plan (Plano de Assinatura)
Schema com Soft Delete - TOTALMENTE CONFIGURÁVEL PELO ADMIN
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class PlanFeatures(BaseModel):
    """Funcionalidades do plano"""
    max_contacts: int = 100  # -1 = ilimitado
    max_messages_per_month: int = 500  # -1 = ilimitado
    max_devices: int = 1
    has_variables: bool = False
    has_sequence: bool = False
    has_media: bool = False  # áudio, imagem, vídeo
    has_advanced_reports: bool = False
    has_api_access: bool = False
    has_multi_user: bool = False
    support_level: str = "email"  # email, email_chat, priority_24x7


class PlanBase(BaseModel):
    name: str  # "Pro", "Enterprise", "Black Friday Special"
    slug: str  # "pro", "enterprise", "black-friday-special"
    description: str
    price_monthly: int  # Em centavos (9900 = R$ 99,00)
    price_yearly: Optional[int] = None  # None = não oferece anual
    features: PlanFeatures

    status: str = "active"  # active, inactive, archived
    is_visible: bool = True  # Mostrar na página de preços
    is_featured: bool = False  # Destacar como "Mais Popular"

    trial_days: int = 0  # 0 = sem trial
    setup_fee: int = 0  # Taxa de setup (em centavos)

    available_gateways: List[str] = ["mercadopago", "stripe", "paypal"]


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[int] = None
    price_yearly: Optional[int] = None
    features: Optional[PlanFeatures] = None
    status: Optional[str] = None
    is_visible: Optional[bool] = None
    is_featured: Optional[bool] = None
    trial_days: Optional[int] = None
    setup_fee: Optional[int] = None
    available_gateways: Optional[List[str]] = None


class PlanInDB(PlanBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    # Soft Delete fields (OBRIGATÓRIO)
    flag_del: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[PyObjectId] = None
    deleted_reason: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None  # Admin que criou

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Pro",
                "slug": "pro",
                "description": "Plano profissional para empresas",
                "price_monthly": 9900,
                "price_yearly": 99000,
                "features": {
                    "max_contacts": 5000,
                    "max_messages_per_month": -1,
                    "max_devices": 3,
                    "has_variables": True,
                    "has_sequence": True,
                    "has_media": True,
                    "has_advanced_reports": True,
                    "has_api_access": False,
                    "has_multi_user": False,
                    "support_level": "email_chat"
                },
                "status": "active",
                "is_visible": True,
                "is_featured": True,
                "trial_days": 7,
                "setup_fee": 0,
                "flag_del": False
            }
        }


class PlanResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    slug: str
    description: str
    price_monthly: int
    price_yearly: Optional[int]
    features: PlanFeatures
    status: str
    is_visible: bool
    is_featured: bool
    trial_days: int
    setup_fee: int
    available_gateways: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
