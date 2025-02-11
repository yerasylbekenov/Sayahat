import requests
import logging
from configs.config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_API_URL

logger = logging.getLogger(__name__)

class PayPalAPI:
    def __init__(self):
        self.client_id = PAYPAL_CLIENT_ID
        self.client_secret = PAYPAL_CLIENT_SECRET
        self.api_url = PAYPAL_API_URL

    def get_access_token(self):
        """Получение токена доступа для PayPal API"""
        auth_url = f"{self.api_url}/v1/oauth2/token"
        auth_data = {
            'grant_type': 'client_credentials'
        }
        auth_headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        try:
            response = requests.post(auth_url, data=auth_data, headers=auth_headers, auth=(self.client_id, self.client_secret))
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting access token: {e}")
            return None

    def create_payment(self, amount, currency, description):
        """Создание платежа через PayPal API"""
        access_token = self.get_access_token()
        if not access_token:
            return "Ошибка: Не удалось получить токен доступа."

        payment_url = f"{self.api_url}/v1/payments/payment"
        payment_data = {
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": "{:.2f}".format(amount),
                    "currency": currency
                },
                "description": description
            }],
            "redirect_urls": {
                "return_url": "https://sayahat.website/payment/success",
                "cancel_url": "https://sayahat.website/"
            }
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        try:
            response = requests.post(payment_url, json=payment_data, headers=headers)
            response.raise_for_status()
            print(response.json())
            approval_url = next((link['href'] for link in response.json().get("links", []) if link["rel"] == "approval_url"), None)
            if approval_url:
                return f"Платёж успешно создан! Перейдите по ссылке для подтверждения: {approval_url}"
            else:
                return "Ошибка: Не удалось найти ссылку для подтверждения платежа."
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating payment: {e}")
            return "Ошибка при создании платежа!"

    def execute_payment(self, payment_id, payer_id):
        """Подтверждает и завершает платеж"""
        access_token = self.get_access_token()
        if not access_token:
            return "Ошибка: Не удалось получить токен доступа."

        execute_url = f"{self.api_url}/v1/payments/payment/{payment_id}/execute"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        data = {
            "payer_id": payer_id
        }
        try:
            response = requests.post(execute_url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error executing payment: {e}")
            return "Ошибка при подтверждении платежа!"

    def get_payment_status(self, payment_id):
        """Проверяет статус платежа по его ID"""
        access_token = self.get_access_token()
        if not access_token:
            return "Ошибка: Не удалось получить токен доступа."

        payment_url = f"{self.api_url}/v1/payments/payment/{payment_id}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        try:
            response = requests.get(payment_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting payment status: {e}")
            return "Ошибка при проверке статуса платежа!"