import flet as ft


class MainView:

    def get_main_tabs(tabsearch):
        return ft.Tabs(
            length=2,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(
                                label="Recherches", icon=ft.Icons.SAVED_SEARCH_ROUNDED
                            ),
                            ft.Tab(label="Perso", icon=ft.Icons.GAMEPAD_ROUNDED),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            tabsearch,
                            ft.Container(
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text("Settings content"),
                            ),
                        ],
                    ),
                ],
            ),
        )
