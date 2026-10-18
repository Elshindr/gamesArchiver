import flet as ft
from front.searchgames.controler import SearchController

from database.createdb import init_db

async def main(page: ft.Page):

    # CHECK DB
    engine = init_db()

    controller = SearchController(page)
    await controller.initialize()
    controller.set_page()


ft.run(main)