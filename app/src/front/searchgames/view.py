import flet as ft, DataColumnSortEvent
import flet_datatable2 as fdt
from models.games import Dessert
from .services import DessertService


def get_data_columns(on_sort:DataColumnSortEvent) -> list[fdt.DataColumn2]:

    return [
        fdt.DataColumn2(
            label=ft.Text("Name"),
            size=fdt.DataColumnSize.L,
            on_sort=on_sort,
            heading_row_alignment=ft.MainAxisAlignment.START,
        ),
        *[
            fdt.DataColumn2(label=ft.Text(l), on_sort=on_sort, numeric=True)
            for l in [
                "Calories",
                "Fat",
                "Carbs",
                "Protein",
                "Sodium",
                "Calcium",
                "Iron",
            ]
        ],
    ]


def get_data_rows(desserts: list[Dessert], selected_dessert: Dessert | None, on_select) -> list[fdt.DataRow2]:
    return [
        fdt.DataRow2(
            specific_row_height=50,
            selected=(d is selected_dessert),
            on_tap=lambda _, d=d: on_select(d),
            cells=[ft.DataCell(content=ft.Text(v)) for v in
                   (d.name, d.calories, d.fat, d.carbs, d.protein, d.sodium, d.calcium, d.iron)],
        )
        for d in desserts
    ]

def SearchPage(page: ft.Page):

    sort_column_index, sort_ascending = 0, True
    selected_dessert: Dessert | None = None  
    desserts = [
        Dessert("Frozen Yogurt", 159, 6.0, 24, 4.0, 87, 14, 1, True),
        Dessert("Ice Cream Sandwich", 237, 9.0, 37, 4.3, 129, 8, 1, True),
        Dessert("Eclair", 262, 16.0, 24, 6.0, 337, 6, 7, True),
        Dessert("Cupcake", 305, 3.7, 67, 4.3, 413, 3, 8, True),
        Dessert("Gingerbread", 356, 16.0, 49, 3.9, 327, 7, 16, True),
        Dessert("Jelly Bean", 375, 0.0, 94, 0.0, 50, 0, 0, True),
        Dessert("Lollipop", 392, 0.2, 98, 0.0, 38, 0, 2, True),
        Dessert("Honeycomb", 408, 3.2, 87, 6.5, 562, 0, 45, True),
        Dessert("Donut", 452, 25.0, 51, 4.9, 326, 2, 22, True),
        Dessert("Apple Pie", 518, 26.0, 65, 7.0, 54, 12, 6, True),
        Dessert("Frozen Yougurt with sugar", 168, 6.0, 26, 4.0, 87, 14, 1, True),
        Dessert("Ice Cream Sandwich with sugar", 246, 9.0, 39, 4.3, 129, 8, 1, True),
        Dessert("Eclair with sugar", 271, 16.0, 26, 6.0, 337, 6, 7, True),
        Dessert("Cupcake with sugar", 314, 3.7, 69, 4.3, 413, 3, 8, True),
        Dessert("Gingerbread with sugar", 345, 16.0, 51, 3.9, 327, 7, 16, True),
        Dessert("Jelly Bean with sugar", 364, 0.0, 96, 0.0, 50, 0, 0, True),
        Dessert("Lollipop with sugar", 401, 0.2, 100, 0.0, 38, 0, 2, True),
        Dessert("Honeycomb with sugar", 417, 3.2, 89, 6.5, 562, 0, 45, True),
        Dessert("Donut with sugar", 461, 25.0, 53, 4.9, 326, 2, 22, True),
        Dessert("Apple pie with sugar", 527, 26.0, 67, 7.0, 54, 12, 6, True),
        Dessert("Frozen yougurt with honey", 223, 6.0, 36, 4.0, 87, 14, 1, True),
        Dessert("Ice Cream Sandwich with honey", 301, 9.0, 49, 4.3, 129, 8, 1, False),
        Dessert("Eclair with honey", 326, 16.0, 36, 6.0, 337, 6, 7, False),
        Dessert("Cupcake with honey", 369, 3.7, 79, 4.3, 413, 3, 8, False),
        Dessert("Gingerbread with honey", 420, 16.0, 61, 3.9, 327, 7, 16, False),
        Dessert("Jelly Bean with honey", 439, 0.0, 106, 0.0, 50, 0, 0, False),
        Dessert("Lollipop with honey", 456, 0.2, 110, 0.0, 38, 0, 2, False),
        Dessert("Honeycomb with honey", 472, 3.2, 99, 6.5, 562, 0, 45, False),
        Dessert("Donut with honey", 516, 25.0, 63, 4.9, 326, 2, 22, False),
        Dessert("Apple pie with honey", 582, 26.0, 77, 7.0, 54, 12, 6, False),
    ]
    table = fdt.DataTable2(
        expand=True,
        show_checkbox_column=False,
        column_spacing=0,
        heading_row_color=ft.Colors.SECONDARY_CONTAINER,
        horizontal_margin=12,
        bottom_margin=10,
        min_width=600,
    )

    def handle_sort(e: ft.DataColumnSortEvent):
        nonlocal sort_column_index, sort_ascending
        sort_column_index, sort_ascending = e.column_index, e.ascending
        DessertService.sort(desserts, e.column_index, e.ascending)
        refresh()

    def handle_select(d: Dessert):
        nonlocal selected_dessert
        selected_dessert = None if selected_dessert is d else d   # re-clic = désélection
        refresh()

    def fill():
        # premier rendu, pas d'update
        table.columns = get_data_columns(on_sort=handle_sort)
        table.rows = get_data_rows(desserts, selected_dessert, handle_select)
        table.sort_column_index = sort_column_index
        table.sort_ascending = sort_ascending
        table.empty = ft.Container(
            content=ft.Text("Effectuez une recherche de jeux", style=ft.TextThemeStyle.TITLE_MEDIUM),
            alignment=ft.Alignment.CENTER,
        )

    def refresh():
        fill()
        table.update()


    # Initial fill
    fill()
    page.views.append(ft.View(controls=[ft.SafeArea(expand=True, content=table)]))
    page.update()
