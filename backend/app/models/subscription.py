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
