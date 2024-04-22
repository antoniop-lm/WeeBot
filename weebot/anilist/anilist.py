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
from pprint import pprint
from Levenshtein import ratio
import weebot


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
                    title {
                        english
                        romaji
                        native
                        userPreferred
                    }
                    season
                    seasonYear
                    id
                    format
                    episodes
                }
            }
        }
    """

    # Define our query variables and values that will be used in the query request
    variables = {"searchTerm": search_term, "perPage": 5}

    response = requests.post(weebot.url, json={"query": query, "variables": variables})

    content = response.json()
    anime_found = []

    # saving the closest match to the provided title
    if search_term:
        for media in content["data"]["Page"]["media"]:
            ratio_english = ratio(
                media["title"]["english"].lower() if media["title"]["english"] else "",
                search_term.lower(),
            )
            ratio_romaji = ratio(media["title"]["romaji"].lower(), search_term.lower())
            ratio_native = ratio(media["title"]["native"].lower(), search_term.lower())

            if (
                ratio_english >= weebot.score_treshold
                or ratio_romaji >= weebot.score_treshold
                or ratio_native >= weebot.score_treshold
            ):
                anime_found.append(
                    {
                        "name": media["title"]["romaji"],
                        "score": ratio_romaji,
                        "id": media["id"],
                    }
                )
                continue
    else:
        anime_found.append(
            {"name": media["title"]["romaji"], "score": 1.0, "id": media["id"]}
        )

    return anime_found
