# base_view.py
import flet as ft

class BaseView(ft.View):
    """Базовый класс для всех страниц."""
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.spacing, self.padding = 20, 40
        self._build()

    def _build(self):
        """Дочерние классы переопределяют этот метод."""
        pass
