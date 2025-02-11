import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Flask, request
from flask_socketio import SocketIO
from configs.config import SECRET_KEY
from data import database
from utils import mail, image
from ai_2 import GigaChatClient
from payments_api import PayPalAPI
from controllers import auth_controller, chat_controller, tour_controller, user_controller, payments_controller

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = SECRET_KEY
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # Initialize services
        self.ps = PayPalAPI()
        self.db = database.Database()
        self.email_verifier = mail.EmailVerifier()
        self.chat_client = GigaChatClient()
        self.uploader = image.ImageBBUploader()

        # Initialize controllers
        self.auth_controller = auth_controller.AuthController(self.db, self.email_verifier)
        self.tour_controller = tour_controller.TourController(self.db)
        self.user_controller = user_controller.UserController(self.db, self.uploader)
        self.chat_controller = chat_controller.ChatController(self.db, self.chat_client)
        self.payments_controller = payments_controller.PaymentsController(self.db, self.ps)

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
        self.app.route('/up_photo', methods=['POST'])(self.auth_controller.login_required(self.user_controller.up_photo))

        # Chat routes
        self.app.route('/chat')(self.auth_controller.login_required(self.chat_controller.chat))

        # payments routes
        self.app.route('/payments')(self.auth_controller.login_required(self.payments_controller.payments))
        self.app.route('/create_ps', methods=['POST'])(self.auth_controller.login_required(self.payments_controller.create_pslink))
        self.app.route('/payment/success')(self.auth_controller.login_required(self.payments_controller.payment_success))

    def _register_socket_events(self):
        @self.socketio.on('message')
        def handle_message(msg):
            try:
                self.chat_controller.handle_message(msg)
            except Exception as e:
                logger.error(f"Error handling message: {e}")

    def run(self, host='127.0.0.1', port=5000, debug=True):
        self.socketio.run(self.app, host=host, port=port, debug=debug)

if __name__ == '__main__':
    try:
        flask_app = FlaskApp()
        flask_app.run()
    except Exception as e:
        logger.error(f"Error starting application: {e}", exc_info=True)