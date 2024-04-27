#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define Anime Watch Party Handler Telegram Bot subscribe and unsubscribe operations

:method subscribe_anime(id: int = None, chat_id: str = None, user_id: str = None, username: str = None): tuple[bool, str]
:method subscribe_multiple_animes(indexList: object, chat_id: str, user_id: str, username: str): tuple[bool, list, list]
:method unsubscribe_anime(id: int = None, chat_id: str = None, user_id: str = None): tuple[bool, str]
:method unsubscribe_multiple_animes(indexList: object, chat_id: str, user_id: str): tuple[bool, list, list]
:method retrieve_subscribable_anime_list(chat_id: str, user_id: str, pageNumber: int = 1): tuple[dict, int]
:method retrieve_unsubscribable_anime_list(chat_id: str, user_id: str, pageNumber: int = 1): tuple[dict, int]
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import TRACKED_LIST_FILE, PAGE_SIZE
import logging, json, math

def subscribe_anime(id: int = None, chat_id: str = None, user_id: str = None, username: str = None):
    """
    Subscribe user to anime based on anime id, chat id and user id.
    
    :param id: Anime id
    :param chat_id: Telegram's chat id
    :param user_id: Telegram's user id
    :param username: Telegram's username
    :return: True if successfully updated, False otherwise and anime name
    """
    # Set data
    data = []
    animeName = ''
    updated = False

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
                        # Subscribe to anime if context is found and not previously subscribed
                        if chat_id in watchlist:
                            notSubscribed = True
                            for user in watchlist[chat_id]["party"]:
                                if user_id in user:
                                    notSubscribed = False
                                    break

                            if notSubscribed:
                                watchlist[chat_id]["party"].append(
                                    {
                                        user_id: '@'+username
                                    }
                                )
                                updated = True
                                break

                    break
        
        # Update file
        if (updated):
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animeName

def subscribe_multiple_animes(indexList: object, chat_id: str, user_id: str, username: str):
    """
    Subscribe user to multiple animes based on list of animes index, chat id and user id.
    
    :param indexList: List of anime index
    :param chat_id: Telegram's chat id
    :param user_id: Telegram's user id
    :param username: Telegram's username
    :return: True if successfully updated, False otherwise, List of subscribed anime names and List of failed anime names
    """
    # Set data
    data = []
    animes = []
    failedAnimes = []
    updated = False
    count = 0

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
                            notSubscribed = True
                            # Set list of already subscribed animes
                            for user in watchlist[chat_id]["party"]:
                                if user_id in user:
                                    notSubscribed = False
                                    if anime["namePreferred"] not in failedAnimes:
                                        failedAnimes.append(anime["namePreferred"])
                                    break
                            
                            # Subscribe to anime if not previously subscribed
                            if notSubscribed:
                                watchlist[chat_id]["party"].append(
                                    {
                                        user_id: '@'+username
                                    }
                                )
                                if anime["namePreferred"] not in animes:
                                    animes.append(anime["namePreferred"])
                                updated = True

                        count += 1
                        break
        
        # Update file
        if (updated):
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animes, failedAnimes

def unsubscribe_anime(id: int = None, chat_id: str = None, user_id: str = None):
    """
    Unsubscribe user to anime based on anime id, chat id and user id.
    
    :param id: Anime id
    :param chat_id: Telegram's chat id
    :param user_id: Telegram's user id
    :return: True if successfully updated, False otherwise and anime name
    """
    # Set data
    data = []
    animeName = ''
    updated = False

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
                        # Unsubscribe to anime if context is found and is previously subscribed
                        if chat_id in watchlist:
                            newParty = []
                            for user in watchlist[chat_id]["party"]:
                                if user_id not in user:
                                    newParty.append(user)
                                else:
                                    updated = True

                            # Remove party if no one is subscribed
                            watchlist[chat_id]["party"] = newParty
                            break

                    break
        
        # Update file
        if (updated):
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animeName

def unsubscribe_multiple_animes(indexList: object, chat_id: str, user_id: str):
    """
    Unsubscribe user to multiple animes based on list of animes index, chat id and user id.
    
    :param indexList: List of anime index
    :param chat_id: Telegram's chat id
    :param user_id: Telegram's user id
    :return: True if successfully updated, False otherwise, List of unsubscribed anime names and List of failed anime names
    """
    # Set data
    data = []
    animes = []
    failedAnimes = []
    updated = False
    count = 0

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
                            newParty = []
                            notUnsubscribed = True
                            for user in watchlist[chat_id]["party"]:
                                if user_id not in user:
                                    newParty.append(user)
                                else:
                                    if anime["namePreferred"] not in animes:
                                        animes.append(anime["namePreferred"])
                                    updated = True
                                    notUnsubscribed = False

                            if notUnsubscribed and anime["namePreferred"] not in failedAnimes:
                                failedAnimes.append(anime["namePreferred"])
                            # Remove party if no one is subscribed
                            watchlist[chat_id]["party"] = newParty

                        count += 1
                        break
        
        # Update file
        if (updated):
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animes, failedAnimes

def retrieve_subscribable_anime_list(chat_id: str, user_id: str, pageNumber: int = 1):
    """
    Retrieve subscribable animes based on pagination, chat id and user id.
    
    :param chat_id: Telegram's chat id
    :param user_id: Telegram's user id
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
                        # Add only subscribable animes
                        notSubscribed = True
                        for user in watchlist[chat_id]["party"]:
                            if user_id in user:
                                notSubscribed = False

                        if notSubscribed:
                            aniList.update({anime["id"]: anime["namePreferred"]})

    # Set pagination information and split anime list accordingly
    totalSize = math.ceil(len(aniList)/PAGE_SIZE)
    if math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, totalSize

def retrieve_unsubscribable_anime_list(chat_id: str, user_id: str, pageNumber: int = 1):
    """
    Retrieve unsubscribable animes based on pagination, chat id and user id.
    
    :param chat_id: Telegram's chat id
    :param user_id: Telegram's user id
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
                        # Add only unsubscribable animes
                        for user in watchlist[chat_id]["party"]:
                            if user_id in user:
                                aniList.update({anime["id"]: anime["namePreferred"]})

    # Set pagination information and split anime list accordingly
    totalSize = math.ceil(len(aniList)/PAGE_SIZE)
    if math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, totalSize
