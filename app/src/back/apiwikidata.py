import re
import os
import time
import random
import asyncio

import requests
from dotenv import load_dotenv
from functools import lru_cache
from typing import List

from database.orm import Game, Platform

load_dotenv()


class WikidataAPI:

    USER_AGENT = f'{os.getenv("USER_AGENT")} ({os.getenv("MAIL")})'
    WIKIDATA_API = "https://www.wikidata.org/w/api.php"

    HEADERS = {"User-Agent": USER_AGENT}

    session = requests.Session()
    session.headers.update(HEADERS)

    @staticmethod
    def get_with_retry(url, params, max_retries=6):
        """Lance la requete HTTP vers wikidata avec gestion des retry et temps d'attentes"""
        for tentative in range(max_retries):

            try:
                response = WikidataAPI.session.get(url, params=params, timeout=30)

                # Rate limit
                if response.status_code == 429:

                    retry_after = response.headers.get("Retry-After")

                    try:
                        attente = float(retry_after)
                    except (TypeError, ValueError):
                        attente = min(30, 2**tentative)

                    time.sleep(attente + random.uniform(0, 0.5))
                    continue

                # Erreurs temporaires
                if response.status_code in (500, 502, 503, 504):

                    time.sleep(min(30, 2**tentative))
                    continue

                response.raise_for_status()

                return response

            except requests.RequestException:

                if tentative == max_retries - 1:
                    raise

                time.sleep(min(30, 2**tentative))

        raise RuntimeError("Trop d'erreurs HTTP, réessaie plus tard.")

    @staticmethod
    @lru_cache(maxsize=10000)
    def obtenir_label_wikidata(qid):
        """Extraction des labels a partir d'un qid"""
        if not qid:
            return None

        params = {
            "action": "wbgetentities",
            "ids": qid,
            "props": "labels",
            "languages": "fr|en|mul",
            "format": "json",
        }

        try:

            data = WikidataAPI.get_with_retry(WikidataAPI.WIKIDATA_API, params).json()

            entity = data.get("entities", {}).get(qid, {})
            labels = entity.get("labels", {})

            # Priorité aux langues principales
            for langue in ("fr", "en", "mul"):

                label = labels.get(langue, {}).get("value")

                if label:
                    return label

            # Dernier recours
            if labels:
                return next(iter(labels.values())).get("value", qid)

        except Exception as e:

            print(f"Erreur récupération label {qid}: {e}")

        return qid

    @staticmethod
    def obtenir_labels_wikidata(qids):
        """
        Récupère plusieurs labels en UNE seule requête.

        Exemple :
            ["Q94", "Q140", "Q7889"]

        retourne :
            {
                "Q94": "jeu...",
                "Q140": "...",
                ...
            }
        """

        qids = list(
            set(
                qid
                for qid in qids
                if qid and isinstance(qid, str) and qid.startswith("Q")
            )
        )

        if not qids:
            return {}

        resultat = {}

        # Wikidata accepte plusieurs IDs.
        # On découpe pour éviter une URL trop grosse.
        taille_batch = 50

        for i in range(0, len(qids), taille_batch):

            batch = qids[i : i + taille_batch]

            params = {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "props": "labels",
                "languages": "fr|en|mul",
                "format": "json",
            }

            try:

                data = WikidataAPI.get_with_retry(
                    WikidataAPI.WIKIDATA_API, params
                ).json()

                for qid, entity in data.get("entities", {}).items():

                    labels = entity.get("labels", {})

                    label = None

                    for langue in ("fr", "en", "mul"):

                        label = labels.get(langue, {}).get("value")

                        if label:
                            break

                    if not label and labels:

                        label = next(iter(labels.values())).get("value", qid)

                    resultat[qid] = label or qid

            except Exception as e:

                print(f"Erreur récupération labels batch: {e}")

        return resultat

    @staticmethod
    def valeur_snak(snak):
        """Extraction des valeurs snak"""

        if not snak or snak.get("snaktype") != "value":
            return None

        datavalue = snak.get("datavalue", {})

        value = datavalue.get("value")

        if isinstance(value, dict):

            return value.get("id") or value.get("text")

        return value

    @staticmethod
    def date_wikidata_vers_chaine(snak):
        """Extraction de la date"""
        if not snak or snak.get("snaktype") != "value":
            return None

        value = snak.get("datavalue", {}).get("value", {})

        if not isinstance(value, dict):
            return None

        date_brute = value.get("time")
        precision = value.get("precision", 11)

        if not date_brute:
            return None

        match = re.match(r"^[+-](\d+)-(\d{2})-(\d{2})", date_brute)

        if not match:
            return date_brute

        annee, mois, jour = map(int, match.groups())

        if precision >= 11:
            return f"{annee:04d}-{mois:02d}-{jour:02d}"

        elif precision == 10:
            return f"{annee:04d}-{mois:02d}"

        elif precision == 9:
            return f"{annee:04d}"

        return date_brute

    @staticmethod
    def extraire_qids_qualificatifs(claim):
        """Extraction des qids des qualificatifs des platformes et region"""

        qualifiers = claim.get("qualifiers", {})

        plateformes = []
        regions = []

        # P400 = plateforme
        for snak in qualifiers.get("P400", []):

            qid = WikidataAPI.valeur_snak(snak)

            if qid:
                plateformes.append(qid)

        # P291 = lieu de publication
        # P1001 = juridiction
        # P3005 = applicable dans la région
        for prop in ("P291", "P1001", "P3005"):

            for snak in qualifiers.get(prop, []):

                qid = WikidataAPI.valeur_snak(snak)

                if qid:
                    regions.append({"propriete": prop, "id": qid})

        return plateformes, regions

    @staticmethod
    def classer_region(regions, labels):
        """Classement des regions"""
        if not regions:
            return 2, "Non précisée"

        ids = {r["id"] for r in regions}

        noms = " ".join(labels.get(r["id"], "").lower() for r in regions)

        if "Q142" in ids or "france" in noms:
            return 0, "France"

        if (
            "Q46" in ids
            or "Q458" in ids
            or "europe" in noms
            or "union européenne" in noms
            or "union europeenne" in noms
        ):
            return 1, "Europe"

        return (3, ", ".join(labels.get(r["id"], r["id"]) for r in regions))

    @staticmethod
    def extraire_dates_sortie(entite):
        """Extraction des dates de sortie/platformes/region"""
        claims = entite.get("claims", {})

        dates_brutes = []

        # Première passe :
        # on récupère seulement les QID.
        for claim in claims.get("P577", []):

            mainsnak = claim.get("mainsnak", {})

            date = WikidataAPI.date_wikidata_vers_chaine(mainsnak)

            if not date:
                continue

            plateformes, regions = WikidataAPI.extraire_qids_qualificatifs(claim)

            dates_brutes.append(
                {
                    "date": date,
                    "plateformes": plateformes,
                    "regions": regions,
                }
            )

        # Tous les QID nécessaires
        qids = set()

        for item in dates_brutes:

            qids.update(item["plateformes"])

            qids.update(r["id"] for r in item["regions"])

        # Une seule récupération batch
        labels = WikidataAPI.obtenir_labels_wikidata(qids)

        dates = []

        for item in dates_brutes:

            plateformes = [
                {"id": qid, "nom": labels.get(qid, qid)} for qid in item["plateformes"]
            ]

            regions = [
                {
                    "propriete": r["propriete"],
                    "id": r["id"],
                    "nom": labels.get(r["id"], r["id"]),
                }
                for r in item["regions"]
            ]

            priorite, region_affichee = WikidataAPI.classer_region(regions, labels)

            dates.append(
                {
                    "date": item["date"],
                    "plateformes": plateformes,
                    "regions": regions,
                    "region_prioritaire": region_affichee,
                    "priorite_region": priorite,
                }
            )

        dates.sort(key=lambda d: (d["priorite_region"], d["date"]))

        return dates

    @staticmethod
    def extraire_qids_propriete(entite, propriete):
        """Extraction des qid des proprietes"""

        resultat = []

        claims = entite.get("claims", {})

        for claim in claims.get(propriete, []):

            snak = claim.get("mainsnak", {})

            qid = WikidataAPI.valeur_snak(snak)

            if qid and isinstance(qid, str) and qid.startswith("Q"):
                resultat.append(qid)

        # Supprimer doublons
        return list(dict.fromkeys(resultat))

    @staticmethod
    def construire_propriete(entite, propriete, labels):

        qids = WikidataAPI.extraire_qids_propriete(entite, propriete)

        return [
            {
                "id": qid,
                "nom": labels.get(qid, qid),
                "wikidata_url": f"https://www.wikidata.org/wiki/{qid}",
            }
            for qid in qids
        ]

    @staticmethod
    def est_un_jeu_video(entite):
        """Verifie si la page est un jeu video en se fiant à l'indice P31"""

        claims = entite.get("claims", {})

        for claim in claims.get("P31", []):

            try:

                qid = claim["mainsnak"]["datavalue"]["value"]["id"]

                if qid == "Q7889":
                    return True

            except (KeyError, TypeError):
                pass

        return False

    @staticmethod
    def rechercher_wikidata(titre, limit=40):
        """Rechercher les pages wikidata en fonction du titre"""
        params = {
            "action": "wbsearchentities",
            "search": titre,
            "language": "fr",
            "uselang": "fr",
            "limit": limit,
            "format": "json",
        }

        response = WikidataAPI.get_with_retry(WikidataAPI.WIKIDATA_API, params)

        return response.json().get("search", [])

    @staticmethod
    def recuperer_entites(qids):
        """Recupere en batch de 50 la liste des entites wikidata à partir des qids des pages trouvées"""
        qids = list(dict.fromkeys(qids))

        if not qids:
            return {}

        resultat = {}

        # Batch de 50
        for i in range(0, len(qids), 50):

            batch = qids[i : i + 50]

            params = {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "format": "json",
                "props": "labels|claims|descriptions|sitelinks",  # récupère que ce qui est nécessaire
                "languages": "fr|en|mul",
            }

            response = WikidataAPI.get_with_retry(WikidataAPI.WIKIDATA_API, params)

            data = response.json()

            resultat.update(data.get("entities", {}))

        return resultat

    @staticmethod
    def extraire_ids(entite):
        """Extrait les ids Rawg et howlongtobeat"""
        claims = entite.get("claims", {})

        resultat = {
            "wikidata_id": entite["id"],
            "rawg_id": None,
            "howlongtobeat_id": None,
        }

        # P9968 = RAWG
        if "P9968" in claims:

            try:
                resultat["rawg_id"] = claims["P9968"][0]["mainsnak"]["datavalue"][
                    "value"
                ]
            except (KeyError, TypeError, IndexError):
                pass

        # P2816 = HowLongToBeat
        if "P2816" in claims:

            try:
                resultat["howlongtobeat_id"] = claims["P2816"][0]["mainsnak"][
                    "datavalue"
                ]["value"]
            except (KeyError, TypeError, IndexError):
                pass

        return resultat

    @staticmethod
    def trouver_jeu(titre):
        """Lance et orchestre la recherche des jeux à partir du titre"""
        candidats = WikidataAPI.rechercher_wikidata(titre, limit=40)

        if not candidats:
            return []

        # On recuperer la liste des qiqs des pages wiki candidates puis leurs entites wikidata
        qids = [candidat["id"] for candidat in candidats]

        entites = WikidataAPI.recuperer_entites(qids)

        # on filtre les entites potentielles pour garder que les games
        jeux_valides = []

        for candidat in candidats:

            qid = candidat["id"]

            entite = entites.get(qid)

            if not entite:
                continue

            if not WikidataAPI.est_un_jeu_video(entite):
                continue

            jeux_valides.append((candidat, entite))

        # on recupere la liste des qid des labels (dev, publisher, platforms ..)
        qids_labels = set()

        for candidat, entite in jeux_valides:

            claims = entite.get("claims", {})

            # Propriétés
            for propriete in (
                "P136",  # genres
                "P178",  # développeurs
                "P123",  # éditeurs
                "P86",  # compositeurs
                "P400",  # plateformes
            ):

                for claim in claims.get(propriete, []):

                    qid = WikidataAPI.valeur_snak(claim.get("mainsnak", {}))

                    if qid and isinstance(qid, str) and qid.startswith("Q"):
                        qids_labels.add(qid)

            # Dates + qualificatifs
            for claim in claims.get("P577", []):

                plateformes, regions = WikidataAPI.extraire_qids_qualificatifs(claim)

                qids_labels.update(plateformes)

                qids_labels.update(r["id"] for r in regions)

        # on recupere les labels
        labels = WikidataAPI.obtenir_labels_wikidata(qids_labels)

        # Build des resultats
        resultats = []

        for candidat, entite in jeux_valides:

            ids = WikidataAPI.extraire_ids(entite)

            ids["label"] = candidat.get("label")
            ids["description"] = candidat.get("description")
            ids["dates_sortie"] = WikidataAPI.extraire_dates_sortie(entite)
            ids["genres"] = WikidataAPI.construire_propriete(entite, "P136", labels)

            ids["developpeurs"] = WikidataAPI.construire_propriete(
                entite, "P178", labels
            )
            ids["editeurs"] = WikidataAPI.construire_propriete(entite, "P123", labels)
            ids["compositeurs"] = WikidataAPI.construire_propriete(
                entite, "P86", labels
            )

            ids["platforms"] = WikidataAPI.construire_propriete(entite, "P400", labels)

            resultats.append(ids)

        return resultats

    @staticmethod
    def transform_jeu(resultats) -> List[Game]:
        """Transforme les données vers les schema de l'orm Game, Platform ..."""
        print(f"Nombre des jeux trouvés : " f"{len(resultats)}")

        lstgames: List[Game] = []

        for jeu in resultats:

            print("-")
            print("Wikidata :", jeu["wikidata_id"])
            print("Nom      :", jeu["label"])
            print("Description :", jeu["description"])
            print("RAWG     :", jeu["rawg_id"])
            print("HLTB     :", jeu["howlongtobeat_id"])

            playtime = None
            img = None

            lstplatforms = []
            lstgenres = " ,".join(g["nom"] for g in jeu["genres"])

            for p in jeu["platforms"]:

                lstplatforms.append(
                    Platform(idRawg=None, idWiki=p["id"], name=p["nom"])
                )

            for sortie in jeu["dates_sortie"]:

                plateformes = (
                    ", ".join(p["nom"] for p in sortie["plateformes"])
                    or "Plateforme non précisée"
                )

                print(
                    f"Date : {sortie['date']} | "
                    f"Région : "
                    f"{sortie['region_prioritaire']} | "
                    f"Plateforme : "
                    f"{plateformes}"
                )

            game = Game(
                name=jeu["label"],
                idWiki=jeu["wikidata_id"],
                idRawg=jeu["rawg_id"],
                idHltb=jeu["howlongtobeat_id"],
                playtimeHltb=playtime,
                developers=None,
                publishers=None,
                composers=None,
                imageUrl=img,
                platforms=lstplatforms,
                tags=None,
                genres=lstgenres,
                release=None,
            )

            lstgames.append(game)

        return lstgames

    @staticmethod
    async def search_jeu(query: str) -> List[Game]:
        """Appel async d'orchestration de la recherche de jeu"""
        if not query.strip():
            return []

        raw_data = await asyncio.to_thread(WikidataAPI.trouver_jeu, query)

        print("recherche ok")

        if not raw_data:
            return []

        return WikidataAPI.transform_jeu(raw_data)
