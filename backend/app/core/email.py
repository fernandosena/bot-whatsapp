"""
Sistema de Envio de Emails

Gerencia envio de emails transacionais usando SMTP
"""

import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
from typing import List, Optional, Dict
from datetime import datetime
import aiosmtplib

logger = logging.getLogger(__name__)


class EmailService:
    """Serviço de envio de emails"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", self.smtp_user)
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

        # Verificar configuração
        if not self.smtp_user or not self.smtp_password:
            logger.warning("⚠️ SMTP não configurado. Emails não serão enviados.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"✅ Email service configurado: {self.smtp_host}:{self.smtp_port}")

    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Envia um email

        Args:
            to: Email do destinatário
            subject: Assunto do email
            html_content: Conteúdo HTML do email
            text_content: Conteúdo texto plano (fallback)

        Returns:
            True se enviado com sucesso
        """
        if not self.enabled:
            logger.warning(f"📧 Email não enviado (SMTP desabilitado): {to} - {subject}")
            return False

        try:
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.smtp_from
            message["To"] = to

            # Adicionar conteúdo texto plano
            if text_content:
                part1 = MIMEText(text_content, "plain", "utf-8")
                message.attach(part1)

            # Adicionar conteúdo HTML
            part2 = MIMEText(html_content, "html", "utf-8")
            message.attach(part2)

            # Enviar usando aiosmtplib (async)
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )

            logger.info(f"✅ Email enviado: {to} - {subject}")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao enviar email para {to}: {str(e)}")
            return False

    async def send_subscription_expiring_email(
        self,
        user_email: str,
        user_name: str,
        plan_name: str,
        expires_at: datetime,
        days_remaining: int
    ) -> bool:
        """
        Envia email de aviso de expiração de assinatura

        Args:
            user_email: Email do usuário
            user_name: Nome do usuário
            plan_name: Nome do plano
            expires_at: Data de expiração
            days_remaining: Dias restantes

        Returns:
            True se enviado com sucesso
        """
        subject = f"⚠️ Sua assinatura expira em {days_remaining} dias"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .warning-box {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Aviso de Expiração</h1>
                </div>
                <div class="content">
                    <p>Olá <strong>{user_name}</strong>,</p>

                    <div class="warning-box">
                        <p><strong>Sua assinatura do plano "{plan_name}" expira em {days_remaining} dias!</strong></p>
                        <p>Data de expiração: <strong>{expires_at.strftime("%d/%m/%Y às %H:%M")}</strong></p>
                    </div>

                    <p>Para continuar aproveitando todos os benefícios do seu plano, renove sua assinatura antes da data de expiração.</p>

                    <p>
                        <strong>O que acontece se minha assinatura expirar?</strong><br>
                        • Você perderá acesso aos recursos premium<br>
                        • Suas campanhas serão pausadas<br>
                        • Seus dados serão mantidos por 30 dias para recuperação
                    </p>

                    <center>
                        <a href="{self.frontend_url}/subscription" class="button">
                            Renovar Agora
                        </a>
                    </center>

                    <p>Se você tiver alguma dúvida, entre em contato com nosso suporte.</p>

                    <p>Atenciosamente,<br>
                    <strong>Equipe WhatsApp Business SaaS</strong></p>
                </div>
                <div class="footer">
                    <p>Este é um email automático, por favor não responda.</p>
                    <p>&copy; 2025 WhatsApp Business SaaS - Todos os direitos reservados</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Olá {user_name},

        Sua assinatura do plano "{plan_name}" expira em {days_remaining} dias!
        Data de expiração: {expires_at.strftime("%d/%m/%Y às %H:%M")}

        Para renovar, acesse: {self.frontend_url}/subscription

        Atenciosamente,
        Equipe WhatsApp Business SaaS
        """

        return await self.send_email(user_email, subject, html_content, text_content)

    async def send_subscription_expired_email(
        self,
        user_email: str,
        user_name: str,
        plan_name: str,
        expired_at: datetime
    ) -> bool:
        """
        Envia email de assinatura expirada
        """
        subject = "❌ Sua assinatura expirou"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #f56565 0%, #c53030 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .error-box {{
                    background: #fee;
                    border-left: 4px solid #f56565;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Assinatura Expirada</h1>
                </div>
                <div class="content">
                    <p>Olá <strong>{user_name}</strong>,</p>

                    <div class="error-box">
                        <p><strong>Sua assinatura do plano "{plan_name}" expirou.</strong></p>
                        <p>Data de expiração: <strong>{expired_at.strftime("%d/%m/%Y às %H:%M")}</strong></p>
                    </div>

                    <p><strong>O que isso significa?</strong><br>
                    • Seu acesso aos recursos premium foi suspenso<br>
                    • Suas campanhas foram pausadas<br>
                    • Seus dados estão seguros e serão mantidos por 30 dias
                    </p>

                    <p>Para reativar sua assinatura e voltar a usar todos os recursos, renove agora:</p>

                    <center>
                        <a href="{self.frontend_url}/subscription" class="button">
                            Renovar Assinatura
                        </a>
                    </center>

                    <p>Tem dúvidas? Entre em contato com nosso suporte.</p>

                    <p>Atenciosamente,<br>
                    <strong>Equipe WhatsApp Business SaaS</strong></p>
                </div>
                <div class="footer">
                    <p>Este é um email automático, por favor não responda.</p>
                    <p>&copy; 2025 WhatsApp Business SaaS - Todos os direitos reservados</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Olá {user_name},

        Sua assinatura do plano "{plan_name}" expirou.
        Data de expiração: {expired_at.strftime("%d/%m/%Y às %H:%M")}

        Para renovar, acesse: {self.frontend_url}/subscription

        Atenciosamente,
        Equipe WhatsApp Business SaaS
        """

        return await self.send_email(user_email, subject, html_content, text_content)

    async def send_subscription_renewed_email(
        self,
        user_email: str,
        user_name: str,
        plan_name: str,
        new_period_end: datetime,
        amount: float
    ) -> bool:
        """
        Envia email de renovação bem-sucedida
        """
        subject = "✅ Assinatura renovada com sucesso!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #48bb78 0%, #2f855a 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .success-box {{
                    background: #d4edda;
                    border-left: 4px solid #48bb78;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .info-table {{
                    width: 100%;
                    background: white;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .info-table tr td {{
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                }}
                .info-table tr:last-child td {{
                    border-bottom: none;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Renovação Confirmada!</h1>
                </div>
                <div class="content">
                    <p>Olá <strong>{user_name}</strong>,</p>

                    <div class="success-box">
                        <p><strong>Sua assinatura foi renovada com sucesso!</strong></p>
                    </div>

                    <table class="info-table">
                        <tr>
                            <td><strong>Plano:</strong></td>
                            <td>{plan_name}</td>
                        </tr>
                        <tr>
                            <td><strong>Valor:</strong></td>
                            <td>R$ {amount:.2f}</td>
                        </tr>
                        <tr>
                            <td><strong>Válido até:</strong></td>
                            <td>{new_period_end.strftime("%d/%m/%Y às %H:%M")}</td>
                        </tr>
                    </table>

                    <p>Você pode continuar aproveitando todos os recursos do seu plano sem interrupções!</p>

                    <center>
                        <a href="{self.frontend_url}/dashboard" class="button">
                            Acessar Dashboard
                        </a>
                    </center>

                    <p>Atenciosamente,<br>
                    <strong>Equipe WhatsApp Business SaaS</strong></p>
                </div>
                <div class="footer">
                    <p>Este é um email automático, por favor não responda.</p>
                    <p>&copy; 2025 WhatsApp Business SaaS - Todos os direitos reservados</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Olá {user_name},

        Sua assinatura foi renovada com sucesso!

        Plano: {plan_name}
        Valor: R$ {amount:.2f}
        Válido até: {new_period_end.strftime("%d/%m/%Y às %H:%M")}

        Acesse: {self.frontend_url}/dashboard

        Atenciosamente,
        Equipe WhatsApp Business SaaS
        """

        return await self.send_email(user_email, subject, html_content, text_content)

    async def send_payment_successful_email(
        self,
        user_email: str,
        user_name: str,
        plan_name: str,
        amount: float,
        payment_method: str,
        transaction_id: str
    ) -> bool:
        """
        Envia email de pagamento aprovado
        """
        subject = "✅ Pagamento aprovado!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .success-box {{
                    background: #d4edda;
                    border-left: 4px solid #48bb78;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .info-table {{
                    width: 100%;
                    background: white;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .info-table tr td {{
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                }}
                .info-table tr:last-child td {{
                    border-bottom: none;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Pagamento Aprovado!</h1>
                </div>
                <div class="content">
                    <p>Olá <strong>{user_name}</strong>,</p>

                    <div class="success-box">
                        <p><strong>Seu pagamento foi aprovado com sucesso!</strong></p>
                    </div>

                    <table class="info-table">
                        <tr>
                            <td><strong>Plano:</strong></td>
                            <td>{plan_name}</td>
                        </tr>
                        <tr>
                            <td><strong>Valor:</strong></td>
                            <td>R$ {amount:.2f}</td>
                        </tr>
                        <tr>
                            <td><strong>Forma de pagamento:</strong></td>
                            <td>{payment_method}</td>
                        </tr>
                        <tr>
                            <td><strong>ID da transação:</strong></td>
                            <td>{transaction_id}</td>
                        </tr>
                    </table>

                    <p>Sua assinatura está ativa e você já pode começar a usar todos os recursos!</p>

                    <center>
                        <a href="{self.frontend_url}/dashboard" class="button">
                            Começar Agora
                        </a>
                    </center>

                    <p>Atenciosamente,<br>
                    <strong>Equipe WhatsApp Business SaaS</strong></p>
                </div>
                <div class="footer">
                    <p>Este é um email automático, por favor não responda.</p>
                    <p>&copy; 2025 WhatsApp Business SaaS - Todos os direitos reservados</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Olá {user_name},

        Seu pagamento foi aprovado com sucesso!

        Plano: {plan_name}
        Valor: R$ {amount:.2f}
        Forma de pagamento: {payment_method}
        ID da transação: {transaction_id}

        Acesse: {self.frontend_url}/dashboard

        Atenciosamente,
        Equipe WhatsApp Business SaaS
        """

        return await self.send_email(user_email, subject, html_content, text_content)

    async def send_password_reset_email(
        self,
        user_email: str,
        user_name: str,
        reset_link: str,
        expires_minutes: int
    ) -> bool:
        """
        Envia email de reset de senha
        """
        subject = "🔐 Redefinir sua senha"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .warning-box {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Redefinir Senha</h1>
                </div>
                <div class="content">
                    <p>Olá <strong>{user_name}</strong>,</p>

                    <p>Recebemos uma solicitação para redefinir a senha da sua conta.</p>

                    <div class="warning-box">
                        <p><strong>Este link expira em {expires_minutes} minutos.</strong></p>
                    </div>

                    <p>Clique no botão abaixo para criar uma nova senha:</p>

                    <center>
                        <a href="{reset_link}" class="button">
                            Redefinir Senha
                        </a>
                    </center>

                    <p>Se você não solicitou esta alteração, ignore este email. Sua senha permanecerá a mesma.</p>

                    <p><strong>Por segurança:</strong></p>
                    <ul>
                        <li>Nunca compartilhe este link</li>
                        <li>Use uma senha forte (mínimo 8 caracteres)</li>
                        <li>Não use a mesma senha de outros sites</li>
                    </ul>

                    <p>Atenciosamente,<br>
                    <strong>Equipe WhatsApp Business SaaS</strong></p>
                </div>
                <div class="footer">
                    <p>Este é um email automático, por favor não responda.</p>
                    <p>&copy; 2025 WhatsApp Business SaaS - Todos os direitos reservados</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Olá {user_name},

        Recebemos uma solicitação para redefinir a senha da sua conta.

        Clique no link abaixo para criar uma nova senha:
        {reset_link}

        Este link expira em {expires_minutes} minutos.

        Se você não solicitou esta alteração, ignore este email.

        Atenciosamente,
        Equipe WhatsApp Business SaaS
        """

        return await self.send_email(user_email, subject, html_content, text_content)

    async def send_password_changed_email(
        self,
        user_email: str,
        user_name: str
    ) -> bool:
        """
        Envia email de confirmação de alteração de senha
        """
        subject = "✅ Senha alterada com sucesso"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #48bb78 0%, #2f855a 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .success-box {{
                    background: #d4edda;
                    border-left: 4px solid #48bb78;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .warning-box {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Senha Alterada</h1>
                </div>
                <div class="content">
                    <p>Olá <strong>{user_name}</strong>,</p>

                    <div class="success-box">
                        <p><strong>Sua senha foi alterada com sucesso!</strong></p>
                    </div>

                    <p>Todas as suas sessões ativas foram encerradas por segurança. Você precisará fazer login novamente com sua nova senha.</p>

                    <div class="warning-box">
                        <p><strong>Se você não fez esta alteração:</strong></p>
                        <p>Entre em contato com nosso suporte imediatamente. Sua conta pode estar comprometida.</p>
                    </div>

                    <p>Atenciosamente,<br>
                    <strong>Equipe WhatsApp Business SaaS</strong></p>
                </div>
                <div class="footer">
                    <p>Este é um email automático, por favor não responda.</p>
                    <p>&copy; 2025 WhatsApp Business SaaS - Todos os direitos reservados</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Olá {user_name},

        Sua senha foi alterada com sucesso!

        Todas as suas sessões ativas foram encerradas por segurança.

        Se você não fez esta alteração, entre em contato com nosso suporte imediatamente.

        Atenciosamente,
        Equipe WhatsApp Business SaaS
        """

        return await self.send_email(user_email, subject, html_content, text_content)

    async def send_welcome_email(
        self,
        user_email: str,
        user_name: str
    ) -> bool:
        """
        Envia email de boas-vindas
        """
        subject = "🎉 Bem-vindo ao WhatsApp Business SaaS!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .feature-box {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    border-left: 4px solid #667eea;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Bem-vindo!</h1>
                </div>
                <div class="content">
                    <p>Olá <strong>{user_name}</strong>,</p>

                    <p>É um prazer ter você conosco! Estamos animados para ajudá-lo a revolucionar sua comunicação no WhatsApp.</p>

                    <h3>🚀 Próximos Passos:</h3>

                    <div class="feature-box">
                        <strong>1. Escolha seu plano</strong><br>
                        Selecione o plano que melhor se adapta às suas necessidades
                    </div>

                    <div class="feature-box">
                        <strong>2. Configure sua conta</strong><br>
                        Personalize suas preferências e conecte seu WhatsApp
                    </div>

                    <div class="feature-box">
                        <strong>3. Crie sua primeira campanha</strong><br>
                        Comece a enviar mensagens de forma automatizada
                    </div>

                    <center>
                        <a href="{self.frontend_url}/plans" class="button">
                            Ver Planos
                        </a>
                    </center>

                    <p>Se precisar de ajuda, nossa equipe de suporte está sempre disponível!</p>

                    <p>Atenciosamente,<br>
                    <strong>Equipe WhatsApp Business SaaS</strong></p>
                </div>
                <div class="footer">
                    <p>Este é um email automático, por favor não responda.</p>
                    <p>&copy; 2025 WhatsApp Business SaaS - Todos os direitos reservados</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Olá {user_name},

        Bem-vindo ao WhatsApp Business SaaS!

        Próximos passos:
        1. Escolha seu plano
        2. Configure sua conta
        3. Crie sua primeira campanha

        Acesse: {self.frontend_url}/plans

        Atenciosamente,
        Equipe WhatsApp Business SaaS
        """

        return await self.send_email(user_email, subject, html_content, text_content)


# Instância global do serviço de email
email_service = EmailService()


# Funções auxiliares para fácil acesso
async def send_expiring_notification(user_email: str, user_name: str, plan_name: str, expires_at: datetime, days: int):
    """Envia notificação de expiração"""
    return await email_service.send_subscription_expiring_email(user_email, user_name, plan_name, expires_at, days)


async def send_expired_notification(user_email: str, user_name: str, plan_name: str, expired_at: datetime):
    """Envia notificação de expiração"""
    return await email_service.send_subscription_expired_email(user_email, user_name, plan_name, expired_at)


async def send_renewed_notification(user_email: str, user_name: str, plan_name: str, new_period_end: datetime, amount: float):
    """Envia notificação de renovação"""
    return await email_service.send_subscription_renewed_email(user_email, user_name, plan_name, new_period_end, amount)


async def send_payment_notification(user_email: str, user_name: str, plan_name: str, amount: float, payment_method: str, transaction_id: str):
    """Envia notificação de pagamento aprovado"""
    return await email_service.send_payment_successful_email(user_email, user_name, plan_name, amount, payment_method, transaction_id)


async def send_welcome(user_email: str, user_name: str):
    """Envia email de boas-vindas"""
    return await email_service.send_welcome_email(user_email, user_name)


async def send_password_reset(user_email: str, user_name: str, reset_link: str, expires_minutes: int):
    """Envia email de reset de senha"""
    return await email_service.send_password_reset_email(user_email, user_name, reset_link, expires_minutes)


async def send_password_changed(user_email: str, user_name: str):
    """Envia email de confirmação de alteração de senha"""
    return await email_service.send_password_changed_email(user_email, user_name)
