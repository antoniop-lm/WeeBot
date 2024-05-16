#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script start Anime Watch Party Handler Telegram Bot

:method handleSavedConversations(ContextTypes.DEFAULT_TYPE): NoReturn
:method handleEpisodesUpdates(ContextTypes.DEFAULT_TYPE): NoReturn
:method error(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn

Usage: main.py
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import EPISODE_CHECK_DELAY, DELETE_DELAY, CONVERSATION_CHECK_DELAY, MESSAGE_TIMEOUT
from weebot import CONVERSATION_FILE, CONVERSATION_FUZZY_STR_FILE, CONVERSATION_PAGINATION_FILE
import weebot.settings
import logging, pickle, datetime
from time import sleep
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, JobQueue
from weebot.database.update import update_all_anime
from weebot.telegram.callbacks import menu_callback
from weebot.telegram.commands import options_command, help_command, ping_command, subscribe_command, list_command, unsubscribe_command, untrack_command
from weebot.telegram.handlers import handle_message

async def handleSavedConversations(context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Expire and save conversation handlers.
    Run as thread.

    :param context: Telegram's context
    """
    now = datetime.datetime.now()
    listToDelete = []
    for option in weebot.settings.conversations:
        if weebot.settings.conversations.get(option).get('Timestamp') + datetime.timedelta(minutes=DELETE_DELAY) < now:
            if weebot.settings.conversations.get(option).get('chat_id') != None:
                await context.bot.edit_message_text(chat_id=weebot.settings.conversations.get(option).get('chat_id'), 
                                                    message_id=option,
                                                    text='This message expired. 😰', 
                                                    read_timeout=MESSAGE_TIMEOUT, 
                                                    write_timeout=MESSAGE_TIMEOUT,
                                                    connect_timeout=MESSAGE_TIMEOUT,
                                                    pool_timeout=MESSAGE_TIMEOUT)
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

async def handleEpisodesUpdates(context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Send information about new anime episode released for each telegram chat and anime.
    Run as thread.

    :param context: Telegram's context
    """
    pingList = update_all_anime()
    for ping in pingList:
        for chat in ping.keys():
            for anime in ping[chat]:
                await context.bot.send_message(chat_id=chat,
                                               text=anime,
                                               read_timeout=MESSAGE_TIMEOUT,
                                               write_timeout=MESSAGE_TIMEOUT,
                                               connect_timeout=MESSAGE_TIMEOUT,
                                               pool_timeout=MESSAGE_TIMEOUT)

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
    app.add_handler(CommandHandler('unsubscribe', unsubscribe_command))
    app.add_handler(CommandHandler('untrack', untrack_command))
    app.add_handler(CommandHandler('list', list_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Callback
    app.add_handler(CallbackQueryHandler(menu_callback))

    # Update file and expire conversations
    conversationBackup_job_queue: JobQueue = app.job_queue
    conversationBackup_job_queue.run_repeating(handleSavedConversations, CONVERSATION_CHECK_DELAY)

    # Send new episodes updates
    episodeUpdate_job_queue: JobQueue = app.job_queue
    episodeUpdate_job_queue.run_repeating(handleEpisodesUpdates, EPISODE_CHECK_DELAY)

    # Polls the bot
    logging.info('Polling...')
    app.run_polling(poll_interval=3, 
                    close_loop=False,
                    read_timeout=MESSAGE_TIMEOUT, 
                    write_timeout=MESSAGE_TIMEOUT,
                    connect_timeout=MESSAGE_TIMEOUT,
                    pool_timeout=MESSAGE_TIMEOUT)
