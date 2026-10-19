import flet as ft
import flet_datatable2 as fdt
from typing import Callable, List
from database.orm import Game, Commentary, Platform
from front.searchgames.services import GameRawgService

class CommsView:

    #### TABLE
    COLUMNS = {
        "name": ["Name", fdt.DataColumnSize.L, ft.Alignment.CENTER_LEFT],
        #"release": ["Released", fdt.DataColumnSize.S, ft.Alignment.CENTER],
        "platforms": ["Platforms", fdt.DataColumnSize.L, ft.Alignment.CENTER_LEFT],
        #"genres": ["Genres", fdt.DataColumnSize.L, ft.Alignment.CENTER_LEFT],
        #"tags": ["Tags", fdt.DataColumnSize.L, ft.Alignment.CENTER_LEFT],
        #"playtime": ["Playtime (h)", fdt.DataColumnSize.S, ft.Alignment.CENTER],
        "commentaire" : ["Commentaire", fdt.DataColumnSize.L, ft.Alignment.CENTER_LEFT],
        "note" : ["Note", fdt.DataColumnSize.S, ft.Alignment.CENTER],
        "status": ["Status", fdt.DataColumnSize.S, ft.Alignment.CENTER],
    }

    def handle_sort(self, e: ft.DataColumnSortEvent):

        self.sort_column_index = e.column_index
        self.sort_ascending = e.ascending

        GameRawgService.sort(
            self.games,
            self.sort_column_index,
            self.sort_ascending,
        )

        self.refresh()


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
        comms: Commentary,
        #on_open_panel: Callable[[Commentary], None],
        #on_add_game: Callable[[Commentary], None],
    ) -> list[ft.DataCell]:
        """Genere les cellules pour chaque colonne et ligne"""
        cells = []
        print()
        for attr in cls.COLUMNS.keys():

            raw = getattr(comms, attr, None)

            if attr =="name":
                value = comms.game.name
            elif attr =="platforms":
                raw = [plt.name for plt in comms.game.platforms]
            elif attr == "status":
                value =comms.status.value
            else:
                value = raw if raw is not None else ""

            if attr in ("platforms"):
                value = ", ".join(raw) if raw else ""


            cells.append(
                ft.DataCell(
                    content=ft.Container(
                        content=ft.Text(
                            value=str(value),
                            tooltip=str(value),
                        ),
                        alignment=cls.COLUMNS.get(attr)[2],
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
                            #on_click=lambda e, g=comms: on_open_panel(g),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            tooltip="Retirer de ma bibliotheque",
                            
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
        comms
    ) -> list[fdt.DataRow2]:
        """Genere les lignes pour chaque colonnes et appelle la generation des cellules"""
        rows = []

        for i, g in enumerate(comms):

            base_color = (
                ft.Colors.SURFACE_CONTAINER_LOW if i % 2 == 0 else ft.Colors.SURFACE
            )

            rows.append(
                fdt.DataRow2(
                    specific_row_height=50,
                    #selected=(g is selected_game),
                    color={
                        ft.ControlState.DEFAULT: base_color,
                        ft.ControlState.SELECTED: ft.Colors.ON_PRIMARY,
                    },
                    #on_tap=lambda _, g=g: on_select(g),
                    cells=cls.get_data_cells(
                        g,
                        #on_open_panel,
                        #on_add_game
                    ),
                )
            )

        return rows


    @staticmethod
    def get_coms_table(coms:List[Commentary]) -> fdt.DataTable2:
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
            columns=CommsView.get_data_columns(on_sort=CommsView.handle_sort),
            rows=CommsView.get_data_rows(comms=coms)
        )



    def get_tabs_comms(table: fdt.DataTable2) -> ft.Container:
        return ft.Container(
            content=ft.SafeArea(
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[table],
                    spacing=10,
                ),
            ),
        )
