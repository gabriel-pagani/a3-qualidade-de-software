import flet as ft


def show_message(page: ft.Page, type: str, message: str):
    colors = {
        "success": [ft.Colors.GREEN, ft.Colors.WHITE],   # Success
        "warning": [ft.Colors.YELLOW, ft.Colors.BLACK],  # Warning
        "error": [ft.Colors.RED, ft.Colors.WHITE],       # Error
        "info": [ft.Colors.GREY, ft.Colors.BLACK],       # Info
    }

    page.overlay.append(
        ft.SnackBar(
            content=ft.Text(message, color=colors[type][1]),
            bgcolor=colors[type][0],
            open=True
        )
    )

    page.update()
