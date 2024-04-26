import json, logging, re, threading, pickle, datetime
import asyncio
from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from time import sleep
from weebot import ANIMEURL
from weebot.track.track import track_anime, untrack_anime, check_if_tracked, retrieve_anime_list, retrieve_anime_list_detail
from weebot.track.track import subscribe_anime, unsubscribe_anime, retrieve_subscribable_anime_list, retrieve_unsubscribable_anime_list
from weebot.track.track import retrieve_updatable_anime_list, update_anime, update_all_anime
from weebot.track.track import ping_anime, retrieve_pingable_anime_list, ping_multiples_animes, subscribe_multiple_animes

# Config
f = open('credentials.json')
creds = json.load(f)
TOKEN: Final = creds['TELEGRAM_TOKEN']
BOT_USERNAME: Final = creds['BOT_USERNAME']
MAX_LINE_SIZE = 8
CONVERSATION_CHECK_DELAY = 60
DELETE_DELAY = 30
EPISODE_CHECK_DELAY = 900

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
    # r"/Subscribe \{animeListIndex\}": r"Subscribe to receive updates when a watch party is happening to all animes on \{animeListIndex\}",
    "Unsubscribe" : "Unsubscribe to stop receiving anime pings",
    "Ping": "Ping all subscribed persons to an anime",
    # r"/Ping \{animeListIndex\}": r"Ping all subscribed persons to all animes on \{animeListIndex\}\n",
    # r"\{animeListIndex\}": "Anime index on List separated by ';'",
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

# Group Handling
with open(r".\data\conversations.pkl", 'rb') as f:
    conversations = pickle.load(f)
with open(r".\data\conversationPagination.pkl", 'rb') as f:
    conversationPagination = pickle.load(f)
with open(r".\data\conversationFuzzyStr.pkl", 'rb') as f:
    conversationFuzzyStr = pickle.load(f)

# Commands
async def options_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Command context
    global conversations
    text = ''
    if 'start' in update.message.text:
        text = 'Hello! 🐶 Bondo likes you! 🥰 Hope we have fun! 😊\n'

    # Create menu
    buttons, text = createMenu(text)

    # Send message
    created_message = await context.bot.send_message(chat_id=update.effective_chat.id, 
                                                     text=text,
                                                     reply_markup=InlineKeyboardMarkup(buttons))
    
    conversationValue = {
        "Value": str(update.effective_chat.id)+str(update.message.from_user.id),
        "Timestamp": datetime.datetime.now()
    }

    conversations.update({str(created_message.message_id): conversationValue})
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global help
    text = ''
    for option in help:
        text += '*__'+option+':__* '+help.get(option)+'\n\n'

    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=text,
                                   parse_mode='MarkdownV2')

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# Callbacks
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get callback data
    global conversations, conversationFuzzyStr, conversationPagination
    # logging.info('Conversation: %s',conversations)
    # logging.info('conversationPagination: %s',conversationPagination)
    # logging.info('conversationFuzzyStr: %s',conversationFuzzyStr)
    commandsToIgnore = ['Substracker']
    option = update.callback_query.data
    result = 'Success'
    conversationValue = {
        "Value": str(update.effective_chat.id)+str(update.callback_query.from_user.id),
        "Timestamp": datetime.datetime.now()
    }

    # Check if the conversation is being tracked
    if not (str(update.callback_query.message.message_id) in conversations):
        await update.callback_query.answer('This message expired. 😰 Could you please send /options again? 🥺')
        return
    # Check if is the same user that started the conversation
    if ((conversations.get(str(update.callback_query.message.message_id)).get('Value') != conversationValue.get('Value')) and not [i for i in commandsToIgnore if i in option]):
        await update.callback_query.answer('Bondo is helping other person, please make your own request or I will be confused 😵')
        return
    
    # Update last time this conversation got a follow up
    conversations.update({str(update.callback_query.message.message_id): conversationValue})

    # Handle options
    match option:
        case str(x) if 'List' in x:
            await handle_list(update,context)
        case str(x) if 'Update' in x:
            await handle_update(update,context)
        case str(x) if 'Track' in x:
            await handle_track(update,context)
        case str(x) if 'Untrack' in x:
            await handle_untrack(update,context)
        case str(x) if 'Subscribe' in x:
            await handle_subscribe(update,context)
        case str(x) if 'Unsubscribe' in x:
            await handle_unsubscribe(update,context)
        case str(x) if 'Ping' in x:
            await handle_ping(update,context)
        case _:
            result = 'Error'
            conversations.pop(str(update.callback_query.message.message_id))
    
    await update.callback_query.answer(result)

