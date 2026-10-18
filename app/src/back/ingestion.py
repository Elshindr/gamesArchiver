from models.games import GameRawg
from sqlalchemy import Engine
from database.orm import Game, Platform, Commentary
from sqlalchemy.orm import sessionmaker
from datetime import date


class Ingestion:

    @staticmethod
    def insert_game_rawg(g: GameRawg, platforms, engine: Engine):
        coms, game, lstplatforms = Ingestion.insert_transform_game(g, platforms)
        Ingestion.insert_many([game], engine)
        Ingestion.insert_many([coms], engine)
        Ingestion.insert_many(lstplatforms, engine)

        return True

    @staticmethod
    def insert_many(lstobj, engine):

        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add_all(lstobj)
            session.commit()
            print(f"Insertions réussie :  ligne insérées.")
        except Exception as e:
            session.rollback()
            print(f"Erreur lors de l'insertion  : {e}")
        finally:
            session.close()

    @staticmethod
    def insert_transform_game(
        gr: GameRawg, lstPlatforms: dict
    ):  # -> tuple(Commentary, Game, Platform) :

        lstplatforms = list[Platform]()
        for plt in gr.platforms:
            plt_r = Platform(idRawg=lstPlatforms.get(plt), name=plt)
            lstplatforms.append(plt_r)

            # print(plt_r)

        release = None
        if gr.released:
            release = date.fromisoformat(gr.released)
        game = Game(
            idRawg=gr.id,
            name=gr.name,
            imageUrl=gr.background_image,
            playtimeRAWG=gr.playtime,
            release=release,
            platforms=lstplatforms,
        )
        coms = Commentary(game=game)

        return coms, game, lstplatforms
