from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class PlatformRawg:
    idRawg:int|None
    idWiki:str|None
    name:str
    dtrelease: date|None

@dataclass
class GameRawg:
    id:int
    name: str
    released: date|None
    platforms: list[PlatformRawg]
    genres: list[str]
    slug: str
    background_image: str|None
    #publisher: str
    #developer: str
    tags: list[str]
    playtime: int|None

    # other wiki
    idwiki:str
    idhltb:int|None
    idrawg:int
    inBase: bool = False

    #composers:str
    #developers:str
    #publishers:str