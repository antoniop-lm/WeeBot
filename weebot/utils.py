#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""\
This script define utility methods for Anime Watch Party Handler Telegram Bot

:method orderByName(e: object): Any
:method multiple_use_regex(list: object): bool
:method use_regex(input_text: str): (Match[str] | None)
:method createMenu(text: str): tuple[list, str]
:method createPagination(aniList: dict, text: str, size: int, pageNumber: int, operation: str): tuple[list, str]
:method optionHandler(operation: str, update: Update, context: ContextTypes.DEFAULT_TYPE, baseText: str, confirmationText: str, successfulText: str): NoReturn
"""

__author__ = "Antônio Mazzarolo and Matheus Soares"
__credits__ = ["Antônio Mazzarolo", "Matheus Soares"]
__version__ = "1.0.0"
__maintainer__ = "Antônio Mazzarolo"
__email__ = "aplmazzarolo@gmail.com"

from weebot import ANIMEURL, MAX_LINE_SIZE
import weebot.settings
import logging, re, datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from weebot.database.ping import ping_anime, retrieve_pingable_anime_list
from weebot.database.subscribe import subscribe_anime, unsubscribe_anime, retrieve_subscribable_anime_list, retrieve_unsubscribable_anime_list
from weebot.database.track import untrack_anime, retrieve_anime_list
from weebot.database.update import retrieve_updatable_anime_list

def orderByName(e: object):
    """
    Select list key as preferred name to help sort.

    :param e: List to select key
    :return: Key to sort
    """
    return e["namePreferred"]

def multiple_use_regex(list: object):
    """
    Check if all string in list are numbers.

    :param list: List to check
    :return: False if any is not a number, True otherwise
    """
    for text in list:
        if not use_regex(text):
            return False
    return True

def use_regex(input_text: str):
    """
    Check if string is a number by regex.

    :param input_text: Input text to check
    :return: None if is not a number, Match str otherwise
    """
    pattern = re.compile(r"^[0-9]+$", re.IGNORECASE)
    return pattern.match(input_text)

def createMenu(text: str):
    """
    Create default Anime Watch Party Handler menu.

    :param text: Telegram message text to change
    :return: List of telegram message buttons and Telegram message text
    """
    # Set menu data
    text += 'What should I sniff for you? 👃'
    buttons = []
    row = []

    # Iterate over menu options and set option details
    for option in weebot.settings.menu:
        if len(row) == 2:
            buttons.append(row)
            row = []
        row.append(InlineKeyboardButton(weebot.settings.menu.get(option)+' '+option, callback_data=option))
    buttons.append(row)

    return buttons, text

def createPagination(aniList: dict, text: str, size: int, pageNumber: int, operation: str):
    """
    Create pagination menu for Anime Watch Party Handler.

    :param aniList: Dict containing anime list
    :param text: Telegram message text
    :param size: Records per page for pagination
    :param pageNumber: Current page for pagination
    :param operation: Selected menu option
    :return: List of telegram message buttons and Telegram message text
    """
    # Set pagination data
    aniListSize = len(aniList)
    buttons = []
    row = []
    count = 0

    # Check if anime list exists
    if aniListSize > 0:
        # Iterate over anime list, set anime details and create pagination when necessary
        for page in weebot.settings.pagination:
            if count >= MAX_LINE_SIZE:
                count = 0
                buttons.append(row)
                row = []
            if str(page) == 'prev':
                if pageNumber > 1:
                    row.append(InlineKeyboardButton(weebot.settings.pagination.get(page), callback_data=page+' '+operation))
                    text += '\nClick on ◀ to see the previous page.\n'
                continue
            if str(page) == 'next':
                if pageNumber < size:
                    row.append(InlineKeyboardButton(weebot.settings.pagination.get(page), callback_data=page+' '+operation))
                    text += '\nClick on ▶ to see the next page.\n'
                continue
            if int(page) < aniListSize:
                row.append(InlineKeyboardButton(weebot.settings.pagination.get(page), callback_data=str(list(aniList)[int(page)])+' '+operation))
                text += weebot.settings.pagination.get(page)+': <a href="'+ANIMEURL+str(list(aniList)[int(page)])+'/">'+list(aniList.values())[int(page)]+'</a>\n'
            count += 1
        buttons.append(row)
    else:
        text = 'I couldn\'t find any anime for this option. 😭'
    
    # Set back to option menu
    back = [InlineKeyboardButton('🔙', callback_data='back '+operation)]
    buttons.append(back)
    text += '\nClick on 🔙 to return to the options.\n\n'
    
    return buttons, text

async def optionHandler(operation: str, update: Update, context: ContextTypes.DEFAULT_TYPE, baseText: str, confirmationText: str, successfulText: str):
    """
    Handle menu option selection for Anime Watch Party Handler.

    :param operation: Selected menu option
    :param update: Telegram's incoming update
    :param context: Telegram's context
    :param baseText: Telegram message base text
    :param confirmationText: Telegram message confirmation text
    :param successfulText: Telegram message successful text
    """
    # Set option data
    buttons = []
    row = []
    text = baseText
    optionClicked = update.callback_query.data
    pageNumber = (weebot.settings.conversationPagination.get(str(update.callback_query.message.message_id)).get('Value') 
                  if str(update.callback_query.message.message_id) in weebot.settings.conversationPagination 
                  else 1)
    
    # Update page number based on option
    match optionClicked:
        case str(x) if 'next' in x:
            pageNumber += 1
        case str(x) if 'prev' in x:
            pageNumber -= 1

    # Get anime list based on operation
    match operation:
        case 'Subscribe':
            aniList, size = retrieve_subscribable_anime_list(chat_id=str(update.effective_chat.id),user_id=str(update.callback_query.from_user.id),pageNumber=pageNumber)
        case 'Unsubscribe':
            aniList, size = retrieve_unsubscribable_anime_list(chat_id=str(update.effective_chat.id),user_id=str(update.callback_query.from_user.id),pageNumber=pageNumber)
        case 'Ping':
            aniList, size = retrieve_pingable_anime_list(chat_id=str(update.effective_chat.id),pageNumber=pageNumber)
        case 'Update':
            aniList, size = retrieve_updatable_anime_list(chat_id=str(update.effective_chat.id),pageNumber=pageNumber)
        case _:
            aniList, size = retrieve_anime_list(chat_id=str(update.effective_chat.id),pageNumber=pageNumber)

    # Choose what to do
    match optionClicked:
        case str(x) if 'next' in x:
            logging.info(pageNumber)
        case str(x) if 'prev' in x:
            logging.info(pageNumber)
        case str(x) if x.replace(' '+operation,'').isnumeric():
            # Get data
            index = x.split()[0]
            text = confirmationText+aniList.get(int(index))+'?'
            
            # Confirmation menu
            for option in weebot.settings.confirmation:
                row.append(InlineKeyboardButton(weebot.settings.confirmation.get(option), callback_data=option+' '+index+' '+operation))
            buttons.append(row)

            # Update message
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                                message_id=update.callback_query.message.message_id,
                                                text=text,
                                                reply_markup=InlineKeyboardMarkup(buttons))
            return
        case str(x) if 'yes' in x:
            # Get data
            index = x.split()[1]
            text = ''

            # Insert match case to call backend
            match operation:
                case 'Subscribe':
                    updated, animeName = subscribe_anime(id=int(index),chat_id=str(update.effective_chat.id),
                                                        user_id=str(update.callback_query.from_user.id),username=str(update.callback_query.from_user.username))
                    text = '@'+update.callback_query.from_user.username+' is already subscribed to '+animeName+'! 😅'
                    if updated:
                        text = '@'+update.callback_query.from_user.username+successfulText+animeName+'! 😍'
                case 'Unsubscribe':
                    updated, animeName = unsubscribe_anime(id=int(index),chat_id=str(update.effective_chat.id),user_id=str(update.callback_query.from_user.id))
                    text = 'Something went wrong 😰, please try again! 🙏'
                    if updated:
                        text = '@'+update.callback_query.from_user.username+successfulText+animeName+'!'
                case 'Untrack':
                    updated, animeName = untrack_anime(id=int(index),chat_id=str(update.effective_chat.id))
                    text = 'Something went wrong 😰, please try again! 🙏'
                    if updated:
                        text = '@'+update.callback_query.from_user.username+successfulText+animeName+'!'
                case 'Ping':
                    usernames, animeName = ping_anime(id=int(index),chat_id=str(update.effective_chat.id))
                    text = 'Something went wrong 😰, please try again! 🙏'
                    if len(usernames) != 0:
                        text = ' '.join(usernames)+successfulText+animeName+'!'
                case 'Update':
                    text += successfulText
                    conversationFuzzyStrValue = {
                        "Value": operation+' '+index,
                        "Timestamp": datetime.datetime.now(),
                        "Message": str(update.callback_query.message.message_id)
                    }
                    conversationFuzzyStrValueId = str(update.effective_chat.id)+str(update.callback_query.from_user.id)
                    weebot.settings.conversationFuzzyStr.update({conversationFuzzyStrValueId: conversationFuzzyStrValue})
            
            # Update message
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                                message_id=update.callback_query.message.message_id,
                                                text=text)
            
            # Clear conversation handlers
            if str(update.callback_query.message.message_id) in weebot.settings.conversationPagination:
                weebot.settings.conversationPagination.pop(str(update.callback_query.message.message_id))
            if str(update.callback_query.message.message_id) in weebot.settings.conversations:
                weebot.settings.conversations.pop(str(update.callback_query.message.message_id))
            return
        case _:
            # Clear conversation handlers
            if str(update.callback_query.message.message_id) in weebot.settings.conversationPagination and 'no' not in optionClicked:
                weebot.settings.conversationPagination.pop(str(update.callback_query.message.message_id))
                
            # Return one screen
            if 'back' in optionClicked:
                buttons, text = createMenu('')
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                                    message_id=update.callback_query.message.message_id,
                                                    text=text,
                                                    reply_markup=InlineKeyboardMarkup(buttons))
                return

    # Create menu, update conversation handlers and message
    buttons, text = createPagination(aniList,text,size,pageNumber,operation)
    conversationPaginationValue = {
        "Value": pageNumber,
        "Timestamp": datetime.datetime.now()
    }
    weebot.settings.conversationPagination.update({str(update.callback_query.message.message_id): conversationPaginationValue})
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                        message_id=update.callback_query.message.message_id,
                                        text=text,
                                        reply_markup=InlineKeyboardMarkup(buttons),
                                        parse_mode='HTML',
                                        disable_web_page_preview=True)
