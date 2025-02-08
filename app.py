from flask import Flask, request
from flask_socketio import SocketIO
from data import database
from utils import mail
from ai import GigaChatClient  # Импортируем GigaChatClient вместо ChatGPTClient
from controllers import auth_controller, chat_controller, tour_controller, user_controller

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'your_secret_key'
        self.socketio = SocketIO(self.app)
        
        # Initialize services
        self.db = database.Database()
        self.email_verifier = mail.EmailVerifier()
        self.chat_client = GigaChatClient()  # Используем GigaChatClient

        # Initialize controllers
        self.auth_controller = auth_controller.AuthController(self.db, self.email_verifier)
        self.tour_controller = tour_controller.TourController(self.db)
        self.user_controller = user_controller.UserController(self.db)
        self.chat_controller = chat_controller.ChatController(self.db, self.chat_client)

        # Register routes
        self._register_routes()
        self._register_socket_events()

    def _register_routes(self):
        # Auth routes
        self.app.route('/register', methods=['GET', 'POST'])(self.auth_controller.register)
        self.app.route('/login', methods=['GET', 'POST'])(self.auth_controller.login)
        self.app.route('/verify_email', methods=['GET', 'POST'])(self.auth_controller.verify_email)
        self.app.route('/verify_code/<email>', methods=['GET', 'POST'])(self.auth_controller.verify_code)
        self.app.route('/logout')(self.auth_controller.login_required(self.auth_controller.logout))

        # Tour routes
        self.app.route('/')(self.auth_controller.login_required(self.tour_controller.index))
        self.app.route('/search')(self.auth_controller.login_required(
            lambda: self.tour_controller.search(request.args.get('term', '').strip())
        ))
        self.app.route('/purchased')(self.auth_controller.login_required(self.tour_controller.purchased))

        # User routes
        self.app.route('/profile')(self.auth_controller.login_required(self.user_controller.profile))

        # Chat routes
        self.app.route('/chat')(self.auth_controller.login_required(self.chat_controller.chat))

    def _register_socket_events(self):
        @self.socketio.on('message')
        @self.auth_controller.login_required
        def handle_message(msg):
            self.chat_controller.handle_message(msg)

    def run(self, debug=True):
        self.socketio.run(self.app, debug=debug)

if __name__ == '__main__':
    flask_app = FlaskApp()
    flask_app.run(debug=False)
