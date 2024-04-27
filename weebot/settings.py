#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define global variables for Anime Watch Party Handler Telegram Bot

:method init(): NoReturn
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

import pickle, json
from typing import Final
from weebot import CONVERSATION_FILE, CONVERSATION_FUZZY_STR_FILE, CONVERSATION_PAGINATION_FILE

def init():
    """
    Set all global variables for Anime Watch Party Handler Telegram Bot.
    """
    global TOKEN, BOT_USERNAME
    global conversations, conversationPagination, conversationFuzzyStr
    global menu, help, pagination, confirmation

    # Configuration
    creds = json.load(open('credentials.json'))
    TOKEN = creds['TELEGRAM_TOKEN']
    BOT_USERNAME = creds['BOT_USERNAME']

    # Files
    with open(CONVERSATION_FILE, 'rb') as f:
        conversations = pickle.load(f)
    with open(CONVERSATION_PAGINATION_FILE, 'rb') as f:
        conversationPagination = pickle.load(f)
    with open(CONVERSATION_FUZZY_STR_FILE, 'rb') as f:
        conversationFuzzyStr = pickle.load(f)

    # Menu
    menu = {
        "List": "📃",
        "Update": "🔄",
        "Track": "✅",
        "Untrack": "❌",
        "Subscribe": "🔼",
        "Unsubscribe" : "🔽",
        "Ping": "🚨"
    }
    help = {
        "List": "List all current animes being watched and their progress",
        "Update": "Set which was the last episode watched for an anime",
        "Track" : "Choose an anime to track new episodes",
        "Untrack": "Stop anime new episodes updates",
        "Subscribe": "Subscribe to receive updates when a watch party is happening",
        "Unsubscribe" : "Unsubscribe to stop receiving anime pings",
        "Ping": "Ping all subscribed persons to an anime",
    }
    pagination = {
        "0": "0️⃣",
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
        "prev": "◀",
        "next": "▶"
    }
    confirmation = {
        "yes": "👍",
        "no": "👎"
    }