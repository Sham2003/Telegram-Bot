import importlib
import sys
from config import *
import logging
from telethon import TelegramClient
from telethon.events import NewMessage
from models.dbmodels import AllowedGroup, connectdb
from motor.motor_asyncio import AsyncIOMotorClient

import os

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

client = AsyncIOMotorClient("mongodb://localhost:27017")

AVOIDED = []
LOADED = True

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=TOKEN)


def import_cogs():
    COGS_DIR = os.path.join(os.path.dirname(__file__), 'cogs')
    sys.path.insert(0, COGS_DIR)
    for filename in os.listdir(COGS_DIR):
        if filename.endswith('cog.py'):
            module_name = f"cogs.{filename[:-3]}"
            module = importlib.import_module(module_name)
            if hasattr(module, 'init_cog'):
                module.init_cog(bot)
            else:
                print(f"Module {module_name} does not have an init_cog function")


@bot.on(NewMessage(pattern='/start'))
async def send_welcome(event: NewMessage.Event):
    await bot.send_message(event.chat_id, 'Howdy, how are you doing?', reply_to=event._message_id)


AVOIDED.append(id(send_welcome))


@bot.on(NewMessage(pattern='/help(.*)'))
async def helper(event: NewMessage.Event):
    query = event.pattern_match.group(1).strip()
    COMMAND_LIST = ["start", "rank", "leaderboard", "calc", "compute", "integrate"]
    if query in COMMAND_LIST:
        help_description = {
            "start": "<u>Command name</u>:<i>start</i> \n <pre>Sends a welcome message </pre>",
            "rank": "<u>Command name</u>:<i>rank</i> \n <pre>Sends your current level</pre>",
            "leaderboard": '''<u>Command name</u>:<i>leaderboard</i> \n <pre>Sends message ranking leaderboard based on "
                           "messages sent </pre>''',
            "calc": '''<u>Command name</u>:<i>calc</i> \n <pre>Calculates a valid mathematical python expression  
            \n Usage: \n /calc 2**2 \n /calc cos(rad(45))</pre>''',
            "compute": '''<u>Command name</u>:<i>compute</i> \n <pre> Calculates a valid mathematical python expression 
                      \n Usage: \n /calc 2**2 \n /calc cos(rad(45))</pre> ''',
            "integrate": '''<u>Command name</u>:<i>integrate</i> \n <pre> Integrate a valid 'x'(only) based equation
            \n Parameters: \n expr:valid x based integrable polynomial or function 
            \n ul: valid integer for upper limit 
            \n ll: valid integer for lower limit
            \n <i> Spaces are important</i>
            \n Usage: \n /integrate expr="x**2" ul=3 ll=-3 
            \n For the funcs supported in integration see <i> /integrators </i></pre>'''
        }
        await bot.send_message(event.chat_id, help_description[query], parse_mode="HTML")
    else:
        help_message = "<b><u>Command List</u></b> <pre> \n"
        for i in COMMAND_LIST:
            help_message += i + "\n"
        help_message += "</pre> To know more about the command <i> /help [command_name]</i> "
        await bot.send_message(event.chat_id, help_message, parse_mode="HTML")


AVOIDED.append(id(helper))


@bot.on(NewMessage(pattern='/listcogs', chats=OWNER))
async def coghelper(event: NewMessage.Event):
    COGMESSAGE = "<b>ALL FUNCTIONS OF COGS:</b>\n"
    for callback, _ in bot.list_event_handlers():
        COGMESSAGE += f"<b>{callback.__name__}</b> \t- {id(callback)} \t- <i>{callback.__module__}</i> \n"

    await event.client.send_message(event.chat_id, COGMESSAGE, parse_mode="HTML")


AVOIDED.append(id(coghelper))


@bot.on(NewMessage(pattern='/loadcogs', chats=OWNER))
async def cogloader(event: NewMessage.Event):
    global LOADED
    if LOADED:
        await event.reply("Already Loaded all cogs")
        return
    import_cogs()
    LOADED = True


AVOIDED.append(id(cogloader))


@bot.on(NewMessage(pattern='/removecogs', chats=OWNER))
async def uncogloader(event: NewMessage.Event):
    global LOADED
    if not LOADED:
        await event.reply("Already removed all cogs")
        return
    for callback, tevent in bot.list_event_handlers():
        if id(callback) not in AVOIDED:
            bot.remove_event_handler(callback=callback, event=tevent)
    LOADED = False


AVOIDED.append(id(uncogloader))

if __name__ == '__main__':
    import_cogs()
    bot.loop.run_until_complete(connectdb(db=client.Telegram))
    print("Bot Started .....")
    bot.run_until_disconnected()
