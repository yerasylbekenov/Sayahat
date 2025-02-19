import flet as ft
from base_view import BaseView
import asyncio

class LoginPage(BaseView):
    def _build(self):
        if self.page.client_storage.get("logged_in"):
            self.page.go("/")
            return

        self.email, self.password = ft.TextField(label="Email", width=300, autofocus=True), ft.TextField(label="Password", password=True, width=300)
        login_button = ft.CupertinoFilledButton("Login", on_click=self._handle_login, width=300)

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [ft.Text("Login", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER), self.email, self.password, login_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
            )
        ]

    def _handle_login(self, _=None):
        valid_email, valid_password = self.email.value == "admin", self.password.value == "admin"
        self.email.border_color, self.password.border_color = ("red" if not valid_email else "black"), ("red" if not valid_password else "black")
        self.page.update()

        if valid_email and valid_password:
            self.page.client_storage.set("logged_in", True)
            self.page.go("/")
        else:
            self.page.run_task(self._reset_border)

    async def _reset_border(self):
        await asyncio.sleep(2)
        self.email.border_color = self.password.border_color = "black"
        self.page.update()