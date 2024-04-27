#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define request methods for anilist API

:method search_anime(id: int = None, search_term: str = None): list
:method calcRatio(anime: str, search_term: str): float
:method orderByScore(e: object): Any
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import URL, SCORE_TRESHOLD, ANIMEURL, ANIME_RETURN_SIZE, ANIME_DISTANCE
import logging, requests
from Levenshtein import ratio, jaro, jaro_winkler, distance

def search_anime(id: int = None, search_term: str = None):
    """
    Search anime using either anime id or search_term with fuzzy string.

    :param id: Anime id on anilist
    :param search_term: Anime name searched
    :return: List of animes found based on score threshold or unique anime by id
    """
    # Parameter check
    if id is None and search_term is None:
        raise Exception("Missing argument in search. Please provide either ID or Title")

    # The graphql query that will be sent to the anilist page
    query = """
        query ($searchTerm: String, $id: Int, $perPage: Int) {
            Page(page:1, perPage: $perPage) {
                pageInfo {
                    total
                    perPage
                    currentPage
                    lastPage
                    hasNextPage
                }
                media(search: $searchTerm, id: $id, type: ANIME) {
                    id
                    title {
                        english
                        romaji
                        native
                        userPreferred
                    }
                    description
                    status
                    startDate {
                        year
                        month
                        day
                    }
                    format
                    episodes
                    nextAiringEpisode {
                        id
                        episode
                        airingAt
                        timeUntilAiring
                    }
                    airingSchedule {
                        nodes {
                            id
                            episode
                            airingAt
                            timeUntilAiring
                        }
                        pageInfo {
                            total
                            perPage
                            currentPage
                            lastPage
                            hasNextPage
                        }
                    }
                    externalLinks {
                        site
                        url
                    }
                }
            }
        }
    """

    # Define our query variables and values that will be used in the query request
    if (search_term is None):
        variables = {"id": id, "perPage": 1}

    else:
        variables = {"searchTerm": search_term, "perPage": 50}

    # Make request
    response = requests.post(URL, json={"query": query, "variables": variables})

    # Set data
    content = response.json()
    anime_found = []
    finalList = []

    # Saving the closest match to the provided title
    if search_term:
        for media in content["data"]["Page"]["media"]:
            # Calculate ratio
            ratio_english = calcRatio(
                media["title"]["english"].lower() if media["title"]["english"] else "",
                search_term.lower(),
            ) if media["title"]["english"] != None else 0
            ratio_romaji = calcRatio(media["title"]["romaji"].lower(), search_term.lower()) if media["title"]["romaji"] != None else 0
            ratio_native = calcRatio(media["title"]["native"].lower(), search_term.lower()) if media["title"]["native"] != None else 0
            maxRatio = max(ratio_english,ratio_romaji,ratio_native)

            # Save score if ratio is above score threshold
            if maxRatio >= SCORE_TRESHOLD:
                anime_found.append(
                    {
                        "name": media["title"]["romaji"],
                        "namePreferred": media["title"]["userPreferred"],
                        "score": maxRatio,
                        "format": media["format"],
                        "status": media["status"],
                        "nextAiringEpisode": media["nextAiringEpisode"],
                        "id": media["id"],
                        "url": ANIMEURL + str(media["id"]),
                        "episodes": media["episodes"]
                    }
                )

    # Save only the corresponding Id provided
    else:
        for media in content["data"]["Page"]["media"]:
            anime_found.append(
                {
                    "name": media["title"]["romaji"], 
                    "namePreferred": media["title"]["userPreferred"],
                    "score": 1.0, 
                    "format": media["format"],
                    "status": media["status"],
                    "nextAiringEpisode": media["nextAiringEpisode"],
                    "id": media["id"],
                    "url": ANIMEURL + str(media["id"]),
                    "episodes": media["episodes"]
                }
            )

    # Sort animes by closest match descending and get only the first # animes
    anime_found.sort(key=orderByScore, reverse=True)
    count = 0
    for anime in anime_found:
        if count == ANIME_RETURN_SIZE:
            break
        finalList.append(anime)
        count += 1

    return finalList

def calcRatio(anime: str, search_term: str):
    """
    Calculate search term score based on anime name.

    :param anime: Anime name
    :param search_term: Anime name searched
    :return: Score value between strings
    """
    # Get ratio for each algorithm
    ratioValue = ratio(anime.lower(), search_term.lower())
    jaroValue = jaro(anime.lower(), search_term.lower())
    jaroWinklerValue = jaro_winkler(anime.lower(), search_term.lower())

    # Get mean of those ratios
    meanRatio = (ratioValue + jaroValue + jaroWinklerValue)/3

    # Add weight if it is a substring or have a close distance
    substring = 0
    if (anime in search_term) or (search_term in anime) or distance(anime,search_term) < ANIME_DISTANCE:
        substring = 1

    # Set final ratio
    finalRatio = meanRatio + substring

    return finalRatio

def orderByScore(e: object):
    """
    Select list key as score to help sort.

    :param e: List to select key
    :return: Key to sort
    """
    return e["score"]