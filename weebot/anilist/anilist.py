""" 
track - Choose an anime to track new episodes.
|-> search for the anime id         DONE
|-> check if it is already tracked  DONE  
|-> track if not found
untrack - Stop anime new episodes updates.
list - List all current animes being watched and their progress.
|-> list the tracked json
update - Set which was the last episode watched for an anime.
subscribe - Subscribe to receive updates when a watch party is happening.
ping - Ping all subscribed persons to an anime.
unsubscribe - Unsubscribe to stop receiving anime pings.

tracked_json:
{
Title
Anilist ID
URL
N of Episodes
Last Episode Seen
Subscribers
}
"""

from operator import is_
import requests
import json
import logging
from pprint import pprint
from Levenshtein import ratio, jaro, jaro_winkler, distance
from weebot import URL, SCORE_TRESHOLD, ANIMEURL, ANIME_RETURN_SIZE, ANIME_DISTANCE


"""Searchs for an anime entry

:param id: The id of the anime
:type id: int
:param search_term: The title of the anime
:type search_term: str
:returns: A list with at most the 5 closest matches containing the name, id and levenshtein score ratio
:rtype: list
"""


def search_anime(id: int = None, search_term: str = None):
    if id is None and search_term is None:
        return "Missing argument in search. Please provide either ID or Title"
    # change to exception or w/e to handle

    # the graphql query that will be sent to the anilist page
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

    response = requests.post(URL, json={"query": query, "variables": variables})

    content = response.json()
    anime_found = []
    finalList = []

    # saving the closest match to the provided title
    if search_term:
        for media in content["data"]["Page"]["media"]:
            ratio_english = calcRatio(
                media["title"]["english"].lower() if media["title"]["english"] else "",
                search_term.lower(),
            )
            ratio_romaji = calcRatio(media["title"]["romaji"].lower(), search_term.lower())
            ratio_native = calcRatio(media["title"]["native"].lower(), search_term.lower())
            
            maxRatio = max(ratio_english,ratio_romaji,ratio_native)

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

    anime_found.sort(key=orderByScore, reverse=True)

    count = 0
    for anime in anime_found:
        if count == ANIME_RETURN_SIZE:
            break
        finalList.append(anime)
        count += 1

    return finalList

def calcRatio(anime: str, search_term: str):
    ratioValue = ratio(anime.lower(), search_term.lower())
    jaroValue = jaro(anime.lower(), search_term.lower())
    jaroWinklerValue = jaro_winkler(anime.lower(), search_term.lower())

    meanRatio = (ratioValue + jaroValue + jaroWinklerValue)/3

    substring = 0
    if (anime in search_term) or (search_term in anime) or distance(anime,search_term) < ANIME_DISTANCE:
        substring = 1

    finalRatio = meanRatio + substring

    return finalRatio

def orderByScore(e):
    return e["score"]