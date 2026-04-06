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
:method seen_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method update_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method list_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method catch_command(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import MESSAGE_TIMEOUT
import weebot.settings
from weebot.utils import createMenu, multiple_use_regex, use_regex
import logging, datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from weebot.database.ping import ping_multiples_animes
from weebot.database.update import update_anime, update_multiple_animes
from weebot.database.subscribe import subscribe_multiple_animes, unsubscribe_multiple_animes
from weebot.database.track import retrieve_anime_list_detail, untrack_multiple_animes
from weebot.telegram.handlers import handle_ping, handle_subscribe, handle_unsubscribe, handle_untrack, handle_update

async def options_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /options command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    is_edited = True if ((update.message != None) and (update.message.edit_date != None)) else False
    if is_edited:
        return

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
    is_edited = True if ((update.message != None) and (update.message.edit_date != None)) else False
    if is_edited:
        return

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
    is_edited = True if ((update.message != None) and (update.message.edit_date != None)) else False
    if is_edited:
        return

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
    is_edited = True if ((update.message != None) and (update.message.edit_date != None)) else False
    if is_edited:
        return

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
    is_edited = True if ((update.message != None) and (update.message.edit_date != None)) else False
    if is_edited:
        return

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
    is_edited = True if ((update.message != None) and (update.message.edit_date != None)) else False
    if is_edited:
        return

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
    
    if updated:
        await list_command(update,context)
    
async def seen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /seen command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    is_edited = True if ((update.message != None) and (update.message.edit_date != None)) else False
    if is_edited:
        return

    # Check args
    args = context.args[0].split(';') if len(context.args) > 0 else []
    if (len(args) == 0) or not multiple_use_regex(args):
        await handle_update(update, context)
        return
    
    # Get list of people to update
    updated, animes, animeEpisodes = update_multiple_animes(indexList=args, 
                                                            chat_id=str(chat_id))

    # Command context
    text = 'Something went wrong 😰, please try again! 🙏'
    if updated:
        text = 'Successfully updated '+', '.join(animes)+'!'

    # Send message
    await context.bot.send_message(chat_id=chat_id, 
                                   text=text, 
                                   read_timeout=MESSAGE_TIMEOUT, 
                                   write_timeout=MESSAGE_TIMEOUT,
                                   connect_timeout=MESSAGE_TIMEOUT,
                                   pool_timeout=MESSAGE_TIMEOUT)
    
async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /update command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    is_edited = True if ((update.message != None) and (update.message.edit_date != None)) else False
    if is_edited:
        return

    # Check args
    args = context.args[0].split(':') if len(context.args) > 0 else []
    if (len(args) == 0) or not multiple_use_regex(args):
        await handle_update(update, context)
        return
    
    anime_id = args[0]
    episode = args[1]
    
    # Command context
    text = 'Something went wrong 😰, please try again! 🙏'
    if use_regex(episode):
        # Get list of people to update
        updated, animes, animeEpisodes = update_multiple_animes(indexList=[anime_id], 
                                                                chat_id=str(chat_id),
                                                                episode=int(episode))
        # Set response
        text = animes[0]+' has only '+str(animeEpisodes)+' episodes. Please send me a lower number!'
        if animeEpisodes == 0:
            text = animes[0]+' is not being tracked by you!'
        if updated:
            text = 'Successfully updated '+animes[0]+'! Episode '+episode+' of '+str(animeEpisodes)+'.'
    
    else:
        text = 'That\'s not a valid episode! 😰 Please send me only the episode number.'

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
    is_edited = True if ((update.message != None) and (update.message.edit_date != None)) else False
    if is_edited:
        return

    # Get list
    aniList, aniListSize, size, indexInformation = retrieve_anime_list_detail(chat_id=str(chat_id),
                                                                              usePagination=False)

    # Command context
    text = 'No Anime is being tracked at the moment.'
    count = 0
    if len(aniList) > 0:
        text = 'These are the Animes being tracked:\n\n'
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

async def catch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot /catch command.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    is_edited = True if ((update.message != None) and (update.message.edit_date != None)) else False
    if is_edited:
        return

    # Command context
    text = 'WOOF WOOF! Here is the ⚾️! I\'m having a good time with you 🥰!'

    # Send message
    await context.bot.send_message(chat_id=chat_id, 
                                   text=text,
                                   parse_mode='HTML',
                                   disable_web_page_preview=True,
                                   read_timeout=MESSAGE_TIMEOUT,
                                   write_timeout=MESSAGE_TIMEOUT,
                                   connect_timeout=MESSAGE_TIMEOUT,
                                   pool_timeout=MESSAGE_TIMEOUT)