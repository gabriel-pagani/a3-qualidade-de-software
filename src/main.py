import flet as ft
import os
from views.auth import AuthView
from views.home import HomeView


class Main:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.auth_view()

    def setup_page(self):
        async def center_window():
            await self.page.window.center()
        
        self.page.title = 'Kryptex'
        self.page.window.icon = os.path.join(os.path.dirname(__file__), "assets", "favicon.png")
        self.page.window.width = 550
        self.page.window.min_width = 550
        self.page.window.height = 750
        self.page.window.min_height = 750
        self.page.run_task(center_window)
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = ft.Colors.WHITE
        self.page.padding = 0
        self.page.update()

    def auth_view(self):
        AuthView(self.page, on_login_success=self.home_view).show_login()

    def home_view(self, user, user_key):
        HomeView(self.page, user, user_key, on_logout=self.logout).show_home()

    def logout(self, e):
        self.auth_view()


def main(page: ft.Page):
    Main(page)


ft.run(main, assets_dir="assets")
