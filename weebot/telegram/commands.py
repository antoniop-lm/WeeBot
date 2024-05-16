#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define Anime Watch Party Handler Telegram Bot command handlers

:method options_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method untrack_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method list_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import MESSAGE_TIMEOUT
import weebot.settings
from weebot.utils import createMenu, multiple_use_regex
import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from weebot.database.ping import ping_multiples_animes
from weebot.database.subscribe import subscribe_multiple_animes, unsubscribe_multiple_animes
from weebot.database.track import retrieve_anime_list_detail, untrack_multiple_animes
from weebot.telegram.handlers import handle_ping, handle_subscribe, handle_unsubscribe, handle_untrack

async def options_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /options command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    # Command context
    text = ''
    if 'start' in update.message.text:
        text = 'Hello! 🐶 Bondo likes you! 🥰 Hope we have fun! 😊\n'

    # Create menu
    buttons, text = createMenu(text)

    # Send message
    created_message = await context.bot.send_message(chat_id=chat_id, 
                                                     text=text,
                                                     reply_markup=InlineKeyboardMarkup(buttons),
                                                     read_timeout=MESSAGE_TIMEOUT,
                                                     write_timeout=MESSAGE_TIMEOUT,
                                                     connect_timeout=MESSAGE_TIMEOUT,
                                                     pool_timeout=MESSAGE_TIMEOUT)
    
    # Create conversation handler
    conversationValue = {
        "Value": str(chat_id)+str(user_id),
        "Timestamp": datetime.datetime.now(),
        "chat_id": str(chat_id),
        "user_id": str(user_id)
    }

    weebot.settings.conversations.update({str(created_message.message_id): conversationValue})
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /help command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id

    # Command context
    text = ''
    for option in weebot.settings.help:
        text += '*__'+option+':__* '+weebot.settings.help.get(option)+'\n\n'

    # Send message
    await context.bot.send_message(chat_id=chat_id, 
                                   text=text,
                                   parse_mode='MarkdownV2',
                                   read_timeout=MESSAGE_TIMEOUT,
                                   write_timeout=MESSAGE_TIMEOUT,
                                   connect_timeout=MESSAGE_TIMEOUT,
                                   pool_timeout=MESSAGE_TIMEOUT)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /ping command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id

    # Check args
    args = context.args[0].split(';') if len(context.args) > 0 else []
    if (len(args) == 0) or not multiple_use_regex(args):
        await handle_ping(update, context)
        return
    
    # Get list of people to ping
    usernames, animes, animesUnsubscribed = ping_multiples_animes(indexList=args, 
                                                                  chat_id=str(chat_id))

    # Command context
    text = ''
    if len(usernames) > 0:
        text = ' '.join(usernames)+' let\'s watch '+', '.join(animes)+'!'
    else:
        text = 'No friend watching '+', '.join(animesUnsubscribed)+'. Please try again! 🙏'

    # Send message
    await context.bot.send_message(chat_id=chat_id, 
                                   text=text, 
                                   read_timeout=MESSAGE_TIMEOUT, 
                                   write_timeout=MESSAGE_TIMEOUT,
                                   connect_timeout=MESSAGE_TIMEOUT,
                                   pool_timeout=MESSAGE_TIMEOUT)
    
async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /subscribe command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Check args
    args = context.args[0].split(';') if len(context.args) > 0 else []
    if (len(args) == 0) or not multiple_use_regex(args):
        await handle_subscribe(update, context)
        return

    # Get subscriptions
    updated, animes, failedAnimes = subscribe_multiple_animes(indexList=args, 
                                                              chat_id=str(chat_id),
                                                              user_id=str(user_id),
                                                              username=str(username))

    # Command context
    text = ''
    if len(failedAnimes) > 0:
        text += '@'+username+' is already subscribed to '+', '.join(failedAnimes)+'! 😅'
    if updated:
        text += '\n@'+username+' successfully subscribed to '+', '.join(animes)+'!'
    if not updated and len(failedAnimes) == 0:
        text = 'Something went wrong 😰, please try again! 🙏'
    
    # Send message
    await context.bot.send_message(chat_id=chat_id, 
                                   text=text, 
                                   read_timeout=MESSAGE_TIMEOUT, 
                                   write_timeout=MESSAGE_TIMEOUT,
                                   connect_timeout=MESSAGE_TIMEOUT,
                                   pool_timeout=MESSAGE_TIMEOUT)
    
async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /unsubscribe command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Check args
    args = context.args[0].split(';') if len(context.args) > 0 else []
    if (len(args) == 0) or not multiple_use_regex(args):
        await handle_unsubscribe(update, context)
        return

    # Get subscriptions
    updated, animes, failedAnimes = unsubscribe_multiple_animes(indexList=args, 
                                                                chat_id=str(chat_id),
                                                                user_id=str(user_id))

    # Command context
    text = ''
    if len(failedAnimes) > 0:
        text += '@'+username+' is not subscribed to '+', '.join(failedAnimes)+'! 😅'
    if updated:
        text += '\n@'+username+' successfully unsubscribed to '+', '.join(animes)+'!'
    if not updated and len(failedAnimes) == 0:
        text = 'Something went wrong 😰, please try again! 🙏'
    
    # Send message
    await context.bot.send_message(chat_id=chat_id, 
                                   text=text, 
                                   read_timeout=MESSAGE_TIMEOUT, 
                                   write_timeout=MESSAGE_TIMEOUT,
                                   connect_timeout=MESSAGE_TIMEOUT,
                                   pool_timeout=MESSAGE_TIMEOUT)
    
async def untrack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /untrack command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id

    # Check args
    args = context.args[0].split(';') if len(context.args) > 0 else []
    if (len(args) == 0) or not multiple_use_regex(args):
        await handle_untrack(update, context)
        return

    # Get subscriptions
    updated, animes = untrack_multiple_animes(indexList=args, 
                                              chat_id=str(chat_id))

    # Command context
    text = 'Something went wrong 😰, please try again! 🙏'
    if updated:
        text = 'Successfully untracked '+', '.join(animes)+'!'
    
    # Send message
    await context.bot.send_message(chat_id=chat_id, 
                                   text=text, 
                                   read_timeout=MESSAGE_TIMEOUT, 
                                   write_timeout=MESSAGE_TIMEOUT,
                                   connect_timeout=MESSAGE_TIMEOUT,
                                   pool_timeout=MESSAGE_TIMEOUT)

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /list command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id

    # Get list
    aniList, aniListSize, size, indexInformation = retrieve_anime_list_detail(chat_id=str(chat_id),
                                                                              usePagination=False)

    # Command context
    text = 'These are the Animes being tracked:\n\n'
    count = 0
    for anime in aniList:
        text += str(count)+': '+anime+' '+aniList[anime][1:]+'\n'
        count += 1

    # Send message
    await context.bot.send_message(chat_id=chat_id, 
                                   text=text,
                                   parse_mode='HTML',
                                   disable_web_page_preview=True,
                                   read_timeout=MESSAGE_TIMEOUT,
                                   write_timeout=MESSAGE_TIMEOUT,
                                   connect_timeout=MESSAGE_TIMEOUT,
                                   pool_timeout=MESSAGE_TIMEOUT)
