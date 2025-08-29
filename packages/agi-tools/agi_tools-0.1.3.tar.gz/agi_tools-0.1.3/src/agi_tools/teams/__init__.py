# -*- coding: utf-8 -*-
from pymsteams import connectorcard
from agi_tools.tools import get_config


class Teams():
    """Classe para integração e envio de mensagens para Microsoft Teams via webhook.

    Utiliza configurações do arquivo TOML para definir o webhook e os tipos de mensagens.
    """

    def __init__(self) -> None:
        """Inicializa a classe Teams carregando configurações do webhook.

        Returns:
            None
        """
        self.teams_config = get_config('teams', 'teams')
        self.webhook = self.teams_config.get('webhook', '')


    def process_message(self, message_type: str = 'success', process_name: str = '') -> dict:
        """Processa e envia uma mensagem para o Teams conforme o tipo.

        Args:
            message_type (str, optional): Tipo da mensagem ('success', 'error', etc). Default 'success'.
            process_name (str, optional): Nome do processo para interpolação na mensagem.

        Returns:
            dict: Resultado do envio, incluindo status e mensagem de erro se houver.
        """
        self.message = self.teams_config.get(message_type, {})
        return self.send_message(
            title=self.message.get('title', ''),
            color=self.message.get('color', ''),
            message=self.message.get('message', '') % process_name
        )

    def send_message(self, title: str, color: str, message: str ) -> dict:
        """Envia uma mensagem para o Teams usando o webhook configurado.

        Args:
            title (str): Título da mensagem.
            color (str): Cor da mensagem (hex ou nome).
            message (str): Texto da mensagem.

        Returns:
            dict: Resultado do envio, incluindo status e mensagem de erro se houver.
        """
        
        try:
            teams_msg = connectorcard(self.webhook)
            teams_msg.title(title)
            teams_msg.text(message)
            teams_msg.color(color)
            teams_msg.send()
            return {
                    "success": True,
                    "status_code": teams_msg.last_http_response.status_code,
                    "message": "Mensagem enviada com sucesso."
                }
        except Exception as e:
            return {
                "success": False,
                "error_type": "exception",
                "message": f"Erro no envio da mensagem: {e}"
            }
