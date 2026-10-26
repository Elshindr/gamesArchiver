import flet as ft
from typing import Callable
#from models.games import GameRawg
from database.orm import Game

class ViewSidePanelDetailGame:

    @staticmethod
    def get_paneldetail(
        game: Game,
        fermer_panel: Callable[[ft.ControlEvent], None],
        on_add_game: Callable[[ft.ControlEvent], None],
    ) -> ft.Control:

        # Données
        platforms = (
            [platform.name for platform in game.platforms] if game.platforms else []
        )

        genres = game.genres or []
        tags = game.tags or []

        released = str(game.release) if game.release else "Non renseignée"
        playtime = f"{game.playtimeHltb} h" if game.playtimeHltb else "Non renseigné"

        # Header
        header = ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            game.name,
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=3,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    tooltip="Fermer",
                    on_click=fermer_panel,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        async def handle_add_game(e: ft.ControlEvent):
            await on_add_game(game)

        footer = ft.Row(
            controls=[
                ft.Button(
                    content="Ajouter",
                    icon=ft.Icons.ADD,
                    tooltip="Ajouter à ma bibliothéque",
                    on_click=handle_add_game,
                ),
                ft.Button(
                    content="Fermer",
                    icon=ft.Icons.CLOSE_ROUNDED,
                    tooltip="Fermer",
                    on_click=fermer_panel,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=20,
            expand=True,
        )

        # Image
        image = ft.Container(
            content=ft.Image(
                src=game.imageUrl or None,
                width=350,
                #height=float("inf"),
                fit=ft.BoxFit.COVER,
                border_radius=ft.BorderRadius.all(12),
                placeholder_src="Non renseignée",
            ),
            border_radius=12,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        # General
        infos = ft.Column(
            [
                ft.Text(
                    "Informations",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    [
                        ViewSidePanelDetailGame.info_card(
                            ft.Icons.CALENDAR_MONTH, "Sortie", released, 150
                        ),
                        ViewSidePanelDetailGame.info_card(
                            ft.Icons.SCHEDULE, "Temps de jeu (h)", playtime, 150
                        ),
                    ],
                    spacing=10,
                ),
                ViewSidePanelDetailGame.info_card(
                    ft.Icons.VIDEOGAME_ASSET,
                    "Plateformes",
                    ", ".join(platforms) if platforms else "Non renseignées",
                    310,
                ),
            ],
            spacing=10,
        )

        # Genres
        genres_section = ft.Column(
            [
                ft.Text(
                    "Genres",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ViewSidePanelDetailGame.chip_list(genres),
            ],
            spacing=8,
        )

        # Tags
        tags_section = ft.Column(
            [
                ft.Text(
                    "Tags",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ViewSidePanelDetailGame.chip_list(tags),
            ],
            spacing=8,
        )

        # Panel
        return ft.Container(
            content=ft.Column(
                [
                    header,
                    image,
                    infos,
                    genres_section,
                    tags_section,
                    ft.Divider(),
                    footer,
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=15,
            expand=True,
        )

    @staticmethod
    def chip_list(
        items: list[str],
    ) -> ft.Control:

        if not items:
            return ft.Text(
                "Non renseigné",
                # color=ft.Colors.PRIMARY,
                size=12,
            )

        return ft.Row(
            [
                ft.Container(
                    content=ft.Text(value=item, color=ft.Colors.ON_PRIMARY_CONTAINER),
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    padding=ft.Padding.symmetric(
                        horizontal=10,
                        vertical=6,
                    ),
                    border_radius=20,
                )
                for item in items
            ],
            wrap=True,
            spacing=6,
            run_spacing=6,
        )

    @staticmethod
    def info_card(icon: str, label: str, value: str, width: int) -> ft.Control:

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            icon,
                            size=20,
                        ),
                        width=25,
                        height=25,
                        alignment=ft.Alignment.CENTER,
                        border_radius=8,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                label,
                                size=11,
                                # color=ft.Colors.GREY_500,
                            ),
                            ft.Text(
                                value,
                                size=13,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=12,
            ),
            padding=10,
            border_radius=10,
            border=ft.Border.all(
                1,
                ft.Colors.OUTLINE_VARIANT,
            ),
            width=width,
        )
