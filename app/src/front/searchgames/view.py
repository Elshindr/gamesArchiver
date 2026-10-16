import flet as ft
from typing import Callable, List
import flet_datatable2 as fdt
from models.games import GameRawg
from front.detailpanel import ViewSidePanelDetailGame

class ViewSearch:
    COLUMNS = {
            "Name": "name",
            "Released": "released",
            "Platforms": "platforms",
            "Genres": "genres",
            "Publisher": "publisher",
            "Developer": "developer",
            "Tags": "tags",
            "Playtime (h)": "playtime",
        }


    @classmethod
    def get_data_columns(
        cls,
        on_sort: Callable[[ft.DataColumnSortEvent], None],
    ) -> list[fdt.DataColumn2]:
        """Génère les colonnes dans l'ordre exact de COLUMNS."""

        labels = list(cls.COLUMNS)

        return [
            *[
                fdt.DataColumn2(
                    label=ft.Text(label),
                    on_sort=on_sort,
                    heading_row_alignment=ft.MainAxisAlignment.START,
                )
                for label in labels
            ],

            # Colonne Actions
            fdt.DataColumn2(
                label=ft.Text("Actions"),
                size=fdt.DataColumnSize.L,
            ),
        ]



    @classmethod
    def get_data_cells(
        cls,
        game: GameRawg,
        on_open_panel: Callable[[GameRawg], None],
    ) -> list[ft.DataCell]:

        cells = []

        for attr in cls.COLUMNS.values():

            raw = getattr(game, attr, None)

            if attr in ("platforms", "genres", "tags"):
                value = ", ".join(raw) if raw else ""
            else:
                value = raw if raw is not None else ""

            cells.append(
                ft.DataCell(
                    content=ft.Text(str(value))
                )
            )

        # UNE SEULE cellule Actions
        cells.append(
            ft.DataCell(
                content=ft.IconButton(
                    icon=ft.Icons.REMOVE_RED_EYE,
                    tooltip="Voir les détails",
                    on_click=lambda e, g=game: on_open_panel(g),
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

        rows = []

        for i, g in enumerate(games):

            base_color = (
                ft.Colors.SURFACE_CONTAINER_LOW
                if i % 2 == 0
                else ft.Colors.SURFACE
            )

            rows.append(
                fdt.DataRow2(
                    specific_row_height=50,

                    selected=(g is selected_game),

                    color={
                        ft.ControlState.DEFAULT: base_color,
                        ft.ControlState.SELECTED: ft.Colors.TEAL,
                        ft.ControlState.PRESSED: ft.Colors.SECONDARY_CONTAINER,
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
                content=ft.Text("Effectuez une recherche de jeux", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                alignment=ft.Alignment.CENTER,
            ),
        )


    @staticmethod
    def get_search_bar(
        query: str,
        on_query_change: Callable[[str], None],
        on_search: Callable[[], object],
    ):
        search_button = ft.FilledButton(
            "Rechercher",
            icon=ft.Icons.SEARCH,
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
                ft.Text("Recherche :", size=16),
                ft.TextField(
                    value=query,
                    hint_text="Nom du jeu …",
                    expand=True,
                    on_change=lambda e: on_query_change(e.control.value or ""),
                    on_submit=handle_input_submit,
                    prefix_icon=ft.Icons.SEARCH,
                ),
                search_button,
                progress,
            ],
            spacing=10,
        )

        return bar, search_button, progress



    @staticmethod
    def build_search_page(
        content: ft.Control,
        search_bar: ft.Control,
    ) -> ft.View:

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
                            content,
                        ],
                        spacing=10,
                    ),
                )
            ],
        )
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