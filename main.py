import flet as ft
from pages.home import HomePage
from pages.login import LoginPage
from pages.settings import SettingsPage
import logger

class MyApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self._configure_page()
        self._setup_routes()

    def _configure_page(self):
        """Базовая конфигурация страницы."""
        self.page.adaptive = True
        self.page.theme_mode = ft.ThemeMode.DARK if self.page.client_storage.get("theme_mode") == "dark" else ft.ThemeMode.LIGHT
        self.page.device_type = self._get_device_type()
        self._apply_device_settings()

    def _get_device_type(self) -> str:
        """Определение типа устройства по User Agent."""
        ua = self.page.client_user_agent.lower()
        if any(device in ua for device in ['iphone', 'android']) and 'tablet' not in ua:
            return "mobile"
        if any(device in ua for device in ['ipad', 'tablet']):
            return "tablet"
        return "desktop"

    def _apply_device_settings(self):
        """Применение настроек в зависимости от типа устройства."""
        is_mobile = self.page.device_type in ["mobile", "tablet"]
        self.page.padding = 10 if is_mobile else 20
        self.page.spacing = 10 if is_mobile else 20
        self.page.scroll = "adaptive"
        self.page.scale = 1.0

    def _setup_routes(self):
        """Настройка маршрутизации."""
        routes = {"/": HomePage, "/settings": SettingsPage, "/login": LoginPage}

        def route_change(route):
            logger.logger.info(f"Переход на страницу: {route.route}")
            self.page.views.clear()
            self.page.views.append(routes.get(route.route, HomePage)(self.page))
            self.page.update()

        self.page.on_route_change = route_change
        self.page.go("/login")

def main(page: ft.Page):
    MyApp(page)

if __name__ == "__main__":
    ft.app(target=main,
           view=ft.WEB_BROWSER,
           port=8550
    )
