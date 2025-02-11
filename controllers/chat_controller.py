from flask import render_template, session, request
from flask_socketio import emit
import logging

logger = logging.getLogger(__name__)

class ChatController:
    def __init__(self, database, chat_client):
        self.db = database
        self.chat_client = chat_client

    def chat(self):
        user_id = session.get('user_id')
        if not user_id:
            return "Ошибка: Пользователь не авторизован.", 401
        
        user = self.db.get_record('users', 'user_id', user_id)
        if not user:
            return "Ошибка: Пользователь не найден.", 404
        
        chat_history = self.db.load_chat_history(user_id)
        return render_template('chat.html', user=user, chat_history=chat_history)

    def handle_message(self, msg):
        user_id = session.get('user_id')
        if not user_id:
            logger.error("Пользователь не авторизован.")
            return
        response = self.chat_client.process_message(user_id, msg)
        emit('message', response, room=request.sid)