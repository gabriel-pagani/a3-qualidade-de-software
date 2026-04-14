import flet as ft
import shutil
import time
import asyncio
import gc
import os
from datetime import datetime
from utils.ui import show_message
from utils.cryptor import generate_password, decrypt_data, verify_hash
from utils.validator import validate_master_password
from database.connection import DB_PATH, is_valid_database_file
from controllers.password import Password
from controllers.password_type import PasswordType


class HomeView:
    def __init__(self, page: ft.Page, user, user_key, on_logout):
        self.page = page
        self.user = user
        self.user_key = user_key
        self.user_passwords = list()
        self.password_types = PasswordType.get_all()
        self.on_logout = on_logout
        self.is_active = True
        self.last_activity = time.time()
        self.timeout_seconds = 600

        self.page.on_keyboard_event = self.reset_timer
        self.page.run_task(self.monitor_inactivity)

    def reset_timer(self, e=None):
        self.last_activity = time.time()

    def logout(self, e):
        self.is_active = False 
        self.user_key = None
        self.user_passwords.clear()
        gc.collect()
        
        self.on_logout(e)

    def forced_logout(self):
        self.is_active = False
        self.user_key = None
        self.user_passwords.clear()
        self.page.pop_dialog()
        gc.collect()
        
        show_message(self.page, "warning", "Session expired due to inactivity! For security reasons, please log in again.")
        self.on_logout(None)

    async def monitor_inactivity(self):
        while self.is_active:
            await asyncio.sleep(1)
            if time.time() - self.last_activity > self.timeout_seconds:
                self.forced_logout()
                break

    def show_home(self):
        def refresh_page():
            try:
                self.password_types = PasswordType.get_all()
            except Exception:
                self.password_types = []

            type_dropdown.options = [
                *(ft.dropdown.Option(key=str(t.id), text=t.name) for t in self.password_types),
                ft.dropdown.Option(key="", text="Others"),
            ]

            tiles_list.controls = build_tiles_controls()
            self.page.update()
        
        # Dialogs components
        service_input = ft.TextField(
            label="Service", 
            prefix_icon=ft.Icons.PUBLIC,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=400,
        )
        
        login_input = ft.TextField(
            label="Login/Username", 
            prefix_icon=ft.Icons.PERSON,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=400,
        )
        
        password_input = ft.TextField(
            label="Password", 
            password=True, 
            can_reveal_password=True, 
            prefix_icon=ft.Icons.KEY,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=350,
        )

        def generate_random_password(e):
            password_input.value = generate_password()
            password_input.update()

        generate_password_button = ft.IconButton(
            icon=ft.Icons.AUTO_AWESOME,
            tooltip="Generate random password",
            on_click=generate_random_password
        )

        type_dropdown = ft.Dropdown(
            label="Type",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_900,
            width=300,
            options=[
                *(ft.dropdown.Option(key=str(t.id), text=t.name) for t in self.password_types),
                ft.dropdown.Option(key="", text="Others"),
            ],
            key="",
            text="Others",
            leading_icon=ft.Icons.CATEGORY,
        )

        new_password_type_input = ft.TextField(
            label="Password type name",
            prefix_icon=ft.Icons.LABEL,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=400,
        )

        create_password_type_button = ft.IconButton(
            icon=ft.Icons.ADD,
            tooltip="Create new password type",
            on_click=...,
        )

        delete_password_type_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip="Delete password type",
            on_click=...,
        )

        url_input = ft.TextField(
            label="URL", 
            prefix_icon=ft.Icons.LINK,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=400,
        )
        
        notes_input = ft.TextField(
            label="Notes", 
            multiline=True, 
            min_lines=3,
            max_lines=3,
            prefix_icon=ft.Icons.CREATE,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=400,
        )

        account_username_input = ft.TextField(
            label="Username",
            prefix_icon=ft.Icons.PERSON,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=400,
        )

        current_master_password_input = ft.TextField(
            label="Current master password",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=400,
        )

        def show_confirm_new_master_password(e: ft.ControlEvent):
            has_value = bool(e.control.value)
            confirm_new_master_password_input.visible = has_value
            if not has_value:
                confirm_new_master_password_input.value = ""
                confirm_new_master_password_input.error = None
            confirm_new_master_password_input.update()

        new_master_password_input = ft.TextField(
            label="New master password",
            prefix_icon=ft.Icons.LOCK_RESET,
            password=True,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=400,
            on_change=show_confirm_new_master_password,
        )

        confirm_new_master_password_input = ft.TextField(
            label="Confirm new master password",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=400,
            visible=False,
        )

        kill_switch_password_input = ft.TextField(
            label="Confirm your master password",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.BLUE_400,
            cursor_color=ft.Colors.BLUE_900,
            width=400,
        )

        # Dialogs
        def close_dialog(e):
            service_input.error = None
            password_input.error = None
            type_dropdown.error_text = None
            
            service_input.value = ""
            login_input.value = ""
            password_input.value = ""
            url_input.value = ""
            notes_input.value = ""
            type_dropdown.value = ""
            
            self.page.pop_dialog()       

        def open_new_password_dialog(e):
            self.page.show_dialog(new_password_dialog)

        def save_new_password(e):
            service_input.error = None
            password_input.error = None
            
            has_error = False

            if not service_input.value:
                service_input.error = 'The service field is required!'
                has_error = True

            if not password_input.value:
                password_input.error = 'The password field is required!'
                has_error = True
            
            if has_error:
                service_input.update()
                password_input.update()
                return

            # SPLIT-CRYPTO: Metadados isolados
            meta_data = {
                "service": service_input.value,
                "login": login_input.value,
                "url": url_input.value,
            }
            
            # SPLIT-CRYPTO: Segredos isolados
            secret_data = {
                "password": password_input.value,
                "notes": notes_input.value,
            }
            
            new_password = Password.create(
                user_id=self.user.id,
                user_key=self.user_key,
                meta_data=meta_data,
                secret_data=secret_data,
                type_id=int(type_dropdown.value) if type_dropdown.value else None,
            )

            if new_password:
                close_dialog(e)
                show_message(self.page, "success", "Password saved successfully!")
                refresh_page()
            else:
                close_dialog(e)
                show_message(self.page, "error", "Error saving password! Please try again later.")   
        
        new_password_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("New password"),
            content=ft.Column(
                controls=[
                    service_input,
                    login_input,
                    ft.Row(
                        controls=[password_input, generate_password_button], 
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    ft.Row(
                        controls=[type_dropdown, create_password_type_button, delete_password_type_button],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    url_input,
                    notes_input
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                height=450,
                alignment=ft.MainAxisAlignment.START,
                spacing=10
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Save", on_click=save_new_password),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )


        def open_new_password_type_dialog(e):
            new_password_type_input.value = ""
            new_password_type_input.error = None
            self.page.show_dialog(new_password_type_dialog)

        def save_new_password_type(e):
            new_password_type_input.error = None
            name = (new_password_type_input.value or "").strip()

            if not name:
                new_password_type_input.error = "Password type name is required!"
                new_password_type_input.update()
                return
            
            for password_type in self.password_types:
                if name.lower() == password_type.name.lower().strip():
                    new_password_type_input.error = "This password type already exists!"
                    new_password_type_input.update()
                    return
                
            if name.lower() == 'others':
                    new_password_type_input.error = "This password type already exists!"
                    new_password_type_input.update()
                    return

            created = PasswordType.create(name)
            if created:
                show_message(self.page, "success", "Password type created successfully!")
                self.page.pop_dialog()
                type_dropdown.value = str(created.id)
                refresh_page()
            else:
                show_message(self.page, "error", "Error creating type! Please try again later.")
                self.page.pop_dialog()
                refresh_page()

        def confirm_delete_password_type(e):
            type_dropdown.error_text = None
            selected = (type_dropdown.value or "").strip()
            
            if not selected:
                type_dropdown.error_text = 'Password type "Others" cannot be deleted!'
                return

            selected_type = PasswordType.get(int(selected))
            if not selected_type:
                type_dropdown.error_text = "Selected password type not found!"
                return

            def do_delete(e):
                ok = selected_type.delete()
                self.page.pop_dialog()
                if ok:
                    type_dropdown.value = ""
                    show_message(self.page, "success", "Password type deleted successfully!")
                    refresh_page()
                else:
                    type_dropdown.error_text = "Error!"

            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm deletion"),
                content=ft.Text(f'Delete type "{selected_type.name}"?'),
                actions=[
                    ft.TextButton("No", on_click=close_dialog),
                    ft.TextButton("Yes", on_click=do_delete),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.show_dialog(confirm_dialog)

        create_password_type_button.on_click = open_new_password_type_dialog

        delete_password_type_button.on_click = confirm_delete_password_type

        new_password_type_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("New password type"),
            content=ft.Column(
                controls=[
                    new_password_type_input,
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                height=100,
                spacing=10,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Save", on_click=save_new_password_type),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )


        editing_password: Password | None = None
        def open_edit_password_dialog(e, password: Password):
            nonlocal editing_password
            editing_password = password
            
            associated_data = f"user_id:{self.user.id};".encode()
            
            # Abre os dois cofres de forma independente
            meta_data = decrypt_data(self.user_key, password.metadata_iv, password.encrypted_metadata, associated_data)
            secret_data = decrypt_data(self.user_key, password.secret_iv, password.encrypted_secret, associated_data)

            service_input.value = meta_data.get("service")
            login_input.value = meta_data.get("login")
            url_input.value = meta_data.get("url")
            
            password_input.value = secret_data.get("password")
            notes_input.value = secret_data.get("notes")
            
            # O tipo de password agora vem diretamente do objeto do banco, não do JSON
            type_dropdown.value = str(password.type_id) if password.type_id else ""
            
            last_changed_str = password.updated_at or password.created_at
            if last_changed_str:
                try:
                    last_changed = datetime.strptime(last_changed_str, "%Y-%m-%d %H:%M:%S")
                    days_passed = (datetime.now() - last_changed).days
                    if days_passed >= 90:
                        password_input.error = f"No changes in the last {days_passed} days!"
                except Exception:
                    pass

            self.page.show_dialog(edit_password_dialog)
        
        def save_edited_password(e, password: Password):
            service_input.error = None
            password_input.error = None
            
            has_error = False

            if not service_input.value:
                service_input.error = 'The service field is required!'
                has_error = True

            if not password_input.value:
                password_input.error = 'The password field is required!'
                has_error = True
            
            if has_error:
                service_input.update()
                password_input.update()
                return
            
            meta_data = {
                "service": service_input.value,
                "login": login_input.value,
                "url": url_input.value,
            }
            
            secret_data = {
                "password": password_input.value,
                "notes": notes_input.value,
            }

            updated = Password.get(password.id).update(
                user_key=self.user_key,
                type_id=int(type_dropdown.value) if type_dropdown.value else 0,
                meta_data=meta_data,
                secret_data=secret_data,
            )

            if updated:
                close_dialog(e)
                show_message(self.page, "success", "Password edited successfully!")
                refresh_page()
            else:
                close_dialog(e)
                show_message(self.page, "error", "Error editing password! Please try again later.")

        def confirm_delete_password(e, password: Password):
            if password and Password.get(password.id):
                Password.get(password.id).delete()
                
                self.page.pop_dialog()  # Close the deletion confirmation dialog
                close_dialog(e)         # Close the password editing dialog
                show_message(self.page, "success", "Password deleted successfully!")
                refresh_page()
            else:
                self.page.pop_dialog()  # Close the deletion confirmation dialog
                close_dialog(e)         # Close the password editing dialog
                show_message(self.page, "error", "Error deleting password! Please try again later.")

        def open_delete_password_dialog(e, password: Password):
            delete_password_confirmation_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm deletion"),
                content=ft.Text("Are you sure you want to delete this password? This action cannot be undone."),
                actions=[
                    ft.TextButton("No", on_click=close_dialog),
                    ft.TextButton("Yes", on_click=lambda e: confirm_delete_password(e, password)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self.page.show_dialog(delete_password_confirmation_dialog)

        edit_password_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit password"),
            content=ft.Column(
                controls=[
                    service_input,
                    login_input,
                    ft.Row(
                        controls=[password_input, generate_password_button], 
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    ft.Row(
                        controls=[type_dropdown, create_password_type_button, delete_password_type_button],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    url_input,
                    notes_input
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                height=450,
                alignment=ft.MainAxisAlignment.START,
                spacing=10
            ),
            actions=[
                ft.TextButton("Delete", on_click=lambda e: open_delete_password_dialog(e, editing_password)),
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Save", on_click=lambda e: save_edited_password(e, editing_password)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )


        def open_my_account_dialog(e):
            current_master_password_input.value = ""
            current_master_password_input.error = None
            
            account_username_input.value = self.user.username
            account_username_input.error = None

            new_master_password_input.value = ""
            new_master_password_input.error = None
            
            confirm_new_master_password_input.value = ""
            confirm_new_master_password_input.error = None
            confirm_new_master_password_input.visible = False

            self.page.show_dialog(my_account_dialog)

        def save_account_changes(e):
            # reset errors
            current_master_password_input.error = None
            account_username_input.error = None
            new_master_password_input.error = None
            confirm_new_master_password_input.error = None

            current_pw = (current_master_password_input.value or "").strip()
            new_username = (account_username_input.value or "").strip()
            new_pw = (new_master_password_input.value or "").strip()
            new_pw_confirm = (confirm_new_master_password_input.value or "").strip()

            has_error = False

            if not current_pw:
                current_master_password_input.error = "Current master password is required!"
                has_error = True

            if (not new_username or new_username == self.user.username) and not new_pw:
                account_username_input.error = "Nothing to update!"
                new_master_password_input.error = "Nothing to update!"
                has_error = True

            if new_pw:
                if not new_pw_confirm:
                    confirm_new_master_password_input.error = "Please confirm the new master password!"
                    has_error = True
                elif not validate_master_password(new_pw):
                    new_master_password_input.error = "Weak password! Use at least 15 characters."
                    has_error = True
                elif new_pw != new_pw_confirm:
                    confirm_new_master_password_input.error = "The new passwords don't match!"
                    has_error = True
                
            if has_error:
                account_username_input.update()
                current_master_password_input.update()
                new_master_password_input.update()
                confirm_new_master_password_input.update()
                return

            updated = self.user.update(
                current_master_password=current_pw,
                new_username=new_username if new_username and new_username != self.user.username else None,
                new_master_password=new_pw if new_pw else None,
            )

            if not updated:
                self.page.pop_dialog()
                show_message(self.page, "error", "Error updating account! Please try again later.")
                return

            self.page.pop_dialog()
            self.on_logout(e)
            show_message(self.page, "success", "Account successfully updated! For your security, please log in again.")

        def execute_kill_switch(e):
            kill_switch_password_input.error = None
            password = (kill_switch_password_input.value or "").strip()

            if not password:
                kill_switch_password_input.error = "Current master password is required!"
                kill_switch_password_input.update()
                return

            if not verify_hash(self.user.master_password_hash, password):
                kill_switch_password_input.error = "Incorrect master password! Action denied."
                kill_switch_password_input.update()
                return

            success = self.user.delete()
            if success:
                close_dialog(e)  # delete_account_dialog
                close_dialog(e)  # my_account_dialog
                show_message(self.page, "success", "Account successfully deleted!")
                self.logout(e)
            else:
                close_dialog(e)
                show_message(self.page, "error", "Failed to delete account! Please try again later.")

        def open_delete_account_dialog(e):
            kill_switch_password_input.value = ""
            kill_switch_password_input.error = None
            self.page.show_dialog(delete_account_dialog)

        delete_account_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.RED), ft.Text("Delete Account", color=ft.Colors.RED)]),
            content=ft.Column(
                controls=[
                    ft.Text("WARNING: This action is irreversible. All your passwords and data will be permanently deleted."),
                    kill_switch_password_input,
                ],
                height=140,
                spacing=25
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton(content=ft.Text("Delete Account", color=ft.Colors.RED), on_click=execute_kill_switch),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        my_account_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Update account"),
            content=ft.Column(
                controls=[
                    current_master_password_input,
                    account_username_input,
                    new_master_password_input,
                    confirm_new_master_password_input,
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                height=360,
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
            actions=[
                ft.TextButton(content=ft.Text("Delete Account", color=ft.Colors.RED), on_click=open_delete_account_dialog),
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Save", on_click=save_account_changes),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Page components
        def build_tiles_controls() -> list[ft.Control]:
            self.user_passwords = Password.get_all_by_user(self.user.id)
            
            # Groups passwords by type
            passwords_by_type = dict()
            for type in self.password_types:
                temp_passwords_by_type = list()
                for password in self.user_passwords:
                    if password.type_id == type.id:
                        temp_passwords_by_type.append(password)
                        
                passwords_by_type[type.name] = temp_passwords_by_type

            temp_passwords_by_type = list()
            for password in self.user_passwords:
                if password.type_id is None:
                    temp_passwords_by_type.append(password)
                        
                passwords_by_type['Others'] = temp_passwords_by_type

            # Create the expansion tiles based on the passwords_by_type dictionary
            expansion_tiles_controls = list()
            for password_type, passwords in passwords_by_type.items():
                tile_controls = list()
                for password in passwords:
                    try:
                        associated_data = f"user_id:{self.user.id};".encode()
                        # LÊ EXCLUSIVAMENTE OS METADADOS. A SENHA NUNCA TOCA NA RAM NESTA FASE.
                        meta_data = decrypt_data(self.user_key, password.metadata_iv, password.encrypted_metadata, associated_data)
                        service = meta_data.get("service", "Unknown Service")
                        login = meta_data.get("login", "")
                    except Exception:
                        service = "Error decrypting"
                        login = ""

                    tile_controls.append(
                        ft.ListTile(
                            title=ft.Text(service),
                            subtitle=ft.Text(login),
                            on_click=lambda e, p=password: open_edit_password_dialog(e, p),
                        )
                    )

                if not tile_controls:
                        continue
                
                expansion_tiles_controls.append(
                    ft.ExpansionTile(
                        title=ft.Text(password_type, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(f"{len(tile_controls)} item(s)", style=ft.TextStyle(italic=True)),
                        affinity=ft.TileAffinity.PLATFORM,
                        maintain_state=True,
                        shape=ft.RoundedRectangleBorder(
                            side=ft.BorderSide(color=ft.Colors.TRANSPARENT, width=0)
                        ),
                        collapsed_shape=ft.RoundedRectangleBorder(
                            side=ft.BorderSide(color=ft.Colors.TRANSPARENT, width=0)
                        ),
                        controls=tile_controls,
                    )
                )
            
            return expansion_tiles_controls

        menu_items = [
            ft.PopupMenuItem(
                content=ft.Row([ft.Icon(ft.Icons.REFRESH, ft.Colors.BLACK), ft.Text("Refresh app")]),
                on_click=lambda e: refresh_page(),
            ),
            ft.PopupMenuItem(
                content=ft.Row([ft.Icon(ft.Icons.PERSON, ft.Colors.BLACK), ft.Text("Update account"),]),
                on_click=open_my_account_dialog,
            )
        ]

        if self.user.is_admin:
            async def export_database(e):
                file_picker = ft.FilePicker()
                path = await file_picker.save_file(file_name=f"{time.strftime(r'%d_%m_%Y-%H_%M')}.sqlite3", file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=['sqlite3'])
                
                if path:
                    try:
                        shutil.copy(DB_PATH, path)
                        show_message(self.page, "success", "Database exported successfully!")
                    except Exception as ex:
                        show_message(self.page, "error", "Error exporting database! Please try again later.")
            
            def confirm_import_database(e, import_path):
                self.page.pop_dialog()
                
                if not is_valid_database_file(import_path):
                    show_message(self.page, "error", "The file provided is either not a valid Kryptex database or is corrupted.")
                    return
                
                backup_path = str(DB_PATH) + ".bak"
                try:
                    shutil.copy(DB_PATH, backup_path)
                    
                    shutil.copy(import_path, DB_PATH)
                    
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                        
                    show_message(self.page, "success", "Database imported successfully! Please log in again.")
                    self.logout(e)
                    
                except Exception as ex:
                    # rollback
                    if os.path.exists(backup_path):
                        shutil.copy(backup_path, DB_PATH)

                    show_message(self.page, "error", f"Error importing database! Please try again later.")

            async def import_database(e):
                file = await ft.FilePicker().pick_files(file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["sqlite3"], allow_multiple=False)
                
                import_confirmation_dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Confirm import"),
                    content=ft.Text("Importing a new database will overwrite all data in the system. This action cannot be undone. Are you sure?"),
                    actions=[
                        ft.TextButton("No", on_click=close_dialog),
                        ft.TextButton("Yes", on_click=lambda e: confirm_import_database(e, file[0].path)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                if file:
                    self.page.show_dialog(import_confirmation_dialog)
            
            menu_items.extend(
                [
                    ft.PopupMenuItem(
                        content=ft.Row(
                            [ft.Icon(ft.Icons.UPLOAD, ft.Colors.BLACK), ft.Text("Import passwords"),]
                        ),
                        on_click=import_database,
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD, ft.Colors.BLACK), ft.Text("Export passwords"),]),
                        on_click=export_database,
                    ),
                ]
            )

        menu_items.extend(
            [
                ft.PopupMenuItem(
                    content=ft.Row([ft.Icon(ft.Icons.ADD, ft.Colors.BLACK), ft.Text("New password"),]),
                    on_click=open_new_password_dialog,
                ),                
                ft.PopupMenuItem(
                    content=ft.Row([ft.Icon(ft.Icons.LOGOUT, ft.Colors.BLACK), ft.Text("Logout"),]),
                    on_click=self.logout,
                ),
            ]
        )

        popup_menu = ft.PopupMenuButton(
            items=menu_items,
            icon_color=ft.Colors.WHITE,
            icon_size=30,
        )

        top_bar = ft.AppBar(
            toolbar_height=80,
            title=ft.Container(
                content=ft.Text(
                    "Kryptex",
                    size=30,
                    weight=ft.FontWeight.W_500,
                ),
                padding=ft.Padding.only(left=16),
            ),
            center_title=False,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_900,
            actions=[
                ft.Container(popup_menu, padding=ft.Padding.only(right=16)),
            ],
        )

        tiles_list = ft.ListView(
            expand=True,
            spacing=6,
            padding=ft.Padding.only(left=12, right=12, top=8, bottom=12),
            controls=build_tiles_controls(),
        )

        # Layout
        content = ft.Column(
            controls=[
                top_bar,
                tiles_list,
            ],
            spacing=4,
            expand=True,
        )

        activity_watcher = ft.GestureDetector(
            content=content,
            on_hover=self.reset_timer,
            on_tap_down=self.reset_timer,
            on_pan_update=self.reset_timer,
            expand=True,
        )

        self.page.clean()       
        self.page.add(activity_watcher)
