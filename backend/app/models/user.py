"""
Model: User (Usuário)
Schema com Soft Delete
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
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


class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    role: str = "user"  # user, admin, super_admin
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    email_verified: bool = False
    phone_verified: bool = False

    # OAuth fields
    oauth_provider: Optional[str] = None  # google, github, linkedin
    oauth_id: Optional[str] = None

    # Subscription
    current_plan_id: Optional[PyObjectId] = None
    subscription_status: str = "free"  # free, active, expired, cancelled

    # Device limits
    active_devices: List[str] = []  # Lista de device fingerprints

    # Soft Delete fields (OBRIGATÓRIO)
    flag_del: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[PyObjectId] = None
    deleted_reason: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "João Silva",
                "phone": "+5511999999999",
                "role": "user",
                "is_active": True,
                "flag_del": False
            }
        }


class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    name: str
    phone: Optional[str]
    avatar: Optional[str]
    role: str
    is_active: bool
    email_verified: bool
    current_plan_id: Optional[str]
    subscription_status: str
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        populate_by_name = True