# Helpers
def multiple_use_regex(list):
    for text in list:
        if not use_regex(text):
            return False
    return True

def use_regex(input_text):
    pattern = re.compile(r"^[0-9]+$", re.IGNORECASE)
    return pattern.match(input_text)

def createMenu(text: str):
    global menu
    text += 'What should I sniff for you? 👃'
    buttons = []
    row = []
    for option in menu:
        if len(row) == 2:
            buttons.append(row)
            row = []
        row.append(InlineKeyboardButton(menu.get(option)+' '+option, callback_data=option))
    buttons.append(row)

    return buttons, text

def createPagination(aniList: dict, text: str, size: int, pageNumber: int, operation: str):
    global pagination
    aniListSize = len(aniList)
    buttons = []
    row = []
    count = 0

    if aniListSize > 0:
        for page in pagination:
            if count >= MAX_LINE_SIZE:
                count = 0
                buttons.append(row)
                row = []
            if str(page) == 'prev':
                if pageNumber > 1:
                    row.append(InlineKeyboardButton(pagination.get(page), callback_data=page+' '+operation))
                    text += '\nClick on ◀ to see the previous page.\n'
                continue
            if str(page) == 'next':
                if pageNumber < size:
                    row.append(InlineKeyboardButton(pagination.get(page), callback_data=page+' '+operation))
                    text += '\nClick on ▶ to see the next page.\n'
                continue
            if int(page) < aniListSize:
                row.append(InlineKeyboardButton(pagination.get(page), callback_data=str(list(aniList)[int(page)])+' '+operation))
                text += pagination.get(page)+': <a href="'+ANIMEURL+str(list(aniList)[int(page)])+'/">'+list(aniList.values())[int(page)]+'</a>\n'
            count += 1
        buttons.append(row)
    else:
        text = 'I couldn\'t find any anime for this option. 😭'
    back = [InlineKeyboardButton('🔙', callback_data='back '+operation)]
    buttons.append(back)
    text += '\nClick on 🔙 to return to the options.\n\n'
    
    return buttons, text

async def optionHandler(operation: str, update: Update, context: ContextTypes.DEFAULT_TYPE, baseText: str, confirmationText: str, successfulText: str):
    global conversationPagination, confirmation, conversationFuzzyStr, conversations
    text = baseText
    optionClicked = update.callback_query.data
    pageNumber = (conversationPagination.get(str(update.callback_query.message.message_id)).get('Value') 
                  if str(update.callback_query.message.message_id) in conversationPagination 
                  else 1)
    
    match optionClicked:
        case str(x) if 'next' in x:
            pageNumber += 1
        case str(x) if 'prev' in x:
            pageNumber -= 1

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
    buttons = []
    row = []

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
            for option in confirmation:
                row.append(InlineKeyboardButton(confirmation.get(option), callback_data=option+' '+index+' '+operation))
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
                    # conversationFuzzyStrValueId += str(update.callback_query.message.message_id) if update.message.chat.type == 'group' else ''
                    conversationFuzzyStr.update({conversationFuzzyStrValueId: conversationFuzzyStrValue})
            
            # Update message
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                                message_id=update.callback_query.message.message_id,
                                                text=text)
            
            # Clear conversation handlers
            if str(update.callback_query.message.message_id) in conversationPagination:
                conversationPagination.pop(str(update.callback_query.message.message_id))
            if str(update.callback_query.message.message_id) in conversations:
                conversations.pop(str(update.callback_query.message.message_id))
            return
        case _:
            # Clear conversation handlers
            if str(update.callback_query.message.message_id) in conversationPagination and 'no' not in optionClicked:
                conversationPagination.pop(str(update.callback_query.message.message_id))
                
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
    conversationPagination.update({str(update.callback_query.message.message_id): conversationPaginationValue})
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                        message_id=update.callback_query.message.message_id,
                                        text=text,
                                        reply_markup=InlineKeyboardMarkup(buttons),
                                        parse_mode='HTML',
                                        disable_web_page_preview=True)

def handleSavedConversations():
    global conversations, conversationPagination, conversationFuzzyStr
    while True:
        now = datetime.datetime.now()
        listToDelete = []
        for option in conversations:
            if conversations.get(option).get('Timestamp') + datetime.timedelta(minutes=DELETE_DELAY) < now:
                listToDelete.append(option)

        for option in listToDelete:
            conversations.pop(option)

        listToDelete = []
        for option in conversationPagination:
            if conversationPagination.get(option).get('Timestamp') + datetime.timedelta(minutes=DELETE_DELAY) < now:
                listToDelete.append(option)

        for option in listToDelete:
            conversationPagination.pop(option)

        listToDelete = []
        for option in conversationFuzzyStr:
            if conversationFuzzyStr.get(option).get('Timestamp') + datetime.timedelta(minutes=DELETE_DELAY) < now:
                listToDelete.append(option)

        for option in listToDelete:
            conversationFuzzyStr.pop(option)
        
        with open(r".\data\conversations.pkl", 'wb') as f:
            pickle.dump(conversations, f)
        with open(r".\data\conversationPagination.pkl", 'wb') as f:
            pickle.dump(conversationPagination, f)
        with open(r".\data\conversationFuzzyStr.pkl", 'wb') as f:
            pickle.dump(conversationFuzzyStr, f)

        sleep(CONVERSATION_CHECK_DELAY)

async def sendEpisodesUpdates(chat, anime):
    app = Application.builder().token(TOKEN).build()
    await app.bot.send_message(chat_id=chat,text=anime)

def handleEpisodesUpdates():
    while True:
        pingList = update_all_anime()
        for ping in pingList:
            for chat in ping.keys():
                for anime in ping[chat]:
                    asyncio.run(sendEpisodesUpdates(chat=chat,anime=anime))

        sleep(EPISODE_CHECK_DELAY)

# Responses
async def handle_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get data
    global conversationPagination, pagination
    text = 'These are the Animes being tracked:\n'
    optionClicked = update.callback_query.data
    pageNumber = (conversationPagination.get(str(update.callback_query.message.message_id)).get('Value') 
                  if str(update.callback_query.message.message_id) in conversationPagination 
                  else 1)
    buttons = []
    row = []

    # Choose what to do
    match optionClicked:
        case str(x) if 'next' in x:
            pageNumber += 1
        case str(x) if 'prev' in x:
            pageNumber -= 1
        case _: 
            if str(update.callback_query.message.message_id) in conversationPagination:
                conversationPagination.pop(str(update.callback_query.message.message_id))
            # Return one screen
            if 'back' in optionClicked:
                buttons, text = createMenu('')
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                                    message_id=update.callback_query.message.message_id,
                                                    text=text,
                                                    reply_markup=InlineKeyboardMarkup(buttons))
                return

    aniList, aniListSize, size, indexInformation = retrieve_anime_list_detail(chat_id=str(update.effective_chat.id),pageNumber=pageNumber)
    text += indexInformation

    # Create menu
    for page in pagination:
        if str(page) == 'prev':
            if pageNumber > 1:
                row.append(InlineKeyboardButton(pagination.get(page), callback_data=page+' List'))
                text += '\nClick on ◀ to see the previous page.\n'
            continue
        if str(page) == 'next':
            if pageNumber < size:
                row.append(InlineKeyboardButton(pagination.get(page), callback_data=page+' List'))
                text += '\nClick on ▶ to see the next page.\n'
            continue
        if int(page) < aniListSize:
            text += str(list(aniList)[int(page)])+': '+list(aniList.values())[int(page)]+'\n'
    buttons.append(row)
    back = [InlineKeyboardButton('🔙', callback_data='back List')]
    buttons.append(back)
    text += '\nClick on 🔙 to return to the options.\n\n'

    # Update conversation handlers and message
    conversationPaginationValue = {
        "Value": pageNumber,
        "Timestamp": datetime.datetime.now()
    }
    conversationPagination.update({str(update.callback_query.message.message_id): conversationPaginationValue})
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                        message_id=update.callback_query.message.message_id,
                                        text=text,
                                        reply_markup=InlineKeyboardMarkup(buttons),
                                        parse_mode='HTML',
                                        disable_web_page_preview=True)

async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Set data
    baseText = 'Which Anime you want to update:\n\n'
    confirmationText = 'Are you sure you want to update '
    successfulText = 'Please send me only the episode number.'

    # Handle update flow
    await optionHandler('Update',update,context,baseText,confirmationText,successfulText)

async def handle_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get data
    global conversations, conversationFuzzyStr, menu
    text = 'Please, send me the Anime name you want to track:\n\n'
    optionClicked = update.callback_query.data

    # Choose what to do
    match optionClicked:
        case str(x) if 'Substracker' in x:
            index = x.split()[1]
            updated, animeName = subscribe_anime(id=int(index),chat_id=str(update.effective_chat.id),
                                                 user_id=str(update.callback_query.from_user.id),username=str(update.callback_query.from_user.username))
            text = '@'+update.callback_query.from_user.username+' is already subscribed to '+animeName+'! 😅'
            if (updated):
                text = '@'+update.callback_query.from_user.username+' successfully subscribed to '+animeName+'! 😍'
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text)
            return
        case str(x) if x.replace(' Track','').isnumeric():
            index = x.split()[0]
            found = track_anime(id=int(index),chat_id=str(update.effective_chat.id))
            text = 'Successfully tracked '+found[0]["namePreferred"]+'!'
            buttons = []
            subscribe = [InlineKeyboardButton(menu.get('Subscribe')+' Subscribe', callback_data='Substracker '+index+' Track')]
            buttons.append(subscribe)
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                                message_id=update.callback_query.message.message_id,
                                                text=text,
                                                reply_markup=InlineKeyboardMarkup(buttons))
            conversationFuzzyStrValueId = str(update.effective_chat.id)+str(update.callback_query.from_user.id)
            # conversationFuzzyStrValueId += str(update.callback_query.message.message_id) if update.message.chat.type == 'group' else ''
            conversationFuzzyStr.pop(conversationFuzzyStrValueId)
            return
        case _:
            # Return one screen
            if not('no' in optionClicked) and str(update.callback_query.message.message_id) in conversations:
                conversations.pop(str(update.callback_query.message.message_id))

    await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                        message_id=update.callback_query.message.message_id,
                                        text=text)
    conversationFuzzyStrValue = {
        "Value": 'Track',
        "Timestamp": datetime.datetime.now(),
        "Message": str(update.callback_query.message.message_id)
    }
    conversationFuzzyStrValueId = str(update.effective_chat.id)+str(update.callback_query.from_user.id)
    # conversationFuzzyStrValueId += str(update.callback_query.message.message_id) if update.message.chat.type == 'group' else ''
    conversationFuzzyStr.update({conversationFuzzyStrValueId: conversationFuzzyStrValue})

async def handle_untrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Set data
    baseText = 'Which Anime you want to untrack:\n\n'
    confirmationText = 'Are you sure you want to untrack '
    successfulText = ' successfully untracked '

    # Handle update flow
    await optionHandler('Untrack',update,context,baseText,confirmationText,successfulText)
    
async def handle_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Set data
    baseText = 'Which Anime you want to subscribe:\n\n'
    confirmationText = 'Are you sure you want to subscribe to '
    successfulText = ' successfully subscribed to '

    # Handle update flow
    await optionHandler('Subscribe',update,context,baseText,confirmationText,successfulText)
    
async def handle_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get data
    baseText = 'Which Anime you want to unsubscribe:\n\n'
    confirmationText = 'Are you sure you want to unsubscribe from '
    successfulText = ' successfully unsubscribed from '

    # Handle update flow
    await optionHandler('Unsubscribe',update,context,baseText,confirmationText,successfulText)
    
async def handle_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Set data
    baseText = 'Which Anime you want to ping:\n\n'
    confirmationText = 'Are you sure you want to ping viewers from '
    successfulText = ' let\'s watch '

    # Handle update flow
    await optionHandler('Ping',update,context,baseText,confirmationText,successfulText)

async def handle_response(text: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Process message
    global conversationFuzzyStr, conversations, pagination
    processed: str = text.lower()
    response = 'Can you throw me the ⚾ again? I didn\'t find it. 😔'
    conversationFuzzyStrValueId = str(update.effective_chat.id)+str(update.message.from_user.id)

    # Handle message
    if conversationFuzzyStrValueId in conversationFuzzyStr:
        aniList = {}
        buttons = []
        row = []
        currentFuzzyStr = conversationFuzzyStr.get(conversationFuzzyStrValueId).get('Value')

        if 'Track' in currentFuzzyStr:
            is_tracked, found, msg = check_if_tracked(search_term=processed,chat_id=str(update.effective_chat.id))
            if(not is_tracked):
                if len(found) == 0:
                    response = 'I couldn\'t find any anime with that name. 😭\nPlease, click on ❌ and try to send me another name!\n'
                else:
                    response = 'I found these Animes. 😋 Is it any of these? 🤔\n\n'
                for anime in found:
                    aniList.update({anime["id"]: anime["namePreferred"]})

                # Create menu
                count = 0
                for anime in aniList:
                    row.append(InlineKeyboardButton(pagination.get(str(count)), callback_data=str(anime)+' Track'))
                    response += pagination.get(str(count))+': <a href="'+ANIMEURL+str(anime)+'/">'+aniList.get(anime)+'</a>\n'
                    count += 1
                buttons.append(row)
                no = [InlineKeyboardButton('❌', callback_data='no Track')]
                buttons.append(no)

                # Send message
                created_message = await context.bot.send_message(chat_id=update.effective_chat.id, 
                                                                    text=response,
                                                                    reply_markup=InlineKeyboardMarkup(buttons),
                                                                    parse_mode='HTML',
                                                                    disable_web_page_preview=True)
                
                # Update last time this conversation got a follow up
                conversationValue = {
                    "Value": conversationFuzzyStrValueId,
                    "Timestamp": datetime.datetime.now()
                }
                conversations.update({str(created_message.message_id): conversationValue})
            
            else:
                response = found["namePreferred"] + ' is already being tracked!\nI will ping you when new episodes are released! 😋'
                # Send message
                await context.bot.send_message(chat_id=update.effective_chat.id,text=response)
                conversationFuzzyStr.pop(conversationFuzzyStrValueId)
            
            return
        
        elif 'Update' in currentFuzzyStr:
            if use_regex(processed):
                index = str(currentFuzzyStr).replace('Update ','')
                updated, animeName, animeEpisodes = update_anime(id=int(index),chat_id=str(update.effective_chat.id),episode=int(processed))
                response = animeName+' has only '+str(animeEpisodes)+' episodes. Please send me a lower number!'
                if animeEpisodes == 0:
                    response = animeName+' is not being tracked by you!'
                if updated:
                    response = 'Successfully updated '+animeName+'! Episode '+processed+' of '+str(animeEpisodes)+'.'
                conversationFuzzyStr.pop(conversationFuzzyStrValueId)
            
            else:
                response = 'That\'s not a valid episode! 😰 Please send me only the episode number.'

    else:
        if 'hello' in processed:
            response = 'Haaai! 😁'
        if 'how are you' in processed:
            response = 'Better now! 🥰'
    
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=response)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global conversationFuzzyStr
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # logging.info(f'User (%s) in %s: "%s"', update.message.chat.id, message_type, text)

    if message_type == 'group':
        conversationFuzzyStrValueId = str(update.effective_chat.id)+str(update.message.from_user.id)
        if conversationFuzzyStrValueId in conversationFuzzyStr:
            if conversationFuzzyStr.get(conversationFuzzyStrValueId).get("Message") != str(update.message.reply_to_message.message_id):
                return
        else:
            return
        new_text: str = text
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME,'').strip()
        await handle_response(new_text,update,context)
    else:
        await handle_response(text,update,context)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f'Update ({update}) caused error {context.error}')

# Main
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO
    )
    logging.info('Starting bot...')
    app = Application.builder().token(TOKEN).build()

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
