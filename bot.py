import logging
import telebot
import dotenv
import ts3
import logging

from telebot.types import BotCommand


# SnappyBeasts: -1001398316625
# Fnace private Chat: 750707743
TRUSTED_CHAT_IDS = [-1001398316625, 750707743]

def get_online_clients():
    conn = ts3.query.TS3ServerConnection(env["QUERY_URI"])
    conn.exec_("use", port="9995")
    clients = conn.exec_("clientlist").parsed
    return clients

def main():

    api_key = env["API_KEY"]
    bot = telebot.TeleBot(api_key)

    commands = []

    comm_help = BotCommand("help", "I will show you a lists of services I provide.")
    commands.append(comm_help)

    comm_get_online_players = BotCommand("get_online_players", "I will show you a list of retards who are online.")
    commands.append(comm_get_online_players)

    bot.set_my_commands(commands)
    

    @bot.message_handler(func=lambda msg: msg.chat.id not in TRUSTED_CHAT_IDS)
    def on_message(msg):
        bot.reply_to(msg, "Chat not trusted")
    
    @bot.message_handler(commands=[comm_get_online_players.command])
    def on_get_online_clients(msg):
        clients = get_online_clients()

        out = "<b>online lifeless retards</b>:\n"

        for client in clients:
            if (int(client["client_type"]) == 0):
                out += f"- {client['client_nickname']}\n"

        bot.send_message(msg.chat.id, out, parse_mode="html")


    print("starting bot")
    bot.infinity_polling(logger_level=logging.INFO)



if __name__ == "__main__":

    global env
    env = dotenv.dotenv_values()

    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    main()