import flet as ft
from front.detailpanel import ViewSidePanelDetailGame
from models.games import GameRawg
from .services import GameRawgService
from .view import ViewSearch
from back.searchs import RAWGAPI
import asyncio


def SearchControl(page: ft.Page):
    
    #### BAR RECHERCHE
    query = ""
    games: list[GameRawg] = []
    paneldetail = ft.Container(
        width=400,
        right=-400,
        top=0,
        bottom=0,
        padding=20,
        shadow=ft.BoxShadow(
            blur_radius=20,
            spread_radius=2,
            color=ft.Colors.BLACK_12,
        ),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,

        animate_position=ft.Animation(
            300,
            ft.AnimationCurve.EASE_OUT,
        ),
    )

    def close_game_panel(e: ft.ControlEvent):
        paneldetail.right = -400
        page.update()

    def open_game_panel(game: GameRawg):

        paneldetail.content = (
            ViewSidePanelDetailGame.get_paneldetail(
                game=game,
                fermer_panel=close_game_panel,
            )
        )

        paneldetail.right = 0

        page.update()
    
    def handle_query_change(new_query: str):
        nonlocal query
        print("handle_query_change: new_query=", new_query)
        query = new_query

    async def handle_search(e=None):
        nonlocal query, games

        if search_button.disabled:
            return

        query = query.strip()

        if not query:
            games = []
            refresh()
            return

        search_button.disabled = True
        search_button.text = "Recherche..."
        progress.visible = True
        page.update()

        try:
            games = await asyncio.to_thread(
                RAWGAPI().search_games,
                query,
            )

            games = games or []

            GameRawgService.sort(
                games,
                sort_column_index,
                sort_ascending,
            )

            refresh()

        except Exception as exc:
            print(f"Erreur pendant la recherche RAWG : {exc}")

        finally:
            search_button.disabled = False
            search_button.text = "Rechercher"
            progress.visible = False
            page.update()

    search_bar, search_button, progress = ViewSearch.get_search_bar(
            query,
            on_query_change=handle_query_change,
            on_search=handle_search,
    )


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

        table.columns = ViewSearch.get_data_columns(
            on_sort=handle_sort,
        )

        table.rows = ViewSearch.get_data_rows(
            games,
            selected_game,
            handle_select,
            on_open_panel=open_game_panel,
        )

        table.sort_column_index = sort_column_index
        table.sort_ascending = sort_ascending

        

    def refresh():
        fill()
        table.update()

    content = ft.Stack(
        expand=True,
        controls=[
            table,
            paneldetail,
        ],
    )
    # Initial fill
    fill()
    page.views.append(
        ViewSearch.build_search_page(
            content,
            search_bar,
        )
    )

    page.update()
