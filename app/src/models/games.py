from dataclasses import dataclass
from datetime import datetime

@dataclass
class PlatformRawg:
    idRawg:int
    name:str

@dataclass
class GameRawg:
    id:int
    name: str
    released: datetime
    platforms: list[PlatformRawg]
    genres: list[str]
    slug: str
    background_image: str
    #publisher: str
    #developer: str
    tags: list[str]
    playtime: int
    inBase: bool = False