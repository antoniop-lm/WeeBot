from typing import Final
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import logging

# Config
f = open('credentials.json')
creds = json.load(f)
TOKEN: Final = creds['TELEGRAM_TOKEN']
BOT_USERNAME: Final = creds['BOT_USERNAME']

# Menu
menu = [
    "Anime",
    "List",
    "Update",
    "Follow",
    "Ping"
]

subMenu = {
    "Anime": ["Track","Untrack"],
    "Follow": ["Subscribe","Unsubscribe"]
}

# Commands
async def start_command (update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    for option in menu:
        buttons.append([KeyboardButton(option)])
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text='Hello! Bondo likes you! Hope we have fun!',
                                   reply_markup=ReplyKeyboardMarkup(buttons))

async def options_command (update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    for option in menu:
        buttons.append([KeyboardButton(option)])
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text='Let me help you',
                                   reply_markup=ReplyKeyboardMarkup(buttons))
    
async def help_command (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('What can I sniff you in?')

async def custom_command (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Throw the ball, please!')

# Responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

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
    
    return 'Could you please explain what you want in another way?'

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
    
    buttons = []
    if subMenu.get(response):
        for subOption in subMenu.get(response):
            buttons.append([KeyboardButton(subOption)])
    
    if buttons:
        await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text='Let me help you',
                                   reply_markup=ReplyKeyboardMarkup(buttons))
    else:
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
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('options', options_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    logging.info('Polling...')
    app.run_polling(poll_interval=3)
