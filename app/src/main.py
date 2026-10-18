import flet as ft
from front.main.maincontroller import MainController


async def main(page: ft.Page):


    # INIT TABS
    controllermain = MainController(page)
    await controllermain.set_page()


ft.run(main)