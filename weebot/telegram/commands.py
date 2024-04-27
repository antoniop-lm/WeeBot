#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define Anime Watch Party Handler Telegram Bot command handlers

:method options_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method list_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

import weebot.settings
from weebot.utils import createMenu, multiple_use_regex
import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from weebot.database.ping import ping_multiples_animes
from weebot.database.subscribe import subscribe_multiple_animes
from weebot.database.track import retrieve_anime_list_detail

async def options_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /options command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Command context
    text = ''
    if 'start' in update.message.text:
        text = 'Hello! 🐶 Bondo likes you! 🥰 Hope we have fun! 😊\n'

    # Create menu
    buttons, text = createMenu(text)

    # Send message
    created_message = await context.bot.send_message(chat_id=update.effective_chat.id, 
                                                     text=text,
                                                     reply_markup=InlineKeyboardMarkup(buttons))
    
    # Create conversation handler
    conversationValue = {
        "Value": str(update.effective_chat.id)+str(update.message.from_user.id),
        "Timestamp": datetime.datetime.now()
    }

    weebot.settings.conversations.update({str(created_message.message_id): conversationValue})
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /help command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Command context
    text = ''
    for option in weebot.settings.help:
        text += '*__'+option+':__* '+weebot.settings.help.get(option)+'\n\n'

    # Send message
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=text,
                                   parse_mode='MarkdownV2')

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /ping command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Check args
    args = context.args[0].split(';') if len(context.args) > 0 else []
    if (len(args) == 0) or not multiple_use_regex(args):
        text = 'These are not valid animes! 😰 Please send me only the index number separated by \';\'.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return
    
    # Get list of people to ping
    usernames, animes, animesUnsubscribed = ping_multiples_animes(indexList=args, chat_id=str(update.effective_chat.id))

    # Command context
    text = ''
    if len(usernames) > 0:
        text = ' '.join(usernames)+' let\'s watch '+', '.join(animes)+'!'
    else:
        text = 'No friend watching '+', '.join(animesUnsubscribed)+'. Please try again! 🙏'

    # Send message
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /subscribe command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Check args
    args = context.args[0].split(';') if len(context.args) > 0 else []
    if (len(args) == 0) or not multiple_use_regex(args):
        text = 'These are not valid animes! 😰 Please send me only the index number separated by \';\'.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return

    # Get subscriptions
    updated, animes, failedAnimes = subscribe_multiple_animes(indexList=args, chat_id=str(update.effective_chat.id),
                                                              user_id=str(update.message.from_user.id), username=str(update.message.from_user.username))

    # Command context
    text = ''
    if len(failedAnimes) > 0:
        text += '@'+update.message.from_user.username+' is already subscribed to '+', '.join(failedAnimes)+'! 😅'
    if updated:
        text += '\n@'+update.message.from_user.username+' successfully subscribed to '+', '.join(animes)+'!'
    if not updated and len(failedAnimes) == 0:
        text = 'Something went wrong 😰, please try again! 🙏'
    
    # Send message
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /list command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get list
    aniList, aniListSize, size, indexInformation = retrieve_anime_list_detail(chat_id=str(update.effective_chat.id),usePagination=False)

    # Command context
    text = 'These are the Animes being tracked:\n\n'
    count = 0
    for anime in aniList:
        text += str(count)+': '+anime+' '+aniList[anime][1:]+'\n'
        count += 1

    # Send message
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=text,
                                   parse_mode='HTML',
                                   disable_web_page_preview=True)
