import math
from telethon import TelegramClient
from telethon.events import NewMessage
import telethon.tl.types as teletypes
from models.dbmodels import RankLevel
from mfilters import adminfilter,allowedgroupfilter,mfilter

EVENTS = []
CALLBACKS = []

async def mylevel(e:NewMessage.Event):
    user_id = e.message.from_id.user_id
    chat_id = e.chat_id
    bot = e.client
    stats = await RankLevel.find_one(RankLevel.user_id == user_id and RankLevel.clan_id == chat_id)
    if stats is None:
        await bot.send_message(chat_id, "Currently you are not in the rank list! Send some messages and try again")
    else:
        await bot.send_message(chat_id,f"Currently you are in Level <b>{stats.level}</b> ! Keep up ", parse_mode="HTML")

EVENTS.append(NewMessage(pattern='/rank',func=allowedgroupfilter))
CALLBACKS.append(mylevel)


async def leaderboard(e:NewMessage.Event):
    print("Leaderboard")
    bot = e.client
    LDRSTRING = "<b><u> TOP RANKINGS </u></b>\n"
    result = await RankLevel.find().sort().limit(10).to_list()
    if result is None:
        return
    for i, usr in enumerate(result):
        LDRSTRING += f"{i + 1}. <a href='tg://user?id={usr.user_id}'>{usr.first_name + usr.last_name}</a> = {usr.level} \n "
    await bot.send_message(e.chat_id, LDRSTRING, parse_mode="HTML")

EVENTS.append(NewMessage(pattern='/leaderboard',func=lambda e:mfilter(allowedgroupfilter,adminfilter)))
CALLBACKS.append(leaderboard)


async def levelup(e:NewMessage.Event):
    if e.message.message.startswith('/'):
        return
    clan_id = e.chat_id
    sender = await e.get_sender()
    user_id = e.message.from_id.user_id
    stats = await RankLevel.find_one(RankLevel.user_id == sender.id and RankLevel.clan_id == clan_id)
    if stats is None:
        rankuser = RankLevel(
            user_id = user_id,
            clan_id=clan_id,
            user_name = sender.username if sender.username is not None else "",
            first_name = sender.first_name,
            last_name = sender.last_name if sender.last_name is not None else '',
            level=0,
            exp=1,
        )
        
        await rankuser.save()
    else:
        stats.exp = stats.exp + 5 
        stats.level = math.floor((1 + math.sqrt(1 + (2 * stats.exp) / 3)) / 2)
        await stats.save()

EVENTS.append(NewMessage(func=allowedgroupfilter))
CALLBACKS.append(levelup)

def init_cog(bot:TelegramClient):
    for event,callback in zip(EVENTS,CALLBACKS):
        bot.add_event_handler(callback,event=event)

    print(f"Loaded {len(CALLBACKS)} event handlers from {__name__}")