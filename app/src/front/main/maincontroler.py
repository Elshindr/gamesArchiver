import flet as ft
from .mainview import MainView
from front.searchgames.searchcontroler import SearchController
import asyncio

class MainController:
    def __init__(self, page):

        self.page = page

    async def set_page(self):
        controllersearch = SearchController(self.page)
        await controllersearch.initialize()

        tabsearch = controllersearch.set_page()

        mainInterface = MainView.get_main_tabs(tabsearch)

        self.page.controls.clear()
        self.page.add(
            ft.SafeArea(
                expand=True,
                content=mainInterface
            )
        )
        self.page.update()