#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define Anime Watch Party Handler Telegram Bot menu option handlers

:method handle_list(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method handle_track(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method handle_untrack(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method handle_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method handle_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method handle_ping(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method handle_response(text: str, update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
:method handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): NoReturn
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import ANIMEURL, MESSAGE_TIMEOUT
import weebot.settings
from weebot.utils import use_regex, createMenu, optionHandler
import logging, datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from weebot.database.subscribe import subscribe_anime
from weebot.database.track import track_anime, check_if_tracked, retrieve_anime_list_detail
from weebot.database.update import update_anime

async def handle_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot List option.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    message_id = update.callback_query.message.message_id
    optionClicked = update.callback_query.data
    text = 'These are the Animes being tracked:\n'
    pageNumber = (weebot.settings.conversationPagination.get(str(message_id)).get('Value') 
                  if str(message_id) in weebot.settings.conversationPagination 
                  else 1)
    buttons = []
    row = []

    # Choose what to do
    match optionClicked:
        # Update page number based on option
        case str(x) if 'next' in x:
            pageNumber += 1
        case str(x) if 'prev' in x:
            pageNumber -= 1

        case _: 
            # Remove conversation pagination handler
            if str(message_id) in weebot.settings.conversationPagination:
                weebot.settings.conversationPagination.pop(str(message_id))

            # Return one screen
            if 'back' in optionClicked:
                buttons, text = createMenu('')
                await context.bot.edit_message_text(chat_id=chat_id, 
                                                    message_id=message_id,
                                                    text=text,
                                                    reply_markup=InlineKeyboardMarkup(buttons),
                                                    read_timeout=MESSAGE_TIMEOUT,
                                                    write_timeout=MESSAGE_TIMEOUT)
                return

    # Get anime list and set message
    aniList, aniListSize, size, indexInformation = retrieve_anime_list_detail(chat_id=str(chat_id),
                                                                              pageNumber=pageNumber)
    text += indexInformation

    # Create menu
    for page in weebot.settings.pagination:
        if str(page) == 'prev':
            if pageNumber > 1:
                row.append(InlineKeyboardButton(weebot.settings.pagination.get(page), callback_data=page+' List'))
                text += '\nClick on ◀ to see the previous page.\n'
            continue

        if str(page) == 'next':
            if pageNumber < size:
                row.append(InlineKeyboardButton(weebot.settings.pagination.get(page), callback_data=page+' List'))
                text += '\nClick on ▶ to see the next page.\n'
            continue

        if int(page) < aniListSize:
            text += str(list(aniList)[int(page)])+': '+list(aniList.values())[int(page)]+'\n'

    # Set back to option menu
    buttons.append(row)
    back = [InlineKeyboardButton('🔙', callback_data='back List')]
    buttons.append(back)
    text += '\nClick on 🔙 to return to the options.\n\n'

    # Update last time this conversation got a follow up
    conversationPaginationValue = {
        "Value": pageNumber,
        "Timestamp": datetime.datetime.now()
    }
    weebot.settings.conversationPagination.update({str(message_id): conversationPaginationValue})
    await context.bot.edit_message_text(chat_id=chat_id, 
                                        message_id=message_id,
                                        text=text,
                                        reply_markup=InlineKeyboardMarkup(buttons),
                                        parse_mode='HTML',
                                        disable_web_page_preview=True,
                                        read_timeout=MESSAGE_TIMEOUT,
                                        write_timeout=MESSAGE_TIMEOUT)

async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot Update option.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Set data
    baseText = 'Which Anime you want to update:\n\n'
    confirmationText = 'Are you sure you want to update '
    successfulText = 'Please send me only the episode number.'

    # Handle update flow
    await optionHandler('Update', update, context, baseText, confirmationText, successfulText)

async def handle_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot Track option.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    message_id = update.callback_query.message.message_id
    optionClicked = update.callback_query.data
    text = 'Please, send me the Anime name you want to track:\n\n'

    # Choose what to do
    match optionClicked:
        case str(x) if 'Substracker' in x:
            index = x.split()[1]
            updated, animeName = subscribe_anime(id=int(index),
                                                 chat_id=str(chat_id),
                                                 user_id=str(user_id),
                                                 username=str(username))
            text = '@'+username+' is already subscribed to '+animeName+'! 😅'
            if (updated):
                text = '@'+username+' successfully subscribed to '+animeName+'! 😍'
            await context.bot.send_message(chat_id=chat_id, 
                                           text=text,
                                           read_timeout=MESSAGE_TIMEOUT,
                                           write_timeout=MESSAGE_TIMEOUT)
            return
        
        case str(x) if x.replace(' Track','').isnumeric():
            # Get data
            index = x.split()[0]
            found = track_anime(id=int(index),chat_id=str(chat_id))

            # Send message
            text = 'Successfully tracked '+found[0]["namePreferred"]+'!'
            buttons = []
            subscribe = [InlineKeyboardButton(weebot.settings.menu.get('Subscribe')+' Subscribe', callback_data='Substracker '+index+' Track')]
            buttons.append(subscribe)
            await context.bot.edit_message_text(chat_id=chat_id, 
                                                message_id=message_id,
                                                text=text,
                                                reply_markup=InlineKeyboardMarkup(buttons),
                                                read_timeout=MESSAGE_TIMEOUT,
                                                write_timeout=MESSAGE_TIMEOUT)
            
            # Remove conversation fuzzy handler
            conversationFuzzyStrValueId = str(chat_id)+str(user_id)
            weebot.settings.conversationFuzzyStr.pop(conversationFuzzyStrValueId)
            return
        
        case _:
            # Return one screen
            if not('no' in optionClicked) and str(message_id) in weebot.settings.conversations:
                weebot.settings.conversations.pop(str(message_id))

    # Send message
    await context.bot.edit_message_text(chat_id=chat_id, 
                                        message_id=message_id,
                                        text=text,
                                        read_timeout=MESSAGE_TIMEOUT,
                                        write_timeout=MESSAGE_TIMEOUT)
    
    # Update last time this conversation fuzzy got a follow up
    conversationFuzzyStrValue = {
        "Value": 'Track',
        "Timestamp": datetime.datetime.now(),
        "Message": str(message_id)
    }
    conversationFuzzyStrValueId = str(chat_id)+str(user_id)
    weebot.settings.conversationFuzzyStr.update({conversationFuzzyStrValueId: conversationFuzzyStrValue})

async def handle_untrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot Untrack option.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Set data
    baseText = 'Which Anime you want to untrack:\n\n'
    confirmationText = 'Are you sure you want to untrack '
    successfulText = 'Successfully untracked '

    # Handle untrack flow
    await optionHandler('Untrack', update, context, baseText, confirmationText, successfulText)
    
async def handle_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot Subscribe option.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Set data
    baseText = 'Which Anime you want to subscribe:\n\n'
    confirmationText = 'Are you sure you want to subscribe to '
    successfulText = ' successfully subscribed to '

    # Handle subscribe flow
    await optionHandler('Subscribe', update, context, baseText, confirmationText, successfulText)
    
async def handle_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot Unsubscribe option.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    baseText = 'Which Anime you want to unsubscribe:\n\n'
    confirmationText = 'Are you sure you want to unsubscribe from '
    successfulText = ' successfully unsubscribed from '

    # Handle unsubscribe flow
    await optionHandler('Unsubscribe', update, context, baseText, confirmationText, successfulText)
    
async def handle_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot Ping option.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Set data
    baseText = 'Which Anime you want to ping:\n\n'
    confirmationText = 'Are you sure you want to ping viewers from '
    successfulText = ' let\'s watch '

    # Handle ping flow
    await optionHandler('Ping', update, context, baseText, confirmationText, successfulText)

async def handle_response(text: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle Anime Watch Party Handler Telegram Bot user input.
    
    :param text: User's message
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    # Process message
    processed: str = text.lower()
    response = 'Can you throw me the ⚾ again? I didn\'t find it. 😔'
    conversationFuzzyStrValueId = str(chat_id)+str(user_id)

    # Handle message
    if conversationFuzzyStrValueId in weebot.settings.conversationFuzzyStr:
        # Set data
        aniList = {}
        buttons = []
        row = []
        currentFuzzyStr = weebot.settings.conversationFuzzyStr.get(conversationFuzzyStrValueId).get('Value')

        # Choose what to do
        if 'Track' in currentFuzzyStr:
            # Check if anime is already tracked
            is_tracked, found, msg = check_if_tracked(search_term=processed,
                                                      chat_id=str(chat_id))

            # Track
            if(not is_tracked):
                # Set response
                if len(found) == 0:
                    response = 'I couldn\'t find any anime with that name. 😭\nPlease, click on ❌ and try to send me another name!\n'
                else:
                    response = 'I found these Animes. 😋 Is it any of these? 🤔\n\n'
                for anime in found:
                    aniList.update({anime["id"]: anime["namePreferred"]})

                # Create menu
                count = 0
                for anime in aniList:
                    row.append(InlineKeyboardButton(weebot.settings.pagination.get(str(count)), callback_data=str(anime)+' Track'))
                    response += weebot.settings.pagination.get(str(count))+': <a href="'+ANIMEURL+str(anime)+'/">'+aniList.get(anime)+'</a>\n'
                    count += 1
                buttons.append(row)
                no = [InlineKeyboardButton('❌', callback_data='no Track')]
                buttons.append(no)

                # Send message
                created_message = await context.bot.send_message(chat_id=chat_id, 
                                                                 text=response,
                                                                 reply_markup=InlineKeyboardMarkup(buttons),
                                                                 parse_mode='HTML',
                                                                 disable_web_page_preview=True,
                                                                 read_timeout=MESSAGE_TIMEOUT,
                                                                 write_timeout=MESSAGE_TIMEOUT)
                
                # Update last time this conversation got a follow up
                conversationValue = {
                    "Value": conversationFuzzyStrValueId,
                    "Timestamp": datetime.datetime.now()
                }
                weebot.settings.conversations.update({str(created_message.message_id): conversationValue})
            
            # Ignore
            else:
                response = found["namePreferred"] + ' is already being tracked!\nI will ping you when new episodes are released! 😋'
                # Send message
                await context.bot.send_message(chat_id=chat_id,
                                               text=response, 
                                               read_timeout=MESSAGE_TIMEOUT, 
                                               write_timeout=MESSAGE_TIMEOUT)
                weebot.settings.conversationFuzzyStr.pop(conversationFuzzyStrValueId)
            
            return
        
        elif 'Update' in currentFuzzyStr:
            # Check if is a valid episode
            if use_regex(processed):
                # Get data
                index = str(currentFuzzyStr).replace('Update ','')
                updated, animeName, animeEpisodes = update_anime(id=int(index),
                                                                 chat_id=str(chat_id),
                                                                 episode=int(processed))

                # Set response
                response = animeName+' has only '+str(animeEpisodes)+' episodes. Please send me a lower number!'
                if animeEpisodes == 0:
                    response = animeName+' is not being tracked by you!'
                if updated:
                    response = 'Successfully updated '+animeName+'! Episode '+processed+' of '+str(animeEpisodes)+'.'
                
                # Remove conversation fuzzy handler
                weebot.settings.conversationFuzzyStr.pop(conversationFuzzyStrValueId)
            
            else:
                response = 'That\'s not a valid episode! 😰 Please send me only the episode number.'

    # Set basic responses
    else:
        if 'hello' in processed:
            response = 'Haaai! 😁'
        if 'how are you' in processed:
            response = 'Better now! 🥰'
    
    # Send message
    await context.bot.send_message(chat_id=chat_id,
                                   text=response,
                                   read_timeout=MESSAGE_TIMEOUT,
                                   write_timeout=MESSAGE_TIMEOUT)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronous method.

    Handle user input based on context.
    
    :param update: Telegram's incoming update
    :param context: Telegram's context
    """
    # Get data
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    message_id = update.message.reply_to_message.message_id if update.message.reply_to_message else ''
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # logging.info(f'User (%s) in %s: "%s"', update.message.chat.id, message_type, text)

    # Message was sent in a group
    if message_type == 'group':
        # Check if a conversation fuzzy str related to the message replied is in progress, otherwise ignore
        conversationFuzzyStrValueId = str(chat_id)+str(user_id)
        if conversationFuzzyStrValueId in weebot.settings.conversationFuzzyStr:
            if weebot.settings.conversationFuzzyStr.get(conversationFuzzyStrValueId).get("Message") != str(message_id):
                return
        else:
            return
        
        # Remove bot username from message if needed
        new_text: str = text
        if weebot.settings.BOT_USERNAME in text:
            new_text: str = text.replace(weebot.settings.BOT_USERNAME,'').strip()
        
        await handle_response(new_text, update, context)

    # Message was sent in a private conversation
    else:
        await handle_response(text, update, context)
