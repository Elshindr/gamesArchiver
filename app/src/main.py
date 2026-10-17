import flet as ft
from front.searchgames.controler import SearchController



async def main(page: ft.Page):

    controller = SearchController(page)

    await controller.initialize()
    controller.set_page()


ft.run(main)