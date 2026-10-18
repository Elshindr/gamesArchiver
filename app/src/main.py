import flet as ft
from front.searchgames.searchcontroler import SearchController
from front.main.maincontroler import MainController
from database.createdb import init_db

async def main(page: ft.Page):

    # CHECK/INIT DB
    engine = init_db()

    # INIT TABS
    controlermain = MainController(page)
    await controlermain.set_page()
    




ft.run(main)