#!/usr/bin/env python
# -*- coding: utf-8 -*-
import crawler
import logging
import threading
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

tasks = dict()
chats = dict()

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def termin(update, context):
    user = update.message.from_user
    update.message.reply_text("Ok. Werde nach einem Termin ausschau halten")
    url = update.message.text.split(" ")[1]
    if not url in tasks:
        tasks[url]=[update]
        chats[url]=[update.message.chat_id]
    else:
        tasks[url].append(update)
        chats[url].append(update.message.chat_id)
def help(update, context):
    """Send a message when the command /help is issued."""
#    print(update)
    update.message.reply_text('Bitte gehe auf https://service.berlin.de/dienstleistungen/ und wähle deine Dienstleistung aus.')

def resume(update, context):
    ch_id = update.message.chat_id
    for url in chats:
        if ch_id in chats[url]:
            tasks[url].append(update)
            update.message.reply_text('OK, werde weiter nach einem Termin ausschau halten')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text("Yo digga, was geht. Bitte benutze /hilfe oder /termin [url]")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def check_for_appointments():
      threading.Timer(20.0, check_for_appointments).start()
      for url in tasks:
        if len(tasks[url]) > 0:
            apps = crawler.crawl(url)
            if apps:
                for user in tasks[url]:
                    user.message.reply_text("Es sind folgende Tage frei:\n" + apps + "\nBitte gehe auf " + url + " und sichere Dir so einen Termin.")
                    tasks[url].remove(user)


def main():
    updater = Updater("bot token", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("termin", termin))
    dp.add_handler(CommandHandler("hilfe", help))
    dp.add_handler(CommandHandler("weiter", resume))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    check_for_appointments()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()