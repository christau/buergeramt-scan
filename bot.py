#!/usr/bin/env python
# -*- coding: utf-8 -*-
import crawler
import logging
import threading
import re
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
    url = update.message.text.split(" ")[1]
    pattern = re.compile(r"^https://service\.berlin\.de/terminvereinbarung/termin/tag.php\?.*")
    if not pattern.match(url):
        update.message.reply_text("Sorry, aber die url scheint falsch zu sein. Sie muss das format https://service.berlin.de/terminvereinbarung/termin/tag.php?termin=1... haben.\nPeace out")
        return
    update.message.reply_text("Ok. Werde nach einem Termin ausschau halten.\nIch werde Die eine Nachricht schicken, sollte es einen freien Termin geben.\nMit /abbruch kannst Du die Suche beenden.")
    #dienstleister=(.+?)&
    #dienstleisterlist=(.+?)&
    
    #remove old chat_id
    if url in chats:
        if update.message.chat_id in chats[url]:
            chats[url].remove(update.message.chat_id)
    if not url in tasks:
        tasks[url]=[update]
        chats[url]=[update.message.chat_id]
    else:
        tasks[url].append(update)
        chats[url].append(update.message.chat_id)
def help(update, context):
    """Send a message when the command /help is issued."""
#    print(update)
    update.message.reply_text('Bitte gehe auf https://service.berlin.de/dienstleistungen/ und wähle deine Dienstleistung aus. Dann klicke Dich durch, bis Du zur Terminbuchung kommst. Kopiere diese Url dann und füge sie nach dem Kommando /termin ein.\n Zum Beispiel /termin https://service.berlin.de/terminvereinbarung/termin/tag.php?...')
def cancel(update, context):
    ch_id = update.message.chat_id
    found = False
    for url in chats:
        if ch_id in chats[url]:
            found = True
            if update in tasks[url]:
                tasks[url].remove(update)
            chats[url].remove(ch_id)
            update.message.reply_text('OK, habe Deine Suche abgebrochen.')
    if found == False:
        update.message.reply_text('Du hast keine Suche offen.')
 
def resume(update, context):
    ch_id = update.message.chat_id
    for url in chats:
        if ch_id in chats[url]:
            tasks[url].append(update)
            update.message.reply_text('OK, werde weiter nach einem Termin ausschau halten. Mit /abbruch kannst Du die Suche beenden.')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text("Yo digga, was geht. Bitte benutze /hilfe , /termin [url] , /abbruch")

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
                    user.message.reply_text("Es sind folgende Tage frei:\n" + apps + "\nBitte gehe auf " + url + " und sichere Dir so einen Termin.\nTippe auf /weiter um weiter nach Terminen zu suchen.")
                    tasks[url].remove(user)


def main():
    updater = Updater("bot token", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("termin", termin))
    dp.add_handler(CommandHandler("hilfe", help))
    dp.add_handler(CommandHandler("weiter", resume))
    dp.add_handler(CommandHandler("abbruch", cancel))
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