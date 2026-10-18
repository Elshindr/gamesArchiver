import os
from dotenv import load_dotenv
import requests
from models.games import GameRawg

load_dotenv()


class RAWGAPI:

    api_key = os.getenv("RAWG_API_KEY")
    base_url = "https://api.rawg.io/api"


    @staticmethod
    def search_raw_get(query, platforms):
        """Lance la requête GET vers l'API RAWG pour rechercher des jeux avec la query donnée et la page spécifiée."""
        url = f"{RAWGAPI.base_url}/games"
        page= 1
        params = {
                "key": RAWGAPI.api_key,
                "search": query,
                "search_precise": True,
                "page_size":1000,
                "search_exact": True,
                "platforms":platforms
        }

        results = []

        while (url is not None) and page <= 50:
            
            print(f"RAWGAPI: search_raw_get: {url} with query='{query}'")
            

            response = requests.get(url, params=params)
            if response.status_code == 200:
                res = response.json()
                games = res.get("results", [])
                results.append(games)

                print(f"RAWGAPI: search_raw_get: {len(games)}, first:{games[0].get('name') if games else 'N/A'} results found for query='{query}' on page {page}")
                if len(games) == 0:
                    print(f"RAWGAPI: search_raw_get: No more results found for query='{query}' on page {page}. Stopping.")
                    url = None  # Stop the loop if no results are found
                    break
                url = res.get("next", None)  # Page suivante si elle existe
                params = {}  # Clear params 

            else:
                response.raise_for_status()
            page += 1
        return [item for sublist in results for item in sublist]  # Flatten the list of lists


    @staticmethod
    def search_transform(data):
        """Transforme les données brutes de l'API RAWG en une liste d'objets GameRawg."""

        print(f"RAWGAPI: search_transform: {len(data)} games found")
        transformed_data = []

        for game in data:
            if not isinstance(game, dict):
                continue

            platforms = [
                item["platform"]["name"]
                for item in (game.get("platforms") or [])
                if isinstance(item, dict)
                and isinstance(item.get("platform"), dict)
                and item["platform"].get("name")
            ]

            genres = [
                item["name"]
                for item in (game.get("genres") or [])
                if isinstance(item, dict) and item.get("name")
            ]


            tags = [
                item["name"]
                for item in (game.get("tags") or [])
                if isinstance(item, dict) and item.get("name") and item.get("language") in ["fra", "fr", "eng"] 
            ]

            transformed_data.append(
                GameRawg(
                    id=game.get("id"),
                    name=game.get("name"),
                    released=game.get("released"),
                    platforms=platforms,
                    genres=genres,
                    slug=game.get("slug"),
                    background_image=game.get("background_image"),
                    #publisher=game.get("publisher"),
                    #developer=game.get("developer"),
                    tags=tags,
                    playtime=game.get("playtime"),
                )
            )


        return transformed_data


    @staticmethod
    def search_games(query, platforms):
        """Recherche des jeux sur l'API RAWG et retourne une liste d'objets GameRawg."""
        if query == "":
            return []
        raw_data = RAWGAPI.search_raw_get(query, platforms)
        if raw_data is None:
            return []
        return RAWGAPI.search_transform(raw_data)


    @staticmethod
    def get_platforms():
        """Lance la requête GET vers l'API RAWG pour rechercher des jeux avec la query donnée et la page spécifiée."""
        url = f"{RAWGAPI.base_url}/platforms"
        page= 1
        params = {
                "key": RAWGAPI.api_key,
                "page_size":1000,
                "order":"name"
        }

        results = []
        while (url is not None) and page <= 50:
            
            print(f"RAWGAPI: search_raw_get: {url}")
            

            response = requests.get(url, params=params)
            if response.status_code == 200:
                res = response.json()
                games = res.get("results", [])
                results.extend(res.get("results", []))
                

                print(f"RAWGAPI: search_raw_get: {len(games)}, first:{games[0].get('name') if games else 'N/A'} ")
                if len(games) == 0:
                    print(f"RAWGAPI: search_raw_get: No more results on page {page}. Stopping.")
                    url = None  # Stop the loop if no results are found
                    break
                url = res.get("next", None)  # Page suivante si elle existe
                params = {}  # Clear params 

            else:
                response.raise_for_status()
            page += 1
        
        setPlatforms = dict()
        for plt in results:
           setPlatforms[plt.get("name")]=plt.get("id")

        return setPlatforms
