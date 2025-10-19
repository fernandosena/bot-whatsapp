"""
Model: Subscription (Assinatura)
Schema com Soft Delete
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.with_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x),
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def validate(cls, v, _info):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class SubscriptionBase(BaseModel):
    user_id: PyObjectId
    plan_id: PyObjectId
    status: str = "active"  # active, expired, cancelled, pending
    payment_method: str  # mercadopago_pix, mercadopago_boleto, stripe, paypal
    billing_cycle: str = "monthly"  # monthly, yearly

    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None

    auto_renew: bool = True


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    status: Optional[str] = None
    auto_renew: Optional[bool] = None
    plan_id: Optional[PyObjectId] = None


class SubscriptionInDB(SubscriptionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    # Pagamento
    last_payment_id: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None

    # Cancelamento
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None

    # Soft Delete fields (OBRIGATÓRIO)
    flag_del: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[PyObjectId] = None
    deleted_reason: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SubscriptionResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    plan_id: str
    status: str
    payment_method: str
    billing_cycle: str
    current_period_start: datetime
    current_period_end: datetime
    auto_renew: bool
    created_at: datetime

    class Config:
        populate_by_name = True
