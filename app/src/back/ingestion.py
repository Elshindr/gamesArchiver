from models.games import GameRawg
from sqlalchemy import Engine
from database.orm import Game, Platform, Commentary
from sqlalchemy.orm import sessionmaker, Session
from datetime import date
from typing import Tuple, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from back.apirawg import RAWGAPI



class Ingestion:
    ### GENERAL
    @staticmethod
    def insert_many(lstobj, engine):
        """Insertion en vrac d'une liste d'obj vers la bd"""

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



    ### GAMES DB
    @staticmethod
    def insert_game_rawg(g: GameRawg, allplatforms:List[Platform], engine: Engine)-> bool:
        """Insere en DB les jeux et ses commentaires par defaut associés. Associe les liens entre games et platforms"""
        
        coms, game, lstplatforms = Ingestion.transform_insert_game(g, allplatforms)
        lstplatforms = Ingestion.filter_platforms(lstplatforms, engine)

        game.platforms = lstplatforms
        #Ingestion.insert_many(lstplatforms, engine)
        Ingestion.insert_many([game], engine)
        Ingestion.insert_many([coms], engine)

        return True


    @staticmethod
    def filter_platforms(lstplatformscurr:List[Platform], engine:Engine) -> List[Platform]:
        """Filtre les platformes pour synchroniser en base les platformes existantes et les nouvelles"""
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
    def transform_insert_game(
        gr: GameRawg, lstPlatformsDB: List[Platform]
    ) -> Tuple[Commentary, Game, Platform]:

        lstplatformsfinal = list[Platform]()
        for plt_g in gr.platforms:
            plt_r = Platform(idRawg=plt_g.idRawg, name=plt_g.name)
            lstplatformsfinal.append(plt_r)

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
            platforms=lstplatformsfinal,
        )
        coms = Commentary(game=game)

        return coms, game, lstplatformsfinal


    ### COMMENTARY DB
    @staticmethod
    def get_coms_db(engine) -> list[Commentary]:
        with Session(engine) as session:
            stmt = (
                select(Commentary)
                .options(selectinload(Commentary.game).selectinload(Game.platforms))   # charge les relations en avance
            )
            return list(session.scalars(stmt))



    ### PLATFORMS DB

    @staticmethod
    def get_platforms_db(engine:Engine) -> list[Platform]:
        """Appelle la bd pour recuperer la liste des platforms"""
        with Session(engine) as session:
            stmt = (select(Platform).order_by("name"))
            return list(session.scalars(stmt))
        
    @staticmethod
    def transform_platforms_rawg(data:List) -> List[Platform]:
        """Transforme les données brutes du json des plateformes vers le modele ORM Platform"""

        lstplatforms = [Platform(idRawg=plt.get("id"), name=plt.get("name")) for plt in data ]
        #lstplatforms.sort(key=lambda x: x.name)

        return lstplatforms


    @staticmethod
    def create_platforms_db(engine:Engine)-> list[Platform]:
        """Recupere la liste des platformes. Si vide, on recupere celles de de l'api RAWG qu'on converti avec le schema orm Platform"""
        lstPlatforms = Ingestion.get_platforms_db(engine)

        if lstPlatforms is None or len(lstPlatforms) == 0:
            lstData = RAWGAPI.get_platforms_rawg()

            lstPlatforms = Ingestion.transform_platforms_rawg(lstData)
            Ingestion.insert_many(lstPlatforms, engine)

            # relance le select
            lstPlatforms = Ingestion.get_platforms_db(engine)


        return lstPlatforms

