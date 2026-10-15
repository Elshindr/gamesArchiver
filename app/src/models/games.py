from dataclasses import dataclass



@dataclass
class Dessert:
    name: str
    calories: float
    fat: float
    carbs: float
    protein: float
    sodium: float
    calcium: float
    iron: float
    selected: bool 