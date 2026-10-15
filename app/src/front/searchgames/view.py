import flet as ft
from typing import Callable, List
import flet_datatable2 as fdt
from models.games import GameRawg



class ViewSearch:
    COLUMNS = {
            "Name": "name",
            "Released": "released",
            "Rating": "rating",
            "Platforms": "platforms",
            "Genres": "genres",
        }

    @classmethod
    def get_data_columns(cls, on_sort: Callable[[ft.DataColumnSortEvent], None]) -> list[fdt.DataColumn2]:
        """Génère les colonnes dans l'ordre exact de COLUMNS, avec gestion du tri."""
        labels = list(cls.COLUMNS)
        return [
            fdt.DataColumn2(
                label=ft.Text(labels[0]),
                size=fdt.DataColumnSize.L,
                on_sort=on_sort,
                heading_row_alignment=ft.MainAxisAlignment.START,
            ),
            *[fdt.DataColumn2(label=ft.Text(c), on_sort=on_sort) for c in labels[1:]],
        ]

    @classmethod
    def get_data_cells(cls, game: GameRawg) -> list[ft.DataCell]:
        """Génère les cellules dans l'ordre exact de COLUMNS, avec gestion des None."""
        cells = []
        for attr in cls.COLUMNS.values():
            raw = getattr(game, attr, None)
            if attr in ("platforms", "genres"):
                value = ", ".join(raw) if raw else ""
            else:
                value = raw
            cells.append(ft.DataCell(content=ft.Text(value)))
        return cells

    @classmethod
    def get_data_rows(cls, games, selected_game, on_select) -> list[fdt.DataRow2]:
        """Retourne les lignes de données pour le tableau de jeux."""
        return [
            fdt.DataRow2(
                specific_row_height=50,
                selected=(g is selected_game),
                on_tap=lambda _, g=g: on_select(g),
                cells=cls.get_data_cells(g),   # même ordre que get_data_columns
            )
            for g in games
        ]

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
                content=ft.Text("Effectuez une recherche de jeux", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                alignment=ft.Alignment.CENTER,
            ),
        )

    @staticmethod
    def get_search_bar(
        query: str,
        on_query_change: Callable[[str], None],
        on_search: Callable[[], object],
    ) -> ft.Control:

        def handle_input_change(e: ft.ControlEvent):
            on_query_change(e.control.value or "")

        async def handle_input_submit(e: ft.ControlEvent):
            await on_search()

        async def handle_button_click(e: ft.ControlEvent):
            await on_search()

        return ft.Row(
            controls=[
                ft.Text("Recherche :", size=16),
                ft.TextField(
                    value=query,
                    hint_text="Nom du jeu …",
                    expand=True,
                    on_change=handle_input_change,
                    on_submit=handle_input_submit,
                    prefix_icon=ft.Icons.SEARCH,
                ),
                ft.FilledButton(
                    "Rechercher",
                    icon=ft.Icons.SEARCH,
                    on_click=handle_button_click,
                ),
            ],
            spacing=10,
        )

    @staticmethod
    def build_search_page(table: fdt.DataTable2, search_bar: ft.Control) -> ft.View:
        """Assemble la vue complète à partir de composants déjà construits."""
        return ft.View(
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        controls=[search_bar, table],
                        spacing=10,
                    ),
                )
            ],
        )