from telegram.ext import Updater
from utils.constants import SERVER_IP, BOT_API_KEY, APP_API_KEY
from telegram.ext import CommandHandler, MessageHandler, Filters
import logging
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=BOT_API_KEY)
dispatcher = updater.dispatcher

API_KEY_HEADER = {'api_key': APP_API_KEY}


def get_token(chat_id):
    url = '{}/token/{}'.format(SERVER_IP, chat_id)
    r = requests.get(url, headers=API_KEY_HEADER)

    if r.status_code == 200:
        return r.text
    else:
        return ""


def request_renewal(chat_id, renew_token):
    url = '{}/token'.format(SERVER_IP)
    data = {"group_id": chat_id}
    if renew_token:
        # PUT for BASE_URL/token/:group_id
        r = requests.put("{}/{}".format(url, chat_id), data, headers=API_KEY_HEADER)
    else:
        # POST for BASE_URL/token
        r = requests.post(url, data, headers=API_KEY_HEADER)

    return r


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hello")


def register(bot, update):
    resp = request_renewal(update.message.chat_id, False)

    if resp.status_code == 200:
        bot.send_message(chat_id=update.message.chat_id, text="Group successfully registered!")
    elif resp.status_code == 403:
        bot.send_message(chat_id=update.message.chat_id, text="The group is already registered in the Bot!")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="There was a problem registering the group :(")


def renew(bot, update):
    resp = request_renewal(update.message.chat_id, True)

    if resp.status_code == 200:
        bot.send_message(chat_id=update.message.chat_id, text="Group token successfully renewed!")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="There was a problem renewing the group's token :(")


def manage_keys(bot, update):
    # Request format is BASE_URL/token/group_id
    resp = requests.get('{}/token/{}'.format(SERVER_IP, update.message.chat_id), headers=API_KEY_HEADER)
    manage_keys_url = '{}/keywords/{}?{}'.format(SERVER_IP, update.message.chat_id, resp.text)
    bot.send_message(chat_id=update.message.chat_id, text=manage_keys_url)


def get_key(bot, update):

    token = get_token(update.message.chat_id)

    keywords_headers = {"auth_token": token}

    if not token:
        bot.send_message(chat_id=update.message.chat_id, text="We could not authenticate the group :(")
        return

    message = update.message.text
    split_message = message.split(' ')
    keyword = split_message[0]

    if keyword[0] != '!':
        return

    filtered_keyword = keyword[1:]

    url = '{}/keywords/{}/{}'.format(SERVER_IP, update.message.chat_id, filtered_keyword)
    resp = requests.get(url, headers=keywords_headers)

    if resp.status_code == 200:
        decoded_resp = resp.text
        if decoded_resp:
            bot.send_message(chat_id=update.message.chat_id, text=decoded_resp)


def main():
    start_handler = CommandHandler('start', start)
    register_handler = CommandHandler('register', register)
    renew_handler = CommandHandler('renew', renew)
    manage_keys_handler = CommandHandler('manage_keys', manage_keys)
    get_key_handler = MessageHandler(Filters.text, get_key)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(register_handler)
    dispatcher.add_handler(renew_handler)
    dispatcher.add_handler(manage_keys_handler)
    dispatcher.add_handler(get_key_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
