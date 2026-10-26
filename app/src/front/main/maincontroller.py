import flet as ft
from .mainview import MainView
from front.searchgames.searchcontroller import SearchController
import asyncio
from front.comsgames.commscontroller import CommsController
from database.createdb import init_db
from back.ingestion import Ingestion
from database.orm import Commentary, Platform, Game
from typing import List
from models.games import GameRawg
from back.apirawg import RAWGAPI
from sqlalchemy import Engine
from back.apiwikidata import WikidataAPI

class MainController:
    def __init__(self, page: ft.Page):

        self.page = page
        self.lstsearchs: List[Game] = []
        self.lstcoms: List[Commentary] = []
        self.lstplatforms: List[Platform] = []

        # CHECK/INIT DB
        self.engine: Engine = init_db()

    async def initialize(self) -> None:
        await self.get_lstplatforms_db()
        await self.get_lstcoms_all_db()

    async def get_lstcoms_all_db(self) -> None:
        self.lstcoms = await asyncio.to_thread(Ingestion.get_coms_db, self.engine)

    async def get_lstplatforms_db(self) -> None:
        self.lstplatforms = await asyncio.to_thread(
            Ingestion.create_platforms_db, self.engine
        )

    async def get_lstsearchs_rawg(self, query, lstplatforms_ids) -> List[Game]:
        #self.lstsearchs = await RAWGAPI.create_games_rawg(query, lstplatforms_ids)
        self.lstsearchs = await WikidataAPI.search_jeu(query)
        return self.lstsearchs

    async def add_game_tab_search(self, game: GameRawg):
        game = await asyncio.to_thread(
            Ingestion.insert_game_rawg,
            game,
            self.lstplatforms,
            self.engine,
        )

    def set_page(self) -> None:

        controllercomms = CommsController(self, self.page, self.engine, self.lstcoms)
        controllersearch = SearchController(
            self,
            self.page,
            self.engine,
            self.lstplatforms,
            on_game_added=controllercomms.refresh,
        )

        tabsearch = controllersearch.set_page()
        tabcomms = controllercomms.set_page()

        mainInterface = MainView.get_main_tabs(tabsearch, tabcomms)

        self.page.controls.clear()
        self.page.add(ft.SafeArea(expand=True, content=mainInterface))
        self.page.update()
