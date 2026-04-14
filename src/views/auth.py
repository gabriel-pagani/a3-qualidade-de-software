import flet as ft
from controllers.user import User
from utils.ui import show_message
from utils.validator import validate_master_password


class AuthView:
    def __init__(self, page: ft.Page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success

    def show_login(self, prefilled_username: str = None):
        def do_login(e):
            username = username_input.value.strip()
            master_password = master_password_input.value.strip()

            if not username:
                show_message(self.page, 'warning', 'The username field is required!')
            elif not master_password:
                show_message(self.page, 'warning', 'The master password field is required!')
            else:
                user, user_key, msg_type, msg = User.login(username, master_password)
                if user: 
                    show_message(self.page, msg_type, msg)
                    self.on_login_success(user, user_key)
                else:
                    show_message(self.page, msg_type, msg)

        def go_register(e):
            self.show_register()


        # Components
        title = ft.Text(
            "Kryptex!", 
            size=70,
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLUE_900
        )

        last_username = prefilled_username or User.get_last_logged_user() or ""
        username_input = ft.TextField(
            label="Username",
            prefix_icon=ft.Icons.PERSON,
            hint_text="Enter your username here...",
            value=last_username,
            autofocus=not bool(last_username),
            width=400,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            on_submit=do_login,
        )

        master_password_input = ft.TextField(
            label="Master password",
            prefix_icon=ft.Icons.LOCK,
            hint_text="Enter your master password here...",
            autofocus=bool(last_username),
            password=True,
            width=400,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            on_submit=do_login,
        )

        login_button = ft.Button(
            content="Login",
            width=400,
            height=50,
            bgcolor=ft.Colors.BLUE_900,
            color=ft.Colors.WHITE,
            on_click=do_login,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )

        register_button = ft.Button(
            content="Create account",
            width=400,
            height=50,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLUE_900,
            on_click=go_register,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )

        # Layout
        content = ft.Column(
            controls=[
                title,
                ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                username_input,
                master_password_input,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                login_button,
                register_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )

        container = ft.Container(
            content=content,
            expand=True,
            alignment=ft.Alignment.CENTER
        )
        
        self.page.clean()
        self.page.add(container)

    def show_register(self):
        def do_register(e):
            username = username_input.value.strip()
            master_password = master_password_input.value.strip()
            master_password_confirmed = master_password_confirmed_input.value.strip()

            if not username:
                show_message(self.page, 'warning', 'The username field is required!')
            elif not master_password:
                show_message(self.page, 'warning', 'The master password field is required!')
            elif not master_password_confirmed:
                show_message(self.page, 'warning', 'The master password confirmation field is required!')
            elif master_password != master_password_confirmed:
                show_message(self.page, 'warning', "The passwords don't match!")
            elif not validate_master_password(master_password):
                show_message(self.page, 'warning', "Weak password! The password must contain at least 15 characters or more.")
            else:
                new_user, msg_type, msg = User.create(username, master_password)

                if new_user:
                    show_message(self.page, msg_type, msg)
                    self.show_login(prefilled_username=username)
                
                else:
                    show_message(self.page, msg_type, msg)

        def go_login(e):
            self.show_login()

        # Components
        title = ft.Text(
            "Create Account", 
            size=70, 
            weight=ft.FontWeight.BOLD, 
            color=ft.Colors.BLUE_900
        )

        username_input = ft.TextField(
            label="Username",
            prefix_icon=ft.Icons.PERSON,
            hint_text="Enter your username here...",
            width=400,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            on_submit=do_register,
        )

        def show_master_password_confirmed_input(e: ft.ControlEvent):
            has_value = bool(e.control.value)
            master_password_confirmed_input.visible = has_value
            if not has_value:
                master_password_confirmed_input.value = ""
            master_password_confirmed_input.update()

        master_password_input = ft.TextField(
            label="Master password",
            prefix_icon=ft.Icons.LOCK,
            hint_text="Enter your master password here...",
            password=True,
            width=400,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            on_change=show_master_password_confirmed_input,
            on_submit=do_register,
        )

        master_password_confirmed_input = ft.TextField(
            label="Confirm master password",
            prefix_icon=ft.Icons.LOCK,
            hint_text="Confirm your master password here...",
            password=True,
            can_reveal_password=True,
            width=400,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            visible=False,
            on_submit=do_register,
        )

        register_button = ft.Button(
            content="Create account",
            width=400,
            height=50,
            bgcolor=ft.Colors.BLUE_900,
            color=ft.Colors.WHITE,
            on_click=do_register,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )

        login_button = ft.Button(
            content="I already have an account",
            width=400,
            height=50,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLUE_900,
            on_click=go_login,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )

        # Layout
        content = ft.Column(
            controls=[
                title,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                username_input,
                master_password_input,
                master_password_confirmed_input,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                register_button,
                login_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )

        container = ft.Container(
            content=content,
            expand=True,
            alignment=ft.Alignment.CENTER
        )

        self.page.clean()
        self.page.add(container)
