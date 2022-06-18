#!/usr/bin/env python
# -*- coding: utf-8 -*-
import crawler
import logging
import threading
import re
from config import token, interval_time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

tasks = dict()
chats = dict()

def termin(update, context):
    user = update.message.from_user.first_name
    url = update.message.text.split(" ")[1]
    logging.info("User " + str(update.message.from_user.id) + ":" + update.message.from_user.first_name + " asked for termin from " + url)
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
    logging.info("User " + str(update.message.from_user.id) + ":" + update.message.from_user.first_name + " asked for help")
    update.message.reply_text('Bitte gehe auf https://service.berlin.de/dienstleistungen/ und wähle deine Dienstleistung aus. Dann klicke Dich durch, bis Du zur Terminbuchung kommst. Kopiere diese Url dann und füge sie nach dem Kommando /termin ein.\n Zum Beispiel /termin https://service.berlin.de/terminvereinbarung/termin/tag.php?...')

def start(update, context):
    user = update.message.from_user.first_name 
    logging.info("User " + str(update.message.from_user.id) + ":" + user+ " started the bot")
    update.message.reply_text('Hallo '+ user +'.\nWillkommen zur Terminsuche für die Bürgerämter in Berlin.\nBitte gehe auf https://service.berlin.de/dienstleistungen/ und wähle deine Dienstleistung aus. Dann klicke Dich durch, bis Du zur Terminbuchung kommst. Kopiere diese Url dann und füge sie nach dem Kommando /termin ein.\n Zum Beispiel /termin https://service.berlin.de/terminvereinbarung/termin/tag.php?...')
def cancel(update, context):
    logging.info("User " + str(update.message.from_user.id) + ":" + update.message.from_user.first_name+ " asked for abbruch")
    ch_id = update.message.chat_id
    found = False
    for url in chats:
        if ch_id in chats[url]:
            found = True
            for item in tasks[url]:
                if item.message.chat_id == ch_id:
                    tasks[url].remove(item)
                    break
            chats[url].remove(ch_id)
            update.message.reply_text('OK, habe Deine Suche abgebrochen.')
    if found == False:
        update.message.reply_text('Du hast keine Suche offen.')
 
def resume(update, context):
    logging.info("User " + str(update.message.from_user.id) + ":" + update.message.from_user.first_name + " asked for resume")
    ch_id = update.message.chat_id
    for url in chats:
        if ch_id in chats[url]:
            tasks[url].append(update)
            update.message.reply_text('OK, werde weiter nach einem Termin ausschau halten. Mit /abbruch kannst Du die Suche beenden.')

def echo(update, context):
    logging.info("User " + str(update.message.from_user.id) + ":" + update.message.from_user.first_name + " asked for " + update.message.text)
    update.message.reply_text("Yo digga, was geht. Bitte benutze /hilfe , /termin [url] , /abbruch")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def check_for_appointments():
      threading.Timer(interval_time, check_for_appointments).start()
      for url in tasks:
        if len(tasks[url]) > 0:
            logging.info("Checking for appointments on " + url)
            apps = crawler.crawl(url)
            if apps:
                for user in tasks[url]:
                    user.message.reply_text("Es sind folgende Tage frei:\n" + apps + "\nBitte gehe auf " + url + " und sichere Dir so einen Termin.\nTippe auf /weiter um weiter nach Terminen zu suchen.")
                    tasks[url].remove(user)


def main():
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
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