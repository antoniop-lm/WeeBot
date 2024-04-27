#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script start Anime Watch Party Handler Telegram Bot

:method handleSavedConversations(): NoReturn
:method sendEpisodesUpdates(chat: str, anime: str): NoReturn
:method handleEpisodesUpdates(): NoReturn
:method error(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn

Usage: main.py
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import EPISODE_CHECK_DELAY, DELETE_DELAY, CONVERSATION_CHECK_DELAY
from weebot import CONVERSATION_FILE, CONVERSATION_FUZZY_STR_FILE, CONVERSATION_PAGINATION_FILE
import weebot.settings
import logging, threading, pickle, datetime, asyncio
from time import sleep
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from weebot.database.update import update_all_anime
from weebot.telegram.callbacks import menu_callback
from weebot.telegram.commands import options_command, help_command, ping_command, subscribe_command, list_command
from weebot.telegram.handlers import handle_message

def handleSavedConversations():
    """
    Expire and save conversation handlers.

    Run as thread.
    """
    while True:
        now = datetime.datetime.now()
        listToDelete = []
        for option in weebot.settings.conversations:
            if weebot.settings.conversations.get(option).get('Timestamp') + datetime.timedelta(minutes=DELETE_DELAY) < now:
                listToDelete.append(option)

        for option in listToDelete:
            weebot.settings.conversations.pop(option)

        listToDelete = []
        for option in weebot.settings.conversationPagination:
            if weebot.settings.conversationPagination.get(option).get('Timestamp') + datetime.timedelta(minutes=DELETE_DELAY) < now:
                listToDelete.append(option)

        for option in listToDelete:
            weebot.settings.conversationPagination.pop(option)

        listToDelete = []
        for option in weebot.settings.conversationFuzzyStr:
            if weebot.settings.conversationFuzzyStr.get(option).get('Timestamp') + datetime.timedelta(minutes=DELETE_DELAY) < now:
                listToDelete.append(option)

        for option in listToDelete:
            weebot.settings.conversationFuzzyStr.pop(option)
        
        with open(CONVERSATION_FILE, 'wb') as f:
            pickle.dump(weebot.settings.conversations, f)
        with open(CONVERSATION_PAGINATION_FILE, 'wb') as f:
            pickle.dump(weebot.settings.conversationPagination, f)
        with open(CONVERSATION_FUZZY_STR_FILE, 'wb') as f:
            pickle.dump(weebot.settings.conversationFuzzyStr, f)

        sleep(CONVERSATION_CHECK_DELAY)

async def sendEpisodesUpdates(chat: str, anime: str):
    """Asynchronous method.

    Send information about new anime episode released to a telegram chat.
    
    :param chat: Telegram's chat id
    :param anime: Anime message content
    """
    app = Application.builder().token(weebot.settings.TOKEN).build()
    await app.bot.send_message(chat_id=chat,text=anime)

def handleEpisodesUpdates():
    """
    Send information about new anime episode released for each telegram chat and anime.
    """
    while True:
        pingList = update_all_anime()
        for ping in pingList:
            for chat in ping.keys():
                for anime in ping[chat]:
                    asyncio.run(sendEpisodesUpdates(chat=chat,anime=anime))

        sleep(EPISODE_CHECK_DELAY)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Log telegram execution errors.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    logging.info(f'Update ({update}) caused error {context.error}')

# Main
if __name__ == '__main__':
    # Initialize variables
    weebot.settings.init()
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO
    )
    logging.info('Starting bot...')
    app = Application.builder().token(weebot.settings.TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', options_command))
    app.add_handler(CommandHandler('options', options_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('ping', ping_command))
    app.add_handler(CommandHandler('subscribe', subscribe_command))
    app.add_handler(CommandHandler('list', list_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Callback
    app.add_handler(CallbackQueryHandler(menu_callback))

    # Update file and expire conversations
    t = threading.Thread(target=handleSavedConversations)
    t.daemon = True
    t.start()

    # Send new episodes updates
    t2 = threading.Thread(target=handleEpisodesUpdates)
    t2.daemon = True
    t2.start()

    # Polls the bot
    logging.info('Polling...')
    app.run_polling(poll_interval=3)
