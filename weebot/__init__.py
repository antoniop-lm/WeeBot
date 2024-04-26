from . import anilist,track
URL = "https://graphql.anilist.co"
ANIMEURL = "https://anilist.co/anime/"
SCORE_TRESHOLD = 0.7
TRACKED_LIST_FILE = r".\data\tracked_list.json"
PAGE_SIZE = 8
ANIME_RETURN_SIZE = 5
ANIME_DISTANCE = 5
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