from dataclasses import dataclass
from datetime import datetime



@dataclass
class GameRawg:
    id:int
    name: str
    released: datetime
    platforms: list[str]
    genres: list[str]
    slug: str
    background_image: str
    #publisher: str
    #developer: str
    tags: list[str]
    playtime: int
    inBase: bool = False