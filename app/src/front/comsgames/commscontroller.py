from .commsview import CommsView
from database.orm import Game, Commentary, Platform
from typing import List
from back.ingestion import Ingestion
import asyncio
#from main.maincontroller import MainController
import flet as ft


class CommsController:
    def __init__(self,main, page:ft.Page, engine, coms):
        self.main = main
        self.page = page
        self.engine = engine
        self.coms: List[Commentary] = coms
        self.table = None

    """async def get_coms_db(self) -> None:
        self.coms = await asyncio.to_thread(Ingestion.get_coms_db, self.engine)"""

    def set_page(self):
        #await self.get_coms_db()
        self.table = CommsView.get_coms_table(self.coms)
        return CommsView.get_tabs_comms(self.table)

    async def refresh(self):
        #await self.get_coms_db()
        self.table.rows = CommsView.get_data_rows(self.coms)
        self.table.update()