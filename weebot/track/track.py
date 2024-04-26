import logging
from datetime import datetime
# from dateutil import tz
import json
import math
from xmlrpc.client import Boolean
from weebot.anilist.anilist import search_anime, calcRatio
from weebot import TRACKED_LIST_FILE, SCORE_TRESHOLD, PAGE_SIZE, MEDIA_STATUS

def orderByName(e):
    return e["namePreferred"]

def check_if_tracked(id: int = -1, search_term: str = None, chat_id: str = None):
    found = []
    msg = ""
    is_tracked = False

    with open(TRACKED_LIST_FILE, "a+") as file:
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                # score = calcRatio(anime["name"].lower(), search_term.lower())
                # if anime["id"] == id or score >= SCORE_TRESHOLD:
                if anime["id"] == id:
                    for watchlist in anime["watchlist"]:
                        if chat_id in watchlist:
                            is_tracked = True
                            found = anime
                            break
                if is_tracked:
                    break

    if not is_tracked:
        found = search_anime(id=id, search_term=search_term)
        msg = "Found {} results.".format(len(found))
        #show the user the found animes
        #ask which one to track

    else:
        msg = "This anime is already tracked."
    
    return is_tracked, found, msg

def track_anime(id: int = None, chat_id: str = None):
    found = search_anime(id=id)
    data = []
    with open(TRACKED_LIST_FILE, "r+") as file:
        notExists = True
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
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
        
        # logging.info(data)
        data.sort(key=orderByName, reverse=False)
        file.seek(0)
        file.write(json.dumps(data) + '\n')
        file.truncate()

    return found

def untrack_anime(id: int = None, chat_id: str = None):
    data = []
    animeName = ''
    updated = False
    remove = False
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            newData = []
            for anime in data:
                if anime["id"] == id:
                    animeName = anime["namePreferred"]
                    newWatchlist = []
                    for watchlist in anime["watchlist"]:
                        if chat_id not in watchlist:
                            newWatchlist.append(watchlist)
                        else:
                            updated = True
                    anime["watchlist"] = newWatchlist
                    if len(newWatchlist) == 0:
                        remove = True
                else:
                    newData.append(anime)
            if remove:
                data = newData
        
        # logging.info(data)
        if (updated):
            # data.sort(key=orderByName, reverse=False)
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animeName

def subscribe_anime(id: int = None, chat_id: str = None, user_id: str = None, username: str = None):
    data = []
    animeName = ''
    updated = False
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                if anime["id"] == id:
                    animeName = anime["namePreferred"]
                    for watchlist in anime["watchlist"]:
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
        
        # logging.info(data)
        if (updated):
            # data.sort(key=orderByName, reverse=False)
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animeName

def subscribe_multiple_animes(indexList: object, chat_id: str, user_id: str, username: str):
    data = []
    animes = []
    failedAnimes = []
    updated = False
    count = 0
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                for watchlist in anime["watchlist"]:
                    if chat_id in watchlist:
                        if str(count) in indexList:
                            notSubscribed = True
                            for user in watchlist[chat_id]["party"]:
                                if user_id in user:
                                    notSubscribed = False
                                    if anime["namePreferred"] not in failedAnimes:
                                        failedAnimes.append(anime["namePreferred"])
                                    break
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
        
        # logging.info(data)
        if (updated):
            # data.sort(key=orderByName, reverse=False)
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animes, failedAnimes

def unsubscribe_anime(id: int = None, chat_id: str = None, user_id: str = None):
    data = []
    animeName = ''
    updated = False
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                if anime["id"] == id:
                    animeName = anime["namePreferred"]
                    for watchlist in anime["watchlist"]:
                        if chat_id in watchlist:
                            newParty = []
                            for user in watchlist[chat_id]["party"]:
                                if user_id not in user:
                                    newParty.append(user)
                                else:
                                    updated = True
                            watchlist[chat_id]["party"] = newParty
                            break
                    break
        
        # logging.info(data)
        if (updated):
            # data.sort(key=orderByName, reverse=False)
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animeName

def update_anime(id: int = None, chat_id: str = None, episode: int = None):
    data = []
    animeName = ''
    updated = False
    animeEpisodes = 0
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                if anime["id"] == id:
                    animeName = anime["namePreferred"]
                    for watchlist in anime["watchlist"]:
                        if chat_id in watchlist:
                            animeEpisodes = anime["episodes"]
                            if animeEpisodes != None and animeEpisodes >= episode and episode > 0:
                                updated = True
                                watchlist[chat_id]["episode"] = episode
                                break
                    break

        # logging.info(data)
        if (updated):
            # data.sort(key=orderByName, reverse=False)
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return updated, animeName, animeEpisodes

def retrieve_anime_list(chat_id: str, pageNumber: int = 1):
    aniList = {}
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                for watchlist in anime["watchlist"]:
                    if chat_id in watchlist:
                        aniList.update({anime["id"]: anime["namePreferred"]})

    totalSize = math.ceil(len(aniList)/PAGE_SIZE)

    if math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, totalSize

