# -*- coding: UTF-8 -*-

import msal
import requests
from agi_tools.tools import get_config
from typing import Optional, Union


class AgiMail:
    """Classe para envio de e-mails via Microsoft Graph API."""

    def __init__(self):
        """Inicializa a classe AgiMail com configurações de autenticação e sessão."""
        self.session = requests.Session()
        self.session.verify = True
        self.email_access_token: Optional[str] = None
        self.mail_config = get_config('mail', 'mail')
        self.__mail_tenant_id = self.mail_config.get("mail_tenant_id", "")
        self.__mail_client_id = self.mail_config.get("mail_client_id", "")
        self.__mail_client_secret = self.mail_config.get("mail_client_secret", "")
        self.sender_email = self.mail_config.get("mail_from", "")
        self.mail_footnote = self.mail_config.get("mail_footnote", "")

        self.creds = {
            "tenant_id": self.__mail_tenant_id,
            "client_id": self.__mail_client_id,
            "client_secret": self.__mail_client_secret
        }


    def get_email_token(self) -> Union[str, dict]:
        """Obtém o token de acesso para envio de e-mails.

        Returns:
            Union[str, dict]: Token de acesso ou dicionário de erro.
        """
        if self.email_access_token:
            return self.email_access_token
        app = msal.ConfidentialClientApplication(
            self.creds['client_id'],
            authority=f"https://login.microsoftonline.com/{self.creds['tenant_id']}",
            client_credential=self.creds['client_secret'],
            http_client=self.session
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"]) or {}
        if 'access_token' in result:
            self.email_access_token = result['access_token']
            return self.email_access_token or ''
        else:
            return {
                "success": False,
                "error_type": "token_error",
                "message": f"Erro ao obter token: {result.get('error_description', result)}"
            }


    def send_email(
        self,
        subject: str,
        mail_to: Union[str, list],
        html_body: str,
        mail_cc: Union[str, list] = []
    ) -> dict:
        """Envia um e-mail usando a API do Microsoft Graph.

        Args:
            subject (str): Assunto do e-mail.
            mail_to (Union[str, list]): Destinatários principais.
            html_body (str): Corpo do e-mail em HTML.
            mail_cc (Union[str, list], optional): Destinatários em cópia.

        Returns:
            dict: Resultado do envio do e-mail.
        """
        if isinstance(mail_to, list):
            mail_to_str = ';'.join(mail_to)
        else:
            mail_to_str = mail_to
        if mail_cc:
            if isinstance(mail_cc, list):
                mail_cc_str = ';'.join(mail_cc)
            else:
                mail_cc_str = mail_cc
        else:
            mail_cc_str = ''
        if not all([subject, mail_to_str, html_body]):
            return {
                "success": False,
                "error_type": "missing_params",
                "message": "Parâmetros obrigatórios ausentes para envio de e-mail."
            }
        if any(["@" not in email for email in mail_to_str.split(';') if email]):
            return {
                "success": False,
                "error_type": "invalid_email",
                "message": f"E-mail de destino inválido: {mail_to_str}"
            }
        if mail_cc_str and any(["@" not in email for email in mail_cc_str.split(';') if email]):
            return {
                "success": False,
                "error_type": "invalid_cc",
                "message": f"E-mail CC inválido: {mail_cc_str}"
            }
        access_token = self.get_email_token()
        if isinstance(access_token, dict):
            return access_token
        if not access_token:
            return {
                "success": False,
                "error_type": "token_missing",
                "message": "Token de acesso não obtido."
            }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": f'{html_body}{self.mail_footnote}'
                },
                "toRecipients": [
                    {"emailAddress": {"address": email}}
                    for email in mail_to_str.split(';') if email
                ],
                "ccRecipients": [
                    {"emailAddress": {"address": email}}
                    for email in mail_cc_str.split(';') if email
                ] if mail_cc_str else []
            },
            "saveToSentItems": "true"
        }
        try:
            response = self.session.post(
                f'https://graph.microsoft.com/v1.0/users/{self.sender_email}/sendMail',
                headers=headers,
                json=email_data,
                verify=self.session.verify
            )
            if response.status_code == 202:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "message": "E-mail enviado com sucesso."
                }
            else:
                return {
                    "success": False,
                    "error_type": "send_error",
                    "status_code": response.status_code,
                    "message": f"Falha ao enviar e-mail: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error_type": "exception",
                "message": f"Erro no envio de email: {e}"
            }
