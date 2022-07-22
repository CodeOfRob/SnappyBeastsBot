import json
import logging
import telebot
import dotenv
import ts3
import logging

from telebot.types import BotCommand

from beerlist import Beerlist
from constants import COMMANDS_RAW, EMOJI_LIST, PRAISE_LIST, TRUSTED_CHAT_IDS

# SnappyBeasts: -1001398316625
# Fnace private Chat: 750707743
TRUSTED_CHAT_IDS = [-1001398316625, 750707743]

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

def save_beerlist(beerlist):

    # init env
    env = dotenv.dotenv_values()
    query_uri = env["QUERY_URI"]

def load_beerlist():

    f = open("beerlist.json", "r")
    out = json.loads(f.read())
    f.close()
    return out 
   
     

def main():

    api_key = env["API_KEY"]
    bot = telebot.TeleBot(api_key)

    commands = []

    comm_help = BotCommand("help", "I will show you a lists of services I provide.")
    commands.append(comm_help)

    comm_get_online_clients = BotCommand("get_online_clients", "I will show you a list of retards who are online.")
    commands.append(comm_get_online_clients)

    comm_bier = BotCommand("beer", "Tell me you drank a beer.")
    commands.append(comm_bier)

    comm_spill = BotCommand("spill", "Tell me you spilled a beer")
    commands.append(comm_spill)

    bot.set_my_commands(commands)
    

    beerlist = load_beerlist()


    @bot.message_handler(func=lambda msg: msg.chat.id not in TRUSTED_CHAT_IDS)
    def on_message(msg):
        bot.reply_to(msg, "Chat not trusted")
    
    @bot.message_handler(commands=[commands["showonlineclients"].command])
    def on_get_online_clients(msg):
        clients = get_online_clients(query_uri)
        channels = {}
        for client in clients:
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

    @bot.message_handler(commands=[comm_help.command])
    def on_help(msg):
        out = "<b>These are the services I provide:</b>\n"
        for command in commands:
            out += f"- /{command.command}: {command.description}\n"
        
        bot.reply_to(msg, out, parse_mode="html")

    @bot.message_handler(commands=[comm_bier.command])
    def on_beer(msg):
        user_id = str(msg.from_user.id)
        if user_id not in beerlist.keys():
            beerlist[user_id] = {"user_id": msg.from_user.id, "username": msg.from_user.username, "beer_count": 0}
        beerlist[user_id]["beer_count"] += 1

        out = "<b>Beerlist:</b>\n"

        for key in beerlist:
            out += f"{beerlist[key]['username']}: {beerlist[key]['beer_count']}\n"

        bot.reply_to(msg, out, parse_mode="html")
        save_beerlist(beerlist)
        
    @bot.message_handler(commands=[comm_spill.command])
    def on_spill(msg):
        user_id = str(msg.from_user.id)
        if user_id not in beerlist.keys():
            beerlist[user_id] = {"user_id": msg.from_user.id, "username": msg.from_user.username, "beer_count": 0}
        beerlist[user_id]["beer_count"] -= 1

    @bot.message_handler(commands=[commands["praisetheleader"].command])
    def praise_The_Leader(msg):

        idx = random.randint(0, len(PRAISE_LIST))-1
        emoji_idx = random.randint(0, len(EMOJI_LIST))-1

        out = f"<b>Praise to be Carlo the {PRAISE_LIST[idx]}!</b> {EMOJI_LIST[emoji_idx]}".upper()
        bot.send_message(msg.chat.id, out, parse_mode="html")

    print("starting bot")
    bot.infinity_polling(logger_level=logging.INFO)



if __name__ == "__main__":

    global env
    env = dotenv.dotenv_values()

    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    main()