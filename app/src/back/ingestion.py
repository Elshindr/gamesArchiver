from models.games import GameRawg
from sqlalchemy import Engine
from database.orm import Game, Platform, Commentary
from sqlalchemy.orm import sessionmaker, Session
from datetime import date
from typing import Tuple, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

class Ingestion:

    @staticmethod
    def insert_game_rawg(g: GameRawg, platforms, engine: Engine):
        coms, game, lstplatforms = Ingestion.insert_transform_game(g, platforms)
        lstplatforms = Ingestion.filter_platforms(lstplatforms, engine)

        game.platforms = lstplatforms
        #Ingestion.insert_many(lstplatforms, engine)
        Ingestion.insert_many([game], engine)
        Ingestion.insert_many([coms], engine)

        return True


    @staticmethod
    def filter_platforms(lstplatformscurr:List[Platform], engine:Engine):
        
        #lstplatformsdb = {plt.name for plt in } 
        
        #return [plt for plt in lstplatformscurr if plt.name not in lstplatformsdb]
        existing = {
            p.name: p for p in Ingestion.get_platforms_db(engine)
        }

        final_platforms = []
        for plt in lstplatformscurr:
            if plt.name in existing:
                final_platforms.append(existing[plt.name])   # objet déjà en base
            else:
                final_platforms.append(plt) 

        return final_platforms

    
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
    ) -> Tuple[Commentary, Game, Platform]:

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


    @staticmethod
    def get_coms_db(engine) -> list[Commentary]:
        with Session(engine) as session:
            stmt = (
                select(Commentary)
                .options(selectinload(Commentary.game).selectinload(Game.platforms))   # charge les relations en avance
            )
            return list(session.scalars(stmt))


    @staticmethod
    def get_platforms_db(engine) -> list[Platform]:
        with Session(engine) as session:
            stmt = (select(Platform))
            return list(session.scalars(stmt))