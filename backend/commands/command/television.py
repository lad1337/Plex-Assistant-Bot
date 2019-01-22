import telegram
import backend.api.telegram

from backend import constants, logger
from backend.scheduler.jobs import catalogue
from backend.commands import checker
from backend.commands.wrapper import send_typing_action, send_upload_photo_action, send_upload_video_action
from backend.database.statement import select, insert, delete, update as update_db

@send_typing_action
def forceUpdate(bot, update):
    catalogue.updateTelevision(None, None)
    update.message.reply_text(constants.TELEVISION_FORCEUPDATE, parse_mode=telegram.ParseMode.MARKDOWN)

def watchShow(bot, update, args):
    show_search = select.getShowsSearch(" ".join(args))
    if(len(show_search) == 0):
        update.message.reply_text(constants.TELEVISION_WATCH_EMPTY_SEARCH, parse_mode=telegram.ParseMode.MARKDOWN)
        return False
    keyboard = []
    for show in range(min(10, len(show_search))):
        keyboard.append([telegram.InlineKeyboardButton(show_search[show][1], callback_data=constants.TELEVISION_WATCH_CALLBACK+show_search[show][1])])
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    update.message.reply_text(constants.TELEVISION_WATCH_FIRST_TEN, reply_markup=reply_markup, pass_chat_data=True, parse_mode=telegram.ParseMode.MARKDOWN)

def watchShowCallback(bot, update):
    show_name = update.callback_query.data[len(constants.TELEVISION_WATCH_CALLBACK):]
    show_id = select.getShowByName(show_name)[0]
    telegram_id = update.callback_query.message.chat_id
    telegram_name = update._effective_user.full_name
    watch_id = str(telegram_id)+str(constants.NOTIFIER_MEDIA_TYPE_TELEVISION)+str(show_id)
    desc = telegram_name + " watching " + show_name

    insert.insertNotifier(watch_id, telegram_id, show_id, constants.NOTIFIER_MEDIA_TYPE_TELEVISION, constants.NOTIFIER_FREQUENCY_IMMEDIATELY, desc)
    logger.info(__name__, "{} started watching a show: {}".format(telegram_name, show_name))
    
    keyboard = []
    for freq in range(len(constants.NOTIFIER_FREQUENCY)):
        keyboard.append([telegram.InlineKeyboardButton(constants.NOTIFIER_FREQUENCY[freq], callback_data=constants.TELEVISION_WATCH_FREQ_CALLBACK+str(watch_id)+","+str(freq))])
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(text=constants.TELEVISION_WATCH_FREQUENCY, reply_markup=reply_markup, chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, parse_mode=telegram.ParseMode.MARKDOWN)

def watchShowFreqCallback(bot, update):
    results =  update.callback_query.data[len(constants.TELEVISION_WATCH_FREQ_CALLBACK):].split(",")
    frequency = constants.NOTIFIER_FREQUENCY[int(results[1])].lower()
    show_name = select.getShow(select.getNotifier(results[0])[2])[1]
    update_db.updateNotifierFrequency(results[0], results[1])
    bot.edit_message_text(text=constants.TELEVISION_WATCH_SUCCESS.format(show_name, frequency), chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, parse_mode=telegram.ParseMode.MARKDOWN)

def unwatchShow(bot, update, args):
    show_search = select.getShowsWatchedSearch(update.message.chat_id, " ".join(args))
    if(len(show_search) == 0):
        update.message.reply_text(constants.TELEVISION_WATCH_EMPTY_SEARCH, parse_mode=telegram.ParseMode.MARKDOWN)
        return False
    keyboard = []
    for show in range(min(10, len(show_search))):
        keyboard.append([telegram.InlineKeyboardButton(show_search[show][1], callback_data=constants.TELEVISION_UNWATCH_CALLBACK+show_search[show][1])])
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    update.message.reply_text(constants.TELEVISION_WATCH_FIRST_TEN, reply_markup=reply_markup, pass_chat_data=True, parse_mode=telegram.ParseMode.MARKDOWN)

def unwatchShowCallback(bot, update):
    show_name = update.callback_query.data[len(constants.TELEVISION_UNWATCH_CALLBACK):]
    show_id = select.getShowByName(show_name)[0]
    telegram_id = update.callback_query.message.chat_id
    telegram_name = update._effective_user.full_name
    watch_id = str(telegram_id)+str(constants.NOTIFIER_MEDIA_TYPE_TELEVISION)+str(show_id)
    desc = telegram_name + " unwatched " + show_name

    delete.deleteNotifier(watch_id)
    logger.info(__name__, "{} unwatched a show: {}".format(telegram_name, show_name))
    bot.edit_message_text(text=constants.TELEVISION_UNWATCH_SUCCESS.format(show_name), chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, parse_mode=telegram.ParseMode.MARKDOWN)
