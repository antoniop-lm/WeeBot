import weebot
import json
from Levenshtein import ratio
from weebot.anilist import search_anime

def check_if_tracked(id: int, search_term: str = None):
    found = []
    msg = ""
    is_tracked = False

    with open(weebot.tracked_list_file, "r") as f:
        j = json.load(f)
        for d in j:
            score = ratio(d["name"].lower(), search_term.lower())
            if d["id"] == id or score >= weebot.score_treshold:
                is_tracked = True

    if not is_tracked:
        found = search_anime(id=id, search_term=search_term)
        msg = "Found {} results.".format(len(found))
        #show the user the found animes
        #ask which one to track
        
    else:
        msg = "This anime is already tracked."

    return is_tracked, found, msg


def track_anime(id: int = None):
    found = search_anime(id=id)
    with open(weebot.tracked_list_file, "rw") as f:
        f.write(json.dumps(found) + '\n')
        