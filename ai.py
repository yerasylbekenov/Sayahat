from gigachat import GigaChat
from configs import config
import logging

logger = logging.getLogger(__name__)

class GigaChatClient:
    def __init__(self):
        self.auth_key = config.AUTH_KEY
        self.verify_ssl = False
    
    def chat(self, user_id, message):
        """Отправляет сообщение в GigaChat и возвращает ответ"""
        try:
            with GigaChat(credentials=self.auth_key, model="GigaChat-Pro", verify_ssl_certs=self.verify_ssl) as giga:
                response = giga.chat(message)
                return response.choices[0].message.content if response.choices else "Ошибка: нет ответа"
        except Exception as e:
            logger.error(f"Ошибка при запросе к GigaChat: {e}")
            return f"Ошибка при запросе к GigaChat: {str(e)}"