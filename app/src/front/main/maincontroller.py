import flet as ft
from .mainview import MainView
from front.searchgames.searchcontroller import SearchController
import asyncio
from front.comsgames.commscontroller import CommsController
from database.createdb import init_db


class MainController:
    def __init__(self, page):

        self.page = page

        # CHECK/INIT DB
        self.engine = init_db()


    async def set_page(self):
        # SEARCH
        controllersearch = SearchController(self.page, self.engine)
        await controllersearch.initialize()
        tabsearch = controllersearch.set_page()

        # COMMS
        controllercomms = CommsController(self.page, self.engine)
        tabcomms = controllercomms.set_page()

        mainInterface = MainView.get_main_tabs(tabsearch, tabcomms)

        self.page.controls.clear()
        self.page.add(
            ft.SafeArea(
                expand=True,
                content=mainInterface
            )
        )
        self.page.update()