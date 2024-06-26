#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define Anime Watch Party Handler Telegram Bot callback handlers

:method menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

import weebot.settings
import logging, datetime
from telegram import Update
from telegram.ext import  ContextTypes
from weebot.telegram.handlers import handle_list, handle_ping, handle_subscribe, handle_track, handle_unsubscribe, handle_untrack, handle_update

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot menus callback.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # logging.info('Conversation: %s',weebot.settings.conversations)
    # logging.info('conversationPagination: %s',weebot.settings.conversationPagination)
    # logging.info('conversationFuzzyStr: %s',weebot.settings.conversationFuzzyStr)

    # Get data
    chat_id = update.effective_chat.id
    user_id = update.callback_query.from_user.id
    message_id = update.callback_query.message.message_id
    option = update.callback_query.data

    # Set callback data
    commandsToIgnore = ['Substracker']
    result = 'Success'
    conversationValue = {
        "Value": str(chat_id)+str(user_id),
        "Timestamp": datetime.datetime.now(),
        "chat_id": str(chat_id),
        "user_id": str(user_id)
    }

    # Check if the conversation is being tracked
    if not (str(message_id) in weebot.settings.conversations):
        await update.callback_query.answer('This message expired. 😰 Could you please send /options again? 🥺')
        return
    # Check if is the same user that started the conversation
    if ((weebot.settings.conversations.get(str(message_id)).get('Value') != conversationValue.get('Value')) 
        and not [i for i in commandsToIgnore if i in option]):
        await update.callback_query.answer('Bondo is helping other person, please make your own request or I will be confused 😵')
        return
    
    # Update last time this conversation got a follow up
    weebot.settings.conversations.update({str(message_id): conversationValue})

    # Handle options
    match option:
        case str(x) if 'List' in x:
            await handle_list(update, context)
        case str(x) if 'Update' in x:
            await handle_update(update, context)
        case str(x) if 'Track' in x:
            await handle_track(update, context)
        case str(x) if 'Untrack' in x:
            await handle_untrack(update, context)
        case str(x) if 'Subscribe' in x:
            await handle_subscribe(update, context)
        case str(x) if 'Unsubscribe' in x:
            await handle_unsubscribe(update, context)
        case str(x) if 'Ping' in x:
            await handle_ping(update, context)
        case _:
            result = 'Error'
            weebot.settings.conversations.pop(str(message_id))
    
    await update.callback_query.answer(result)
