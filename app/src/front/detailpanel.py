import flet as ft
from typing import Callable
from models.games import GameRawg


class ViewSidePanelDetailGame:

    @staticmethod
    def get_paneldetail(
        game: GameRawg,
        fermer_panel: Callable[[ft.ControlEvent], None],
    ) -> ft.Control:

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            f"{game.name}",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            tooltip="Fermer",
                            on_click=fermer_panel,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Image(
                    src=game.background_image or "",
                    width=490,
                    height=490,
                    fit= ft.BoxFit.FIT_WIDTH,
                    
                ),
                ft.Text(f"ID : {game.id}"),
                ft.Text(f"Date de sortie : " f"{game.released or 'Non spécifiée'}"),
                ft.Text(
                    "Plateformes : "
                    + (
                        ", ".join(game.platforms)
                        if game.platforms
                        else "Non spécifiées"
                    )
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
