from dataclasses import dataclass
from datetime import datetime



@dataclass
class GameRawg:
    id:int
    name: str
    released: datetime
    rating: float
    platforms: list[str]
    genres: list[str]
    #selected: bool 