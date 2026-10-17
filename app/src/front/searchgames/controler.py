import flet as ft
from front.detailpanel import ViewSidePanelDetailGame
from models.games import GameRawg
from .services import GameRawgService
from .view import ViewSearch
from back.searchs import RAWGAPI
import asyncio


#def SearchControl(page: ft.Page):
class SearchController:


    def __init__(self, page: ft.Page):
        self.page = page

        # État
        self.query = ""
        self.games: list[GameRawg] = []
        self.selected_game: GameRawg | None = None
        self.selected_platforms_ids: set[str] = set()

        self.sort_column_index = 0
        self.sort_ascending = True

        # Données
        self.platforms: dict= {}

        # Contrôles Flet
        self.search_button: ft.FilledButton | None = None
        self.progress: ft.ProgressRing | None = None
        self.table = None

        self.text_platforms = ft.Text(
            "Aucune plateforme sélectionnée"
        )

        self.paneldetail = ft.Container(
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


    #### INIT PAGE
    async def initialize(self):
        """Initialise les données nécessaires au controller."""

        self.platforms = await asyncio.to_thread(
            RAWGAPI.get_platforms
        )

        #self.platforms = [
        #    platform.get("name")
        #    for platform in platforms
        #]
    
    def set_page(self):

        (search_bar,self.search_button,self.progress) = ViewSearch.get_search_bar(
            self.query,
            self.platforms,
            self.text_platforms,
            on_query_change=self.handle_query_change,
            on_search=self.handle_search,
            on_toggle_platform=self.toggle_platform,
        )

        self.table = ViewSearch.get_search_table()


        tables = ft.Stack(
            expand=True,
            controls=[
                self.table,
                self.paneldetail,
            ],
        )

        self.fill()

        self.page.views.append(
            ViewSearch.build_search_page(
                tables,
                search_bar,
            )
        )

        self.page.update()


    #### DROPDOWN PLATFORMS

    def update_text_platforms(self):
        if self.selected_platforms_ids:
            self.text_platforms.value = ", ".join(sorted(self.selected_platforms_ids))
        else:
            self.text_platforms.value = "Aucune plateforme sélectionnée"
        self.page.update()


    def toggle_platform(self, platform, checked):
            if checked:
                self.selected_platforms_ids.add(platform)
            else:
                self.selected_platforms_ids.discard(platform)

            self.update_text_platforms()



    # PANEL DETAIL GAME
    def close_game_panel(self, e: ft.ControlEvent):
        self.paneldetail.right = -400
        self.page.update()


    def open_game_panel(self, game: GameRawg):

        self.paneldetail.content = ViewSidePanelDetailGame.get_paneldetail(
            game=game,
            fermer_panel=self.close_game_panel,
        )

        self.paneldetail.right = 0

        self.page.update()
   


    # RECHERCHE GAMES RAWG
    def handle_query_change(self,new_query: str):
        self.query = new_query


    async def handle_search(self, e=None):

        if self.search_button.disabled:
            return

        query = self.query.strip()

        if not query:
            self.games = []
            self.refresh()
            return

        self.search_button.disabled = True
        self.progress.visible = True

        self.page.update()

        plt_ids = [self.platforms.get(name) for name in self.selected_platforms_ids]
        print(plt_ids)
        try:
            self.games = await asyncio.to_thread(
                RAWGAPI().search_games,
                query,
                plt_ids
            )

            self.games = self.games or []

            GameRawgService.sort(
                self.games,
                self.sort_column_index,
                self.sort_ascending,
            )

            self.refresh()

        except Exception as exc:
            print(f"Erreur pendant la recherche RAWG : {exc}")

        finally:
            self.search_button.disabled = False
            self.search_button.text = "Rechercher"
            self.progress.visible = False

            self.page.update()


    def handle_sort(self, e: ft.DataColumnSortEvent):

        self.sort_column_index = e.column_index
        self.sort_ascending = e.ascending

        GameRawgService.sort(
            self.games,
            self.sort_column_index,
            self.sort_ascending,
        )

        self.refresh()


    def handle_select(self, g: GameRawg):
        self.selected_game = None if self.selected_game is g else g  # re-clic = désélection
        self.refresh()


    ### GENERALS
    def fill(self):

        self.table.columns = ViewSearch.get_data_columns(
            on_sort=self.handle_sort,
        )

        self.table.rows = ViewSearch.get_data_rows(
            self.games,
            self.selected_game,
            self.handle_select,
            on_open_panel=self.open_game_panel,
        )

        self.table.sort_column_index = self.sort_column_index
        self.table.sort_ascending = self.sort_ascending


    def refresh(self):
        self.fill()
        self.table.update()
    
    
