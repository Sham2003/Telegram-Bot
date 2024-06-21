
from telethon import TelegramClient
from telethon.events import NewMessage
from models.dbmodels import AllowedGroup
from mfilters import adminfilter,allowedgroupfilter,mfilter
import asyncio

EVENTS = []
CALLBACKS = []



async def authhandler(event:NewMessage.Event):
    result = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id)
    if result is not None:
        await event.reply("Already Authenticated")
    else:
        chat = await event.get_chat()
        await AllowedGroup(clan_id=event.chat_id,clan_name=chat.title).insert()
        await event.reply("Authenticated this group")

EVENTS.append(NewMessage(pattern='/authorize',func=adminfilter))
CALLBACKS.append(authhandler)


async def unauthhandler(event:NewMessage.Event):
    result = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id)
    if result is None:
        await event.reply("Not Authenticated in the first place !!!!")
    else:
        await result.delete()
        await event.reply("Unauthenticated this group")


EVENTS.append(NewMessage(pattern='/unauthorize',func=adminfilter))
CALLBACKS.append(unauthhandler)


async def aqhandler(event:NewMessage.Event):
    result = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id )
    if hasattr(result,'quiz') and getattr(result,'quiz'):
        await event.reply("Already subscribed !!!")
    elif result is not None:
        result.quiz = True
        await result.save()
        await event.reply("Hourly Quiz subscribed !!!")



EVENTS.append(NewMessage(pattern='/askquiz',func=mfilter(allowedgroupfilter,adminfilter)))
CALLBACKS.append(aqhandler)


async def noqhandler(event:NewMessage.Event):
    result = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id)
    if not result.quiz:
        await event.reply("Already usubscribed !!!")
    else:
        result.quiz = False
        await result.save()
        await event.reply("Nomore quiz !!!")

EVENTS.append(NewMessage(pattern='/noaskquiz',func=mfilter(allowedgroupfilter,adminfilter)))
CALLBACKS.append(noqhandler)

async def chessauthhandler(event:NewMessage.Event):
    result = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id )
    if result.chess:
        await event.reply("Already subscribed !!!")
    else:
        result.chess = True
        await result.save()
        await event.reply("Now you can play chess !!!")



EVENTS.append(NewMessage(pattern='/authchess',func=mfilter(allowedgroupfilter,adminfilter)))
CALLBACKS.append(chessauthhandler)


async def nochesshandler(event:NewMessage.Event):
    result = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id)
    if not result.quiz:
        await event.reply("Already usubscribed !!!")
    else:
        result.chess = False
        await result.save()
        await event.reply("No more chess !!!")

EVENTS.append(NewMessage(pattern='/unauthchess',func=mfilter(allowedgroupfilter,adminfilter)))
CALLBACKS.append(nochesshandler)

def init_cog(bot:TelegramClient):
    for event,callback in zip(EVENTS,CALLBACKS):
        bot.add_event_handler(callback,event=event)

    print(f"Loaded {len(CALLBACKS)} event handlers from {__name__}")