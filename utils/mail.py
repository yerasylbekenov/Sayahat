import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import re
from configs import config

class EmailVerifier:
    def __init__(self):
        """
        Инициализация объекта для отправки email с использованием данных из конфигурации.
        """
        self.sender_email = config.SENDER_EMAIL
        self.sender_password = config.SENDER_PASSWORD
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT

    def is_valid_email(self, email):
        """
        Проверка валидности email.
        
        :param email: Email для проверки.
        :return: True, если email валиден, иначе False.
        """
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

    def generate_verification_code(self, length=6):
        """
        Генерация случайного кода для верификации.

        :param length: Длина кода верификации.
        :return: Сгенерированный код.
        """
        # Генерация случайного кода
        code = str(random.randint(100000, 999999))  # Генерация 6-значного кода
        print(code)
        return code

    def send_verification_email(self, to_email, db):
        """
        Отправка письма с кодом верификации на указанный email.

        :param to_email: Email получателя.
        :param db: Объект базы данных.
        :return: Возвращает код верификации, если письмо отправлено, иначе None.
        """
        if not self.is_valid_email(to_email):
            print("Некорректный email.")
            return None

        verification_code = self.generate_verification_code()

        user = db.get_user(to_email)
        if user:
            db.update_record('users', 'user_id', user.user_id, code=verification_code)
        else:
            print(f"Пользователь с email {to_email} не найден.")
            return None

        # HTML-шаблон для письма
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    text-align: center;
                    padding: 20px;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                    width: 400px;
                    margin: auto;
                }}
                h2 {{
                    color: #333;
                }}
                p {{
                    font-size: 16px;
                    color: #666;
                }}
                .code {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #ffffff;
                    background: #007bff;
                    padding: 10px 20px;
                    display: inline-block;
                    border-radius: 5px;
                    margin-top: 10px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #999;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Ваш код верификации</h2>
                <p>Используйте этот код для подтверждения входа:</p>
                <div class="code">{verification_code}</div>
                <p class="footer">Если вы не запрашивали этот код, просто игнорируйте это письмо.</p>
            </div>
        </body>
        </html>
        """

        try:
            # Настроим подключение к серверу с использованием SSL
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)

                msg = MIMEMultipart()
                msg['From'] = self.sender_email
                msg['To'] = to_email
                msg['Subject'] = "Код верификации"

                msg.attach(MIMEText(html_content, 'html'))

                server.sendmail(self.sender_email, to_email, msg.as_string())

            print(f'Письмо с кодом верификации отправлено на {to_email}.')
            return verification_code

        except Exception as e:
            print(f"Ошибка при отправке письма: {e}")
            return None