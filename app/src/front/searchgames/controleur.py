import flet as ft
from models.games import GameRawg
from .services import GameRawgService
from .view import ViewSearch
from back.searchs import RAWGAPI
import asyncio


def SearchControl(page: ft.Page):
    
    #### BAR RECHERCHE
    query = ""
    games: list[GameRawg] = []
    page_cur = 1

    def handle_query_change(new_query: str):
        nonlocal query
        print("handle_query_change: new_query=", new_query)
        query = new_query

    async def handle_search(e=None):
        nonlocal query, games, page_cur
        print(f"Recherche de jeux pour: {query}")
        games  = await asyncio.to_thread(RAWGAPI().search_games, query) 
        refresh()

    search_bar = ViewSearch.get_search_bar(query, on_query_change=handle_query_change, on_search=handle_search)



    #### TABLE
    sort_column_index, sort_ascending = 0, True
    selected_game: GameRawg | None = None  
    
    table = ViewSearch.get_search_table()
    
    def handle_sort(e: ft.DataColumnSortEvent):
        nonlocal sort_column_index, sort_ascending
        sort_column_index, sort_ascending = e.column_index, e.ascending
        GameRawgService.sort(games, e.column_index, e.ascending)
        refresh()


    def handle_select(g: GameRawg):
        nonlocal selected_game
        selected_game = None if selected_game is g else g   # re-clic = désélection
        refresh()


    def fill():
        # premier rendu, pas d'update
        nonlocal games
        table.columns = ViewSearch.get_data_columns(on_sort=handle_sort)
        table.rows = ViewSearch.get_data_rows(games, selected_game, handle_select)
        table.sort_column_index = sort_column_index
        table.sort_ascending = sort_ascending
        


    def refresh():
        fill()
        table.update()


    # Initial fill
    fill()
    page.views.append(ViewSearch.build_search_page(table, search_bar))
    page.update()
