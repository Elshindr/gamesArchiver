
from models.games import Dessert

class DessertService:
    SORTERS = {
        0: lambda d: d.name.lower(), 1: lambda d: d.calories, 2: lambda d: d.fat,
        3: lambda d: d.carbs,       4: lambda d: d.protein,  5: lambda d: d.sodium,
        6: lambda d: d.calcium,     7: lambda d: d.iron,
    }

    @staticmethod
    def sort(desserts: list[Dessert], column_index: int, ascending: bool) -> list[Dessert]:
        desserts.sort(key=DessertService.SORTERS[column_index], reverse=not ascending)
        return desserts

    @staticmethod
    def toggle(dessert: Dessert) -> None:
        dessert.selected = not dessert.selected

    @staticmethod
    def toggle_all(desserts: list[Dessert], target: bool) -> None:
        for d in desserts:
            d.selected = target
