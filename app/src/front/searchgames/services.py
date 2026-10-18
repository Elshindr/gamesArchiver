
from models.games import GameRawg

class GameRawgService:
    SORTERS = {
        0: lambda g: (
            g.name.casefold() if g.name else None
        ),
        1: lambda g: g.released or None,
        2: lambda g: (
            ", ".join(g.platforms or []).casefold()
            if g.platforms else None
        ),
        3: lambda g: (
            ", ".join(g.genres or []).casefold()
            if g.genres else None
        ),
        4: lambda g: (
            ", ".join(g.tags or []).casefold()
            if g.tags else None
        ),
        5: lambda g: g.playtime if g.playtime is not None else None,
    }

    @staticmethod
    def sort(
        games: list[GameRawg],
        column_index: int,
        ascending: bool,
    ) -> list[GameRawg]:

        key_func = GameRawgService.SORTERS[column_index]

        # Séparation: valeur existe / valeur None
        with_value = [
            game for game in games
            if key_func(game) is not None
        ]

        without_value = [
            game for game in games
            if key_func(game) is None
        ]

        # Trier uniquement les valeurs comparables
        with_value.sort(
            key=key_func,
            reverse=not ascending,
        )

        if ascending:
            games[:] = with_value + without_value
        else:
            games[:] = without_value + with_value

        return games

    """@staticmethod
    def toggle(game: GameRawg) -> None:
        game.selected = not game.selected

    @staticmethod
    def toggle_all(games: list[GameRawg], target: bool) -> None:
        for d in games:
            d.selected = target"""
