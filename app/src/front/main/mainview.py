import flet as ft


class MainView:

    def get_main_tabs(tabsearch, tabcoms):
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
                            ft.Tab(label="Mes Jeux", icon=ft.Icons.GAMEPAD_ROUNDED),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            tabsearch,
                            tabcoms,
                        ],
                    ),
                ],
            ),
        )
