import flet as ft
#from models.games import GameRawg
from database.orm import Game, Platform

from .services import GameRawgService
from .searchview import ViewSearch
from .detailpanelview import ViewSidePanelDetailGame
import asyncio
from collections.abc import Awaitable, Callable
from back.ingestion import Ingestion
from database.orm import Platform
from typing import List
from sqlalchemy import Engine
import flet_datatable2 as fdt
from back.apihltb import get_howlongtobeat


class SearchController:

    def __init__(
        self,
        main,
        page: ft.Page,
        engine: Engine,
        lstplatforms: List[Platform],
        on_game_added: Callable[[], Awaitable[None]] | None = None,
    ):
        self.main = main
        self.page = page
        self.engine = engine
        self.on_game_added = on_game_added

        # État
        self.query = ""
        self.selected_game: Game | None = None
        self.selected_platforms: List[Platform] = []

        self.sort_column_index = 0
        self.sort_ascending = True

        # Données
        self.lstplatforms: List[Platform] = lstplatforms

        # Contrôles Flet
        self.search_button: ft.FilledButton | None = None
        self.progress: ft.ProgressRing | None = None
        self.table: fdt.DataTable2 = None

        self.text_platforms = ft.Text("Aucune plateforme sélectionnée")

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

    @property
    def games(self) -> list[Game]:
        return self.main.lstsearchs

    #### INIT TAB SEARCH

    def set_page(self):

        search_bar, self.search_button, self.progress = ViewSearch.get_search_bar(
            self.query,
            self.lstplatforms,
            self.text_platforms,
            on_query_change=self.handle_query_change,
            on_search=self.handle_search,
            on_toggle_platform=self.toggle_platform,
        )

        self.table = ViewSearch.get_search_table(handle_sort=self.handle_sort)

        tables = ft.Stack(
            expand=True,
            controls=[
                self.table,
                self.paneldetail,
            ],
        )

        self.fill()

        return ViewSearch.build_search_page(tables, search_bar)

    #### DROPDOWN PLATFORMS
    def update_text_platforms(self):
        """Met à jour le texte des platformes selectionnées"""

        if self.selected_platforms:
            self.text_platforms.value = ", ".join(
                sorted([plt.name for plt in self.selected_platforms])
            )
        else:
            self.text_platforms.value = "Aucune plateforme sélectionnée"
        self.page.update()

    def toggle_platform(self, platform: Platform, checked: bool):
        """Event lors du cochage/decochage d'une checkbox du dropdown des platformes"""

        if checked:
            self.selected_platforms.append(platform)
        else:
            self.selected_platforms.remove(platform)

        self.update_text_platforms()

    # PANEL DETAIL GAME
    def close_game_panel(self, e: ft.ControlEvent):
        self.paneldetail.right = -400
        self.page.update()

    async def open_game_panel(self, game: Game):
        self.paneldetail.content = ft.Column(
            [
                ft.Text(game.name, size=24, weight=ft.FontWeight.BOLD),
                ft.ProgressRing(),
                ft.Text("Recherche …"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.paneldetail.right = 0
        self.page.update()

        if game.playtimeHltb is None and game.imageUrl is None:
            try:
                playtime, img = await asyncio.to_thread(
                    get_howlongtobeat, game.idHltb, game.name
                )
                game.playtimeHltb = playtime
                if img:
                    game.imageUrl = img
            except Exception as exc:
                # TODO:À remplacer idéalement par un message visible dans le panneau.
                print(f"Erreur pendant la recherche HowLongToBeat : {exc}")

        self.paneldetail.content = ViewSidePanelDetailGame.get_paneldetail(
            game=game,
            fermer_panel=self.close_game_panel,
            on_add_game=self.on_add_game,
        )
        self.page.update()

    # RECHERCHE BAR GAMES RAWG
    def handle_query_change(self, new_query: str):
        self.query = new_query

    async def handle_search(self, e=None):

        if self.search_button.disabled:  # bloque les nouvelles recherches
            return

        query = self.query.strip()  # nettoie la chaine

        if not query:
            self.main.lstsearchs = []
            self.refresh()
            return

        # Gestion de l'affichage des boutons
        self.search_button.disabled = True
        self.progress.visible = True
        self.page.update()

        plt_ids = [
            plt.idRawg for plt in self.selected_platforms
        ]  # IdRawg des platforms selectionnées

        try:
            self.main.lstsearchs = await self.main.get_lstsearchs_rawg(query, plt_ids)
            print("assign ok")
            # self.games = self.games or []

            GameRawgService.sort(
                self.games,
                self.sort_column_index,
                self.sort_ascending,
            )
            print("sort ok")
            self.refresh()
            print("refresh ok")

        except Exception as e:
            print(f"Erreur pendant la recherche RAWG : {e}")

        finally:
            self.search_button.disabled = False
            self.progress.visible = False

            self.page.update()

    # TABLE GAMES_SEARCH EVENTs
    def handle_sort(self, e: ft.DataColumnSortEvent):

        self.sort_column_index = e.column_index
        self.sort_ascending = e.ascending

        GameRawgService.sort(
            self.games,
            self.sort_column_index,
            self.sort_ascending,
        )

        self.refresh()

    def handle_select(self, g: Game):
        self.selected_game = (
            None if self.selected_game is g else g
        )  # re-clic = désélection
        self.refresh()

    ### ACTION BTN
    async def on_add_game(self, game: Game):
        self.main.add_game_tab_search(game)

        if self.on_game_added is not None:
            await self.on_game_added()

        self.page.update()

    ### GENERALS
    def fill(self):

        self.table.rows = ViewSearch.get_data_rows(
            self.games,
            self.selected_game,
            self.handle_select,
            on_open_panel=self.open_game_panel,
            on_add_game=self.on_add_game,
        )

        self.table.sort_column_index = self.sort_column_index
        self.table.sort_ascending = self.sort_ascending

    def refresh(self):
        self.fill()
        self.table.update()
