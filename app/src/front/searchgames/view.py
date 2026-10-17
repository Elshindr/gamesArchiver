import flet as ft
from typing import Callable, List
import flet_datatable2 as fdt
from models.games import GameRawg


class ViewSearch:

    #### TABLE
    COLUMNS = {
        "name": ["Name", fdt.DataColumnSize.L, ft.Alignment.CENTER_LEFT],
        "released": ["Released", fdt.DataColumnSize.S, ft.Alignment.CENTER],
        "platforms": ["Platforms", fdt.DataColumnSize.L, ft.Alignment.CENTER_LEFT],
        "genres": ["Genres", fdt.DataColumnSize.L, ft.Alignment.CENTER_LEFT],
        "tags": ["Tags", fdt.DataColumnSize.L, ft.Alignment.CENTER_LEFT],
        "playtime": ["Playtime (h)", fdt.DataColumnSize.S, ft.Alignment.CENTER],
    }


    @classmethod
    def get_data_columns(
        cls,
        on_sort: Callable[[ft.DataColumnSortEvent], None],
    ) -> list[fdt.DataColumn2]:
        """Génère les colonnes dans l'ordre exact de COLUMNS."""

        return [
            *[
                fdt.DataColumn2(
                    label=ft.Text(config[0]),
                    on_sort=on_sort,
                    heading_row_alignment=ft.MainAxisAlignment.CENTER,
                    size=config[1],
                )
                for col, config in cls.COLUMNS.items()
            ],
            # Colonne Actions
            fdt.DataColumn2(
                heading_row_alignment=ft.MainAxisAlignment.CENTER,
                label=ft.Text("Actions"),
                size=fdt.DataColumnSize.S,
                col=1,
            ),
        ]


    @classmethod
    def get_data_cells(
        cls,
        game: GameRawg,
        on_open_panel: Callable[[GameRawg], None],
    ) -> list[ft.DataCell]:
        """Genere les cellules pour chaque colonne et ligne"""
        cells = []

        for attr in cls.COLUMNS.keys():

            raw = getattr(game, attr, None)

            if attr in ("platforms", "genres", "tags"):
                value = ", ".join(raw) if raw else ""
            else:
                value = raw if raw is not None else ""

            cells.append(
                ft.DataCell(
                    content=ft.Container(
                        content=ft.Text(
                            value=str(value),
                            tooltip=str(value),
                        ),
                        alignment=cls.COLUMNS.get(attr)[2],
                        # border=ft.Border(
                        #    right=ft.BorderSide(
                        #        width=0.5,
                        #       color=ft.Colors.OUTLINE_VARIANT,
                        #   )
                        # ),
                        expand=True,
                    )
                )
            )

        # cellule Actions
        cells.append(
            ft.DataCell(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.REMOVE_RED_EYE,
                            tooltip="Voir les détails",
                            on_click=lambda e, g=game: on_open_panel(g),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            tooltip="Ajouter à la base de données",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
        )

        return cells


    @classmethod
    def get_data_rows(
        cls,
        games,
        selected_game,
        on_select,
        on_open_panel,
    ) -> list[fdt.DataRow2]:
        """Genere les lignes pour chaque colonnes et appelle la generation des cellules"""
        rows = []

        for i, g in enumerate(games):

            base_color = (
                ft.Colors.SURFACE_CONTAINER_LOW if i % 2 == 0 else ft.Colors.SURFACE
            )

            rows.append(
                fdt.DataRow2(
                    specific_row_height=50,
                    selected=(g is selected_game),
                    color={
                        ft.ControlState.DEFAULT: base_color,
                        ft.ControlState.SELECTED: ft.Colors.ON_PRIMARY,
                    },
                    on_tap=lambda _, g=g: on_select(g),
                    cells=cls.get_data_cells(
                        g,
                        on_open_panel,
                    ),
                )
            )

        return rows


    @staticmethod
    def get_search_table() -> fdt.DataTable2:
        """Retourne le composant de tableau de jeux trouvés."""
        return fdt.DataTable2(
            expand=True,
            show_checkbox_column=False,
            column_spacing=0,
            heading_row_color=ft.Colors.SECONDARY_CONTAINER,
            horizontal_margin=12,
            bottom_margin=10,
            min_width=600,
            empty=ft.Container(
                content=ft.Text(
                    "Effectuez une recherche de jeux",
                    theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                ),
                alignment=ft.Alignment.CENTER,
            ),
        )

    #### BAR SEARCH
    @staticmethod
    def get_search_bar(
        query: str,
        platforms: dict,
        text_platforms:ft.Text,
        on_query_change: Callable[[str], None],
        on_search: Callable[[], object],
        on_toggle_platform,
    ):

        search_button = ft.FilledButton(
            None,
            icon=ft.Icons.SEARCH,
        )

        menu_items = []
        for plt, ids in platforms.items():
            print(plt)
            print(ids)
            checkbox = ft.Checkbox(
                label=plt,
                value=False,
                on_change=lambda e, p=plt: on_toggle_platform(p, e.control.value),
                expand=True,

            )

            menu_items.append(
                ft.PopupMenuItem(
                    content=checkbox
                )
            )
        
        
        text_platforms.color=ft.Colors.BLUE_GREY_200
        text_platforms.size=16
        text_platforms.margin=ft.Margin.only(left=9)

        combo = ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.VIDEOGAME_ASSET_ROUNDED,
                            color=ft.Colors.BLUE_GREY_200,
                        ),
                        text_platforms,
                    ],
                    spacing=5,
                ),
                padding=11,
                border=ft.Border.all(1, ft.Colors.OUTLINE),
                border_radius=5,
                expand=True,
                width=450,
            ),
            items=menu_items,
            width=500,
        )

        progress = ft.ProgressRing(
            width=18,
            height=18,
            stroke_width=2,
            visible=False,
        )

        async def handle_input_submit(e: ft.ControlEvent):
            await on_search()

        async def handle_button_click(e: ft.ControlEvent):
            await on_search()

        search_button.on_click = handle_button_click

        bar = ft.Row(
            controls=[
                ft.TextField(
                    value=query,
                    hint_text="Nom du jeu …",
                    on_change=lambda e: on_query_change(e.control.value or ""),
                    on_submit=handle_input_submit,
                    prefix_icon=ft.Icons.ABC_ROUNDED,  # ft.Icons.GAMEPAD_ROUNDED,
                ),
                combo,
                #menu_content,
                search_button,
                progress,
            ],
            spacing=10,
        )

        return bar, search_button, progress

    ### ASSEMBLE
    @staticmethod
    def build_search_page(
        tables: ft.Control,
        search_bar: ft.Control,
    ) -> ft.View:
        """Assemble la vue complète à partir de composants déjà construits."""
        return ft.View(
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        controls=[
                            search_bar,
                            tables,
                        ],
                        spacing=10,
                    ),
                )
            ],
        )
