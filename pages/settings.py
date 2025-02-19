import flet as ft
from base_view import BaseView

class SettingsPage(BaseView):
    def _build(self):
        self._load_theme()
        self.controls = [
            ft.Text("Settings Page", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Toggle Theme", on_click=self._toggle_theme),
            ft.ElevatedButton("Go to Home", on_click=lambda _: self.page.go("/")),
            ft.ElevatedButton("Logout", on_click=self._logout, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
        ]

    def _load_theme(self):
        """Загружаем сохранённую тему."""
        self.page.theme_mode = ft.ThemeMode.DARK if self.page.client_storage.get("theme_mode") == "dark" else ft.ThemeMode.LIGHT

    def _toggle_theme(self, _):
        """Переключение темы."""
        new_theme = ft.ThemeMode.DARK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        self.page.theme_mode = new_theme
        self.page.client_storage.set("theme_mode", "dark" if new_theme == ft.ThemeMode.DARK else "light")
        self.page.update()

    def _logout(self, _):
        """Выход из аккаунта."""
        self.page.client_storage.set("logged_in", False)
        self.page.go("/login")  # Перенаправляем на страницу входа
        self.page.update()