def retrieve_updatable_anime_list(chat_id: str, pageNumber: int = 1):
    aniList = {}
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                for watchlist in anime["watchlist"]:
                    if chat_id in watchlist:
                        if anime["episodes"] != None:
                            aniList.update({anime["id"]: anime["namePreferred"]})

    totalSize = math.ceil(len(aniList)/PAGE_SIZE)

    if math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, totalSize

def retrieve_anime_list_detail(chat_id: str, pageNumber: int = 1, usePagination: bool = True):
    aniList = {}
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

    totalSize = math.ceil(len(aniList)/PAGE_SIZE) if usePagination else len(aniList)

    indexInformation = 'Index ' + str((pageNumber-1)*PAGE_SIZE) + '-' + str(pageNumber*PAGE_SIZE-1) + '\n\n'

    if usePagination and math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, len(aniList), totalSize, indexInformation

def retrieve_pingable_anime_list(chat_id: str, pageNumber: int = 1):
    aniList = {}
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                for watchlist in anime["watchlist"]:
                    if chat_id in watchlist:
                        if len(watchlist[chat_id]["party"]) > 0:
                            aniList.update({anime["id"]: anime["namePreferred"]})

    totalSize = math.ceil(len(aniList)/PAGE_SIZE)

    if math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, totalSize

def retrieve_subscribable_anime_list(chat_id: str, user_id: str, pageNumber: int = 1):
    aniList = {}
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                for watchlist in anime["watchlist"]:
                    if chat_id in watchlist:
                        notSubscribed = True
                        for user in watchlist[chat_id]["party"]:
                            if user_id in user:
                                notSubscribed = False
                        if notSubscribed:
                            aniList.update({anime["id"]: anime["namePreferred"]})

    totalSize = math.ceil(len(aniList)/PAGE_SIZE)

    if math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, totalSize

def retrieve_unsubscribable_anime_list(chat_id: str, user_id: str, pageNumber: int = 1):
    aniList = {}
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                for watchlist in anime["watchlist"]:
                    if chat_id in watchlist:
                        for user in watchlist[chat_id]["party"]:
                            if user_id in user:
                                aniList.update({anime["id"]: anime["namePreferred"]})

    totalSize = math.ceil(len(aniList)/PAGE_SIZE)

    if math.ceil(len(aniList)/PAGE_SIZE) > 1:
        listSlice = slice((pageNumber-1)*PAGE_SIZE,pageNumber*PAGE_SIZE)
        aniList = dict(list(aniList.items())[listSlice])

    return aniList, totalSize

def ping_anime(id: int = None, chat_id: str = None):
    data = []
    animeName = ''
    usernames = []
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                if anime["id"] == id:
                    animeName = anime["namePreferred"]
                    for watchlist in anime["watchlist"]:
                        if chat_id in watchlist:
                            for user in watchlist[chat_id]["party"]:
                                usernames.append(next(iter(user.values())))
                            break

    return usernames, animeName

def ping_multiples_animes(indexList: object, chat_id: str):
    count = 0
    usernames = []
    animes = []
    animesUnsubscribed = []
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                for watchlist in anime["watchlist"]:
                    if chat_id in watchlist:
                        if str(count) in indexList:
                            if (anime["namePreferred"] not in animes) and (anime["namePreferred"] not in animesUnsubscribed):
                                if len(watchlist[chat_id]["party"]) > 0:
                                    animes.append(anime["namePreferred"])
                                else:
                                    animesUnsubscribed.append(anime["namePreferred"])
                            for user in watchlist[chat_id]["party"]:
                                username = next(iter(user.values()))
                                if username not in usernames:
                                    usernames.append(username)
                        count += 1
                        break

    return usernames, animes, animesUnsubscribed

def who_to_ping(old: object, new: object):
    pingList = []

    if old["nextAiringEpisode"] != None:
        if (new["nextAiringEpisode"] == None
            or old["nextAiringEpisode"]["episode"] != new["nextAiringEpisode"]["episode"]
            or new["nextAiringEpisode"]["timeUntilAiring"] < 0):
            for watchlist in old["watchlist"]:
                pingList.append(next(iter(watchlist.keys())))

    return pingList

def update_all_anime():
    data = []
    pingList = []
    queryList = []
    with open(TRACKED_LIST_FILE, "r+") as file:
        file.seek(0,2)
        if (file.tell()):
            file.seek(0)
            data = json.load(file)
            for anime in data:
                queryList.append(anime["id"])

        updated = False
        for id in queryList:
            found = search_anime(id=id)
            for anime in data:
                if anime["id"] == found[0]["id"]:
                    if (anime["status"] != found[0]["status"] 
                        or found[0]["status"] == MEDIA_STATUS["RELEASING"]):
                        updated = True
                        episodePingList = who_to_ping(anime,found[0])
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

        # logging.info(data)
        if (updated):
            file.seek(0)
            file.write(json.dumps(data) + '\n')
            file.truncate()

    return pingList