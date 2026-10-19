
from sqlalchemy import create_engine,Engine
from pathlib import Path
import os
from .orm import Base

def init_db()-> Engine:
    storage_dir = os.getenv("FLET_APP_STORAGE_DATA")

    if not storage_dir:
        raise RuntimeError(
            "FLET_APP_STORAGE_DATA n'est pas défini. "
            "Lance l'application via Flet."
        )

    db_path = Path(storage_dir) / "dev_games.db"

    engine = create_engine(
        f"sqlite:///{db_path.as_posix()}"
    )

    #Base.metadata.drop_all(engine)#TODO: to delete
    Base.metadata.create_all(engine)

    print(f"Base de données : {db_path.resolve()}")

    return engine

