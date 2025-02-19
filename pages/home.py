import flet as ft
from base_view import BaseView

class HomePage(BaseView):
    def _build(self):
        device_type = self.page.device_type

        if device_type == "desktop":
            self.controls = [
                ft.Row([
                    ft.Text("Welcome to the Desktop Home Page!", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("Go to Desktop Settings", on_click=lambda _: self.page.go("/settings"))
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text(f"You're using a {device_type}.", size=18)
            ]
        elif device_type == "tablet":
            self.controls = [
                ft.Column([
                    ft.Text("Welcome to the Tablet Home Page!", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(f"You're using a {device_type}.", size=18),
                    ft.ElevatedButton("Go to Tablet Settings", on_click=lambda _: self.page.go("/settings"))
                ], alignment=ft.MainAxisAlignment.CENTER)
            ]
        else:  # mobile
            self.controls = [
                ft.Column([
                    ft.Text("Welcome to the Mobile Home Page!", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(f"You're using a {device_type}.", size=18),
                    ft.ElevatedButton("Go to Mobile Settings", on_click=lambda _: self.page.go("/settings"))
                ], spacing=10, alignment=ft.MainAxisAlignment.START)
            ]
