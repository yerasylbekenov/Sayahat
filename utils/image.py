import requests
import logging
from configs.config import IMG_KEY

logger = logging.getLogger(__name__)

class ImageBBUploader:
    """
    Класс для загрузки изображений на ImageBB.
    """
    
    def __init__(self):
        """
        Инициализирует объект загрузчика с API-ключом.
        """
        self.api_key = IMG_KEY
        self.upload_url = "https://api.imgbb.com/1/upload"

    def upload_image(self, image_bytes: bytes, filename: str = "image.jpg") -> str:
        """
        Загружает изображение на ImageBB и возвращает URL загруженного изображения.
        """
        try:
            response = requests.post(
                self.upload_url,
                params={"key": self.api_key},
                files={"image": (filename, image_bytes)}
            )
            response.raise_for_status()
            data = response.json()
            return data["data"]["url"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error uploading image: {e}")
            raise Exception(f"Ошибка загрузки изображения: {e}")