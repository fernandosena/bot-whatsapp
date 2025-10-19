"""
Model: Session (Sessão de usuário)
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


class SessionBase(BaseModel):
    user_id: PyObjectId
    device_fingerprint: str
    ip_address: str
    user_agent: str
    is_active: bool = True
    last_activity: datetime = Field(default_factory=datetime.utcnow)


class SessionCreate(SessionBase):
    pass


class SessionInDB(SessionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    # Tokens
    access_token: str
    refresh_token: str

    # Rastreamento
    login_at: datetime = Field(default_factory=datetime.utcnow)
    logout_at: Optional[datetime] = None

    # Localização (opcional)
    country: Optional[str] = None
    city: Optional[str] = None

    # Desktop app info (se aplicável)
    is_desktop: bool = False
    desktop_version: Optional[str] = None

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


class SessionResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    device_fingerprint: str
    ip_address: str
    user_agent: str
    is_active: bool
    last_activity: datetime
    login_at: datetime
    is_desktop: bool

    class Config:
        populate_by_name = True
