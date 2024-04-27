#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define Anime Watch Party Handler Telegram Bot ping operations

:method retrieve_pingable_anime_list(chat_id: str, pageNumber: int = 1): tuple[dict, int]
:method ping_anime(id: int = None, chat_id: str = None): tuple[list, str]
:method ping_multiples_animes(indexList: object, chat_id: str): tuple[list, list, list]
:method who_to_ping(old: object, new: object): list
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import TRACKED_LIST_FILE, PAGE_SIZE
import logging, json, math

def retrieve_pingable_anime_list(chat_id: str, pageNumber: int = 1):
    """
    Retrieve pingable animes based on pagination and chat id.
    
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
                        # Add only pingable animes
                        if len(watchlist[chat_id]["party"]) > 0:
                            aniList.update({anime["id"]: anime["namePreferred"]})

    # Set pagination information and split anime list accordingly
    totalSize = math.ceil(len(aniList)/PAGE_SIZE)
    if math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, totalSize

def ping_anime(id: int = None, chat_id: str = None):
    """
    Retrieve usernames to ping based on anime id and chat id.
    
    :param id: Anime id
    :param chat_id: Telegram's chat id
    :return: List of usernames to ping and Anime name
    """
    # Set data
    data = []
    animeName = ''
    usernames = []

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
                        # Set usernames to ping if context is found
                        if chat_id in watchlist:
                            for user in watchlist[chat_id]["party"]:
                                usernames.append(next(iter(user.values())))
                            break

    return usernames, animeName

def ping_multiples_animes(indexList: object, chat_id: str):
    """
    Retrieve usernames to ping based on list of anime index and chat id.
    
    :param indexList: List of anime index
    :param chat_id: Telegram's chat id
    :return: List of usernames to ping, List of pingable animes and List of unpingable animes
    """
    # Set data
    count = 0
    usernames = []
    animes = []
    animesUnsubscribed = []

    # Iterate over list of tracked animes and check if it is tracked by the context provided
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)

        if (file.tell()):
            file.seek(0)
            data = json.load(file)

            for anime in data:
                for watchlist in anime["watchlist"]:
                    if chat_id in watchlist:
                        # Check if index matches the list provided
                        if str(count) in indexList:
                            # Set list of subscribed and unsubscribed animes
                            if (anime["namePreferred"] not in animes) and (anime["namePreferred"] not in animesUnsubscribed):
                                if len(watchlist[chat_id]["party"]) > 0:
                                    animes.append(anime["namePreferred"])
                                else:
                                    animesUnsubscribed.append(anime["namePreferred"])

                            # Set usernames to ping
                            for user in watchlist[chat_id]["party"]:
                                username = next(iter(user.values()))
                                if username not in usernames:
                                    usernames.append(username)

                        count += 1
                        break

    return usernames, animes, animesUnsubscribed

def who_to_ping(old: object, new: object):
    """
    Retrieve list of chat id to ping when there is a new anime episode based on new and old anime metadata.
    
    :param old: Old anime metadata
    :param new: New anime metadata
    :return: List of usernames to chat ids to ping
    """
    # Set Data
    pingList = []

    # Retrieve list of contexts to receive new episode updates
    if old["nextAiringEpisode"] != None:
        if (new["nextAiringEpisode"] == None
            or old["nextAiringEpisode"]["episode"] != new["nextAiringEpisode"]["episode"]
            or new["nextAiringEpisode"]["timeUntilAiring"] < 0):
            for watchlist in old["watchlist"]:
                pingList.append(next(iter(watchlist.keys())))

    return pingList
