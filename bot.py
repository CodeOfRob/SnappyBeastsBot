import logging

import dotenv
import telebot
import ts3
from telebot.types import BotCommand

from beerlist import Beerlist
from constants import COMMANDS_RAW, TRUSTED_CHAT_IDS


def get_online_clients(query_uri):
    conn = ts3.query.TS3ServerConnection(query_uri)
    conn.exec_("use", port="9995")
    clients = conn.exec_("clientlist").parsed
    return clients

def get_channel_info(query_uri, cid):
    conn = ts3.query.TS3ServerConnection(query_uri)
    conn.exec_("use", port="9995")
    info = conn.exec_(f"channelinfo", cid=cid).parsed
    return info

def main():

    # init env
    env = dotenv.dotenv_values()
    query_uri = env["QUERY_URI"]

    # init telebot logger
    telebot.logger.setLevel(logging.INFO)

    # init telegram api
    api_key = env["API_KEY"]
    bot = telebot.TeleBot(api_key)

    # init commands
    commands = {}
    for command, details in COMMANDS_RAW.items():
        comm = BotCommand(details["name"], details["description"])
        commands[command] = comm
    bot.set_my_commands(commands.values())
    
    # init beerlist
    beerlist = Beerlist("./data/beerlist.json")

    # commands
    @bot.message_handler(func=lambda msg: msg.chat.id not in TRUSTED_CHAT_IDS)
    def on_message(msg):
        bot.reply_to(msg, "Chat not trusted")
    
    @bot.message_handler(commands=[commands["showonlineclients"].command])
    def on_get_online_clients(msg):
        clients = get_online_clients(query_uri)
        # filter out clients that dont have client_type == 0 (normal client)
        clients = [c for c in clients if int(c["client_type"]) == 0]

        if len(clients) == 0:
            bot.send_message(msg.chat.id, "no clients online", parse_mode="html")
            return

        channels = {}
        for client in clients:
            if (int(client["client_type"]) == 0):
                channel_name = get_channel_info(query_uri, client["cid"])[0]["channel_name"]
                if channel_name not in channels:
                    channels[channel_name] = []
                channels[channel_name].append(client['client_nickname'])

        out = ""
        for channel_name in channels:
            out += f"<b>{channel_name}</b>\n"
            for client in channels[channel_name]:
                out += f" - {client}\n"

        bot.send_message(msg.chat.id, out, parse_mode="html")

    @bot.message_handler(commands=[commands["help"].command])
    def on_help(msg):
        out = "<b>These are the services I provide:</b>\n"
        for command in commands.values():
            out += f"- /{command.command}: {command.description}\n"
        bot.send_message(msg.chat.id, out, parse_mode="html")

    @bot.message_handler(commands=[commands["drink"].command])
    def on_beer(msg):
        beerlist.add_action("drink", msg.from_user.id, msg.from_user.username, 1)
        bot.send_message(msg.chat.id, str(beerlist), parse_mode="html")
        
    @bot.message_handler(commands=[commands["spill"].command])
    def on_spill(msg):
        beerlist.add_action("spill", msg.from_user.id, msg.from_user.username, 1)
        bot.send_message(msg.chat.id, str(beerlist), parse_mode="html")
        
    @bot.message_handler(commands=[commands["praisetheleader"].command])
    def praise_The_Leader(msg):

        idx = random.randint(0, len(PRAISE_LIST))-1
        emoji_idx = random.randint(0, len(EMOJI_LIST))-1

        out = f"<b>Praise to be Carlo the {PRAISE_LIST[idx]}!</b> {EMOJI_LIST[emoji_idx]}".upper()
        bot.send_message(msg.chat.id, out, parse_mode="html")

    bot.infinity_polling(logger_level=logging.INFO)

if __name__ == "__main__":
    main()
