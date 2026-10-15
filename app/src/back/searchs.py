import os
from dotenv import load_dotenv
import requests
from models.games import GameRawg

load_dotenv()


class RAWGAPI:
    def __init__(self):
        self.api_key = os.getenv("RAWG_API_KEY")
        self.base_url = "https://api.rawg.io/api"

    def search_raw_get(self, query, page=1):
        """Lance la requête GET vers l'API RAWG pour rechercher des jeux avec la query donnée et la page spécifiée."""
        url = f"{self.base_url}/games"
        print(f"RAWGAPI: search_raw_get: {url} with query='{query}' and page={page}")
        params = {
            "key": self.api_key,
            "search": query,
            "page": page
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def search_transform(self, data):
        """Transforme les données brutes de l'API RAWG en une liste d'objets GameRawg."""
        results = data.get("results", [])
        transformed_data = []
        for game in results:
            transformed_data.append(GameRawg(
                id=game.get("id"),
                name=game.get("name"),
                released=game.get("released"),
                rating=game.get("rating"),
                platforms=[platform["platform"]["name"] for platform in game.get("platforms", [])],
                genres=[genre["name"] for genre in game.get("genres", [])],
            ))
        return transformed_data

    def search_games(self, query, page=1):
        """Recherche des jeux sur l'API RAWG et retourne une liste d'objets GameRawg."""
        raw_data = self.search_raw_get(query, page)
        return self.search_transform(raw_data)