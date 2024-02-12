from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import json
import logging

# Config
f = open('credentials.json')
creds = json.load(f)
TOKEN: Final = creds['TELEGRAM_TOKEN']
BOT_USERNAME: Final = creds['BOT_USERNAME']

# Menu
menu = {
    "Anime": "🎬",
    "List": "📃",
    "Update": "🔄",
    "Follow": "➕",
    "Ping": "🚨"
}

subMenu = {
    "Anime": {
        "Track" : "✅",
        "Untrack": "❌"
    },
    "Follow": {
        "Subscribe": "✅",
        "Unsubscribe" : "❌"
    }
}

help = {
    "Anime": {
        "Description" : "Group related commands to \\(un\\)track an anime",
        "Track" : "Choose an anime to track new episodes",
        "Untrack": "Stop anime new episodes updates"
    },
    "List": "List all current animes being watched and their progress",
    "Update": "Set which was the last episode watched for an anime",
    "Follow": {
        "Description" : "User related commands to \\(un\\)follow a watch party",
        "Subscribe": "Subscribe to receive updates when a watch party is happening",
        "Unsubscribe" : "Unsubscribe to stop receiving anime pings"
    },
    "Ping": "Ping all subscribed persons to an anime"
}

# Commands
async def options_command (update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Command context
    text = ''
    if 'start' in update.message.text:
        text = 'Hello! 🐶 Bondo likes you! 🥰 Hope we have fun! 😊\n'
    text += 'What should I sniff for you? 👃'

    # Create menu
    buttons = []
    row = []
    for option in menu:
        if len(row) == 2:
            buttons.append(row)
            row = []
        row.append(InlineKeyboardButton(menu.get(option)+' '+option, callback_data=option))
    buttons.append(row)

    # Send message
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=text,
                                   reply_markup=InlineKeyboardMarkup(buttons))
    
async def help_command (update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ''
    for option in help:
        if type(help.get(option)) is str:
            text += '*__'+option+':__* '+help.get(option)+'\n'
        else:
            text += '*__'+option+':__* '
            for subOption in help.get(option):
                if 'Description' in subOption:
                    text += help.get(option).get(subOption)+'\n'
                else:
                    text += '➖ *'+subOption+':* '+help.get(option).get(subOption)+'\n'
        text += '\n'

    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text=text,
                                   parse_mode='MarkdownV2')

# Callbacks
async def menu_callback (update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get callback data
    option = update.callback_query.data

    # Check if callback should trigger Sub Menu
    buttons = []
    if subMenu.get(option):
        row = []
        for subOption in subMenu.get(option):
            row.append(InlineKeyboardButton(subMenu.get(option).get(subOption)+' '+subOption, callback_data=subOption))
        buttons.append(row)
    
    # Create menu
    if buttons:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                            message_id=update.callback_query.message.message_id,
                                            text='I need to smell a little more: 👃',
                                            reply_markup=InlineKeyboardMarkup(buttons))
        await update.callback_query.answer()
    # Handle options
    else:
        if option == 'List':
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                            message_id=update.callback_query.message.message_id,
                                            text=option)
        elif option == 'Update':
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                            message_id=update.callback_query.message.message_id,
                                            text=option)
        elif option == 'Ping':
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                            message_id=update.callback_query.message.message_id,
                                            text=option)
        elif option == 'Track':
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                            message_id=update.callback_query.message.message_id,
                                            text=option)
        elif option == 'Untrack':
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                            message_id=update.callback_query.message.message_id,
                                            text=option)
        elif option == 'Subscribe':
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                            message_id=update.callback_query.message.message_id,
                                            text=option)
        elif option == 'Unsubscribe':
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                            message_id=update.callback_query.message.message_id,
                                            text=option)
        await update.callback_query.answer('Success')
        

# Responses
def handle_response(text: str) -> str:
    # Process message
    processed: str = text.lower()

    # Handle message
    if text in menu:
        return text
    if text in subMenu["Anime"]:
        return text
    if text in subMenu["Follow"]:
        return text
    if 'hello' in processed:
        return 'Haaai!'
    if 'how are you' in processed:
        return 'Better now!'
    
    # Error
    return 'Can you throw me the ⚾ again? I didn\'t find it 😔'

async def handle_message (update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    logging.info(f'User (%s) in %s: "%s"', update.message.chat.id, message_type, text)

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME,'').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    logging.info('Bot: %s', response)
    
    await update.message.reply_text(response)

async def error (update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Callback
    app.add_handler(CallbackQueryHandler(menu_callback))

    # Polls the bot
    logging.info('Polling...')
    app.run_polling(poll_interval=3)
