from flask import render_template, session
from flask_socketio import send

class ChatController:
    def __init__(self, database, chat_client):
        self.db = database
        self.chat_client = chat_client

    def chat(self):
        user_id = session['user_id']
        user = self.db.get_record('users', 'user_id', user_id)
        return render_template('chat.html', user=user)

    def handle_message(self, msg):
        user_id = session['user_id']
        response = self.chat_client.chat(user_id, msg)
        send(response, broadcast=True)