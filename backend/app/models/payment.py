"""
Payment Models - Schemas para pagamentos
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class PaymentGateway(str, Enum):
    """Gateways de pagamento suportados"""
    MERCADOPAGO = "mercadopago"
    STRIPE = "stripe"
    PAYPAL = "paypal"


class PaymentStatus(str, Enum):
    """Status do pagamento"""
    PENDING = "pending"           # Pendente
    PROCESSING = "processing"     # Processando
    APPROVED = "approved"         # Aprovado
    REJECTED = "rejected"         # Rejeitado
    CANCELLED = "cancelled"       # Cancelado
    REFUNDED = "refunded"         # Reembolsado
    CHARGEBACK = "chargeback"     # Chargeback


class PaymentMethod(str, Enum):
    """Métodos de pagamento"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    BOLETO = "boleto"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


# ==================== MongoDB Schema ====================

class PaymentSchema(BaseModel):
    """
    Schema de Payment no MongoDB

    Armazena todos os pagamentos do sistema
    """
    # IDs
    user_id: str                          # ObjectId do usuário
    subscription_id: Optional[str] = None # ObjectId da assinatura
    plan_id: str                          # ObjectId do plano

    # Gateway
    gateway: PaymentGateway               # mercadopago, stripe, paypal
    gateway_payment_id: str               # ID do pagamento no gateway
    gateway_customer_id: Optional[str] = None  # ID do cliente no gateway

    # Valores
    amount: float                         # Valor total
    currency: str = "BRL"                 # Moeda (BRL, USD, EUR)

    # Método
    payment_method: PaymentMethod         # pix, boleto, credit_card, etc

    # Status
    status: PaymentStatus = PaymentStatus.PENDING

    # Detalhes do gateway
    gateway_response: Optional[Dict[str, Any]] = None  # Resposta completa do gateway
    gateway_error: Optional[str] = None                # Erro do gateway (se houver)

    # Detalhes do cartão (se aplicável)
    card_last_4_digits: Optional[str] = None
    card_brand: Optional[str] = None  # visa, mastercard, amex, etc

    # PIX (se aplicável)
    pix_qr_code: Optional[str] = None
    pix_qr_code_base64: Optional[str] = None

    # Boleto (se aplicável)
    boleto_url: Optional[str] = None
    boleto_barcode: Optional[str] = None
    boleto_due_date: Optional[datetime] = None

    # Datas
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None  # Para PIX e Boleto

    # Metadata
    metadata: Optional[Dict[str, Any]] = None  # Dados adicionais

    # Soft delete
    flag_del: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    deleted_reason: Optional[str] = None

    # Auditoria
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "subscription_id": "507f1f77bcf86cd799439012",
                "plan_id": "507f1f77bcf86cd799439013",
                "gateway": "mercadopago",
                "gateway_payment_id": "1234567890",
                "amount": 99.90,
                "currency": "BRL",
                "payment_method": "pix",
                "status": "approved",
                "pix_qr_code": "00020126580014br.gov.bcb.pix...",
                "paid_at": "2025-10-19T10:30:00Z"
            }
        }


# ==================== Request/Response Models ====================

class CreatePaymentRequest(BaseModel):
    """Request para criar pagamento"""
    plan_id: str
    payment_method: PaymentMethod
    gateway: PaymentGateway

    # Dados do cartão (se payment_method for credit_card ou debit_card)
    card_token: Optional[str] = None

    # Metadata adicional
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "507f1f77bcf86cd799439013",
                "payment_method": "pix",
                "gateway": "mercadopago",
                "metadata": {
                    "campaign": "black_friday_2025"
                }
            }
        }


class PaymentResponse(BaseModel):
    """Response de pagamento"""
    payment_id: str
    status: PaymentStatus
    amount: float
    currency: str
    payment_method: PaymentMethod
    gateway: PaymentGateway

    # URLs/QR Codes
    checkout_url: Optional[str] = None
    pix_qr_code: Optional[str] = None
    pix_qr_code_base64: Optional[str] = None
    boleto_url: Optional[str] = None

    # Detalhes
    gateway_payment_id: str
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": "507f1f77bcf86cd799439014",
                "status": "pending",
                "amount": 99.90,
                "currency": "BRL",
                "payment_method": "pix",
                "gateway": "mercadopago",
                "pix_qr_code": "00020126580014br.gov.bcb.pix...",
                "gateway_payment_id": "1234567890",
                "expires_at": "2025-10-19T23:59:59Z",
                "created_at": "2025-10-19T10:00:00Z"
            }
        }


class PaymentListItem(BaseModel):
    """Item da lista de pagamentos"""
    id: str
    amount: float
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod
    gateway: PaymentGateway
    created_at: datetime
    paid_at: Optional[datetime] = None
    plan_name: Optional[str] = None


class PaymentHistoryResponse(BaseModel):
    """Response do histórico de pagamentos"""
    total: int
    payments: List[PaymentListItem]


class WebhookPayload(BaseModel):
    """Payload genérico de webhook"""
    gateway: PaymentGateway
    event_type: str
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "gateway": "mercadopago",
                "event_type": "payment.updated",
                "data": {
                    "id": "1234567890",
                    "status": "approved"
                }
            }
        }


# ==================== Subscription Payment Models ====================

class SubscriptionPaymentSchema(BaseModel):
    """
    Schema para pagamentos recorrentes (assinaturas)

    Relaciona subscription com payments
    """
    subscription_id: str                   # ObjectId da assinatura
    user_id: str                          # ObjectId do usuário
    plan_id: str                          # ObjectId do plano

    # Gateway de assinatura
    gateway: PaymentGateway
    gateway_subscription_id: str          # ID da assinatura no gateway
    gateway_customer_id: str              # ID do cliente no gateway

    # Status
    is_active: bool = True

    # Valores
    amount: float
    currency: str = "BRL"
    interval: str = "monthly"             # monthly, yearly

    # Próxima cobrança
    next_billing_date: datetime

    # Histórico
    payments: List[str] = []              # Lista de ObjectIds de Payment

    # Cancelamento
    cancelled_at: Optional[datetime] = None
    cancel_reason: Optional[str] = None

    # Datas
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    flag_del: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    deleted_reason: Optional[str] = None


class CreateSubscriptionRequest(BaseModel):
    """Request para criar assinatura recorrente"""
    plan_id: str
    payment_method: PaymentMethod
    gateway: PaymentGateway
    interval: str = "monthly"  # monthly ou yearly

    # Token do cartão (obrigatório para assinaturas)
    card_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "507f1f77bcf86cd799439013",
                "payment_method": "credit_card",
                "gateway": "stripe",
                "interval": "monthly",
                "card_token": "tok_visa_4242"
            }
        }


class CancelSubscriptionRequest(BaseModel):
    """Request para cancelar assinatura"""
    reason: Optional[str] = None
    cancel_at_period_end: bool = True  # Se True, cancela no fim do período

    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Não preciso mais do serviço",
                "cancel_at_period_end": True
            }
        }


# ==================== Refund Models ====================

class RefundRequest(BaseModel):
    """Request para solicitar reembolso"""
    payment_id: str
    amount: Optional[float] = None  # Se None, reembolsa tudo
    reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": "507f1f77bcf86cd799439014",
                "amount": 99.90,
                "reason": "Cliente solicitou cancelamento"
            }
        }


class RefundResponse(BaseModel):
    """Response de reembolso"""
    refund_id: str
    payment_id: str
    amount: float
    status: str
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "refund_id": "re_1234567890",
                "payment_id": "507f1f77bcf86cd799439014",
                "amount": 99.90,
                "status": "succeeded",
                "created_at": "2025-10-19T11:00:00Z"
            }
        }
