from . import integrations, database, telegram
import os
URL = "https://graphql.anilist.co"
ANIMEURL = "https://anilist.co/anime/"
SCORE_TRESHOLD = 0.7
TRACKED_LIST_FILE = os.path.join('.','data','tracked_list.json')
CONVERSATION_FILE = os.path.join('.','data','conversations.pkl')
CONVERSATION_PAGINATION_FILE = os.path.join('.','data','conversationPagination.pkl')
CONVERSATION_FUZZY_STR_FILE = os.path.join('.','data','conversationFuzzyStr.pkl')
PAGE_SIZE = 8
ANIME_RETURN_SIZE = 5
ANIME_DISTANCE = 5
MAX_LINE_SIZE = 8
CONVERSATION_CHECK_DELAY = 60
DELETE_DELAY = 30
EPISODE_CHECK_DELAY = 900
MESSAGE_TIMEOUT = 30
MEDIA_STATUS = {
    "FINISHED"          : "FINISHED",
    "RELEASING"         : "RELEASING",
    "NOT_YET_RELEASED"  : "NOT_YET_RELEASED",
    "CANCELLED"         : "CANCELLED",
    "HIATUS"            : "HIATUS"
}
MEDIA_FORMAT = {
    "TV"        : "TV",
    "TV_SHORT"  : "TV_SHORT",
    "MOVIE"     : "MOVIE",
    "SPECIAL"   : "SPECIAL",
    "OVA"       : "OVA",
    "ONA"       : "ONA",
    "MUSIC"     : "MUSIC",
    "MANGA"     : "MANGA",
    "NOVEL"     : "NOVEL",
    "ONE_SHOT"  : "ONE_SHOT"
}
MEDIA_TYPE = {
    "ANIME"     : "ANIME",
    "MANGA"     : "MANGA"
}