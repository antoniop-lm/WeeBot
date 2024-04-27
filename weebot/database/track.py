#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define Anime Watch Party Handler Telegram Bot track and untrack operations

:method check_if_tracked(id: int = -1, search_term: str = None, chat_id: str = None): tuple[bool, list, str]
:method track_anime(id: int = None, chat_id: str = None): list
:method untrack_anime(id: int = None, chat_id: str = None): tuple[bool, str]
:method untrack_multiple_animes(indexList: object, chat_id: str): tuple[bool, list]
:method retrieve_anime_list(chat_id: str, pageNumber: int = 1): tuple[dict, int]
:method retrieve_anime_list_detail(chat_id: str, pageNumber: int = 1, usePagination: bool = True): tuple[dict, int, int, str]
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import TRACKED_LIST_FILE, PAGE_SIZE
import logging, json, math
from datetime import datetime
from weebot.integrations.anilist import search_anime

def check_if_tracked(id: int = -1, search_term: str = None, chat_id: str = None):
    """
    Check if anime is already tracked based on chat id and anime id or search term.
    
    :param id: Anime id
    :param search_term: Anime name searched
    :param chat_id: Telegram's chat id
    :return: True if is tracked, False otherwise, Found Anime metadata and Result message
    """
    # Set data
    found = []
    msg = ""
    is_tracked = False

    # Iterate over list of tracked animes and check if it is tracked by the context provided
    with open(TRACKED_LIST_FILE, "a+") as file:
        if (file.tell()):
            file.seek(0)
            data = json.load(file)

            for anime in data:
                if anime["id"] == id:
                    for watchlist in anime["watchlist"]:
                        if chat_id in watchlist:
                            is_tracked = True
                            found = anime
                            break

                if is_tracked:
                    break
    
    # Set response
    if not is_tracked:
        found = search_anime(id=id, 
                             search_term=search_term)
        msg = "Found {} results.".format(len(found))

    else:
        msg = "This anime is already tracked."
    
    return is_tracked, found, msg

def track_anime(id: int = None, chat_id: str = None):
    """
    Track anime based on anime id and chat id.
    
    :param id: Anime id
    :param chat_id: Telegram's chat id
    :return: Anime tracked
    """
    from weebot.utils import orderByName
    # Set data
    found = search_anime(id=id)
    data = []

    # Iterate over list of tracked animes and check if it is tracked by the context provided
    with open(TRACKED_LIST_FILE, "r+") as file:
        notExists = True
        file.seek(0,2)

        if (file.tell()):
            file.seek(0)
            data = json.load(file)

            for anime in data:
                # Update anime watchlist if found 
                if (anime["id"] == found[0]["id"]):
                    anime["watchlist"].append(
                        {
                            chat_id: {
                                "episode": 1,
                                "party": []
                            }
                        }
                    )
                    notExists = False
                    break
        
        # Add anime to list if not found
        if (notExists):
            found[0]["watchlist"] = [
                {
                    chat_id: {
                        "episode": 1,
                        "party": []
                    }
                }
            ]
            data.append(found[0])
        
        # Update file
        data.sort(key=orderByName, reverse=False)
        file.seek(0)
        file.write(json.dumps(data) + '\n')
        file.truncate()

    return found

def untrack_anime(id: int = None, chat_id: str = None):
    """
    Untrack anime based on anime id and chat id.
    
    :param id: Anime id
    :param chat_id: Telegram's chat id
    :return: True if successfully untracked, False otherwise and Anime name
    """
    # Set data
    data = []
    animeName = ''
    updated = False
    remove = False

    # Iterate over list of tracked animes and check if it is tracked by the context provided
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)

        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            newData = []

            for anime in data:
                # Untrack anime if found
                if anime["id"] == id:
                    animeName = anime["namePreferred"]
                    newWatchlist = []
                    for watchlist in anime["watchlist"]:
                        # Remove context
                        if chat_id not in watchlist:
                            newWatchlist.append(watchlist)
                        else:
                            updated = True
                    anime["watchlist"] = newWatchlist

                    # No one is tracking anymore
                    if len(newWatchlist) == 0:
                        remove = True

                # Add to aux list if not
                else:
                    newData.append(anime)

            # Remove anime from file if no one is tracking
            if remove:
                data = newData

        # Update file
        if (updated):
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animeName

def untrack_multiple_animes(indexList: object, chat_id: str):
    """
    Untrack multiple animes based on list of animes index and chat id.
    
    :param indexList: List of anime index
    :param chat_id: Telegram's chat id
    :return: True if successfully updated, False otherwise and List of untracked anime names
    """
    # Set data
    data = []
    animes = []
    updated = False
    remove = False
    count = 0

    # Iterate over list of tracked animes and check if it is tracked by the context provided
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)

        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            newData = []

            for anime in data:
                saveAnime = True
                untracked = False
                newWatchlist = []
                for watchlist in anime["watchlist"]:
                    if chat_id in watchlist:
                        # Check if index matches the list provided
                        if str(count) in indexList:
                            # Remove context
                            if anime["namePreferred"] not in animes:
                                animes.append(anime["namePreferred"])
                            updated = True
                            untracked = True

                        else:
                            newWatchlist.append(watchlist)

                        count += 1

                    else:
                        newWatchlist.append(watchlist)

                # Save new watchlist
                if untracked:
                    anime["watchlist"] = newWatchlist
                    
                # No one is tracking anymore
                if len(newWatchlist) == 0:
                    remove = True
                    saveAnime = False

                # Add to aux list if more contexts tracks
                if saveAnime:
                    newData.append(anime)

            # Remove anime from file if no one is tracking
            if remove:
                data = newData
        
        # Update file
        if (updated):
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animes

def retrieve_anime_list(chat_id: str, pageNumber: int = 1):
    """
    Retrieve tracked animes based on pagination and chat id.
    
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
                        aniList.update({anime["id"]: anime["namePreferred"]})

    # Set pagination information and split anime list accordingly
    totalSize = math.ceil(len(aniList)/PAGE_SIZE)
    if math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, totalSize

def retrieve_anime_list_detail(chat_id: str, pageNumber: int = 1, usePagination: bool = True):
    """
    Retrieve tracked animes with more details based on chat id and w/wo pagination.
    
    :param chat_id: Telegram's chat id
    :param pageNumber: Current page for pagination
    :param usePagination: Ignore or Apply pagination
    :return: List of animes, Amount of animes on list, Total amount of animes and Index information of animes
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
                        episode = ((str(watchlist[chat_id]["episode"]) + '/' + str(anime["episodes"]) + ' episodes') 
                                   if str(anime["episodes"]) != 'None' 
                                   else 'TBA')
                        episode += ((' - episode ' + str(anime["nextAiringEpisode"]["episode"]) + ': ' 
                                     + datetime.strftime(datetime.fromtimestamp(anime["nextAiringEpisode"]["airingAt"]),'%d/%m/%Y, %H:%M')) 
                                   if anime["nextAiringEpisode"] != None
                                   else '')
                        animeName = '<a href="'+anime["url"]+'/">'+anime["namePreferred"]+'</a>'
                        aniList.update({animeName: '\n'+episode})

    # Set pagination information and split anime list accordingly
    totalSize = math.ceil(len(aniList)/PAGE_SIZE) if usePagination else len(aniList)
    indexInformation = 'Index ' + str((pageNumber-1)*PAGE_SIZE) + '-' + str(pageNumber*PAGE_SIZE-1) + '\n\n'
    if usePagination and math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, len(aniList), totalSize, indexInformation
