#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define Anime Watch Party Handler Telegram Bot update operations

:method update_anime(id: int = None, chat_id: str = None, episode: int = None): tuple[bool, str, int]
:method retrieve_updatable_anime_list(chat_id: str, pageNumber: int = 1): tuple[dict, int]
:method update_all_anime(): list
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import TRACKED_LIST_FILE, PAGE_SIZE, MEDIA_STATUS
import logging, json, math
from weebot.integrations.anilist import search_anime
from weebot.database.ping import who_to_ping

def update_anime(id: int = None, chat_id: str = None, episode: int = None):
    """
    Update anime based on anime id and chat id.
    
    :param id: Anime id
    :param chat_id: Telegram's chat id
    :param episode: Anime episode new value
    :return: True if is tracked, False otherwise, Anime name and Anime amount of episodes
    """
    # Set data
    data = []
    animeName = ''
    updated = False
    animeEpisodes = 0

    # Iterate over list of tracked animes and check if it is tracked by the context provided
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)

        if (file.tell()):
            file.seek(0)
            data = json.load(file)

            for anime in data:
                if anime["id"] == id:
                    animeName = anime["namePreferred"]
                    for watchlist in anime["watchlist"]:
                        # Update episode if context is found and pass validations
                        if chat_id in watchlist:
                            animeEpisodes = anime["episodes"]
                            if animeEpisodes != None and animeEpisodes >= episode and episode > 0:
                                updated = True
                                watchlist[chat_id]["episode"] = episode
                                break
                    
                    break
        
        # Update file
        if (updated):
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animeName, animeEpisodes

def retrieve_updatable_anime_list(chat_id: str, pageNumber: int = 1):
    """
    Retrieve updatable animes based on pagination and chat id.
    
    :param chat_id: Telegram's chat id
    :param pageNumber: Current page for pagination
    :return: List of animes and Total amount of animes
    """
    # Set data
    aniList = {}

    # Iterate over list of tracked animes and check if it is tracked by the context provided
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)

        if (file.tell()):
            file.seek(0)
            data = json.load(file)

            for anime in data:
                for watchlist in anime["watchlist"]:
                    if chat_id in watchlist:
                        # Add only updatable animes
                        if anime["episodes"] != None:
                            aniList.update({anime["id"]: anime["namePreferred"]})

    # Set pagination information and split anime list accordingly
    totalSize = math.ceil(len(aniList)/PAGE_SIZE)
    if math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, totalSize

def update_all_anime():
    """
    Update all animes if any relevant information is changed.

    :return: List of chat and animes to ping
    """
    # Set data
    data = []
    pingList = []
    queryList = []

    # Iterate over list of tracked animes
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        updated = False

        # Set Ids to query
        if (file.tell()):
            file.seek(0)
            data = json.load(file)

            for anime in data:
                queryList.append(anime["id"])

        # Query for anime data on anilist
        for id in queryList:
            found = search_anime(id=id)
            if len(found) == 0:
                continue
            for anime in data:
                if "imdb" in anime["url"]:
                    continue
                if anime["id"] == found[0]["id"]:
                    # Update information if any is found
                    if (anime["status"] != found[0]["status"] 
                        or found[0]["status"] == MEDIA_STATUS["RELEASING"]):
                        updated = True
                        episodePingList = who_to_ping(anime,found[0])

                        # Set contexts to receive updates of new episodes
                        if len(episodePingList) > 0:
                            text = 'Episode '+str(anime["nextAiringEpisode"]["episode"])+' of '+str(anime["namePreferred"]+' is live!')
                            for chat in episodePingList:
                                notExists = True
                                for chatPing in pingList:
                                    if chat in chatPing:
                                        chatPing[chat].append(text)
                                        notExists = False
                                        break

                                if notExists:
                                    pingList.append({chat: [text]})

                        anime["status"] = found[0]["status"]
                        anime["nextAiringEpisode"] = found[0]["nextAiringEpisode"]
                        anime["episodes"] = found[0]["episodes"]

                    break
        
        # Update file
        if (updated):
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return pingList