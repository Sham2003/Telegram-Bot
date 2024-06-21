import asyncio
from models.dbmodels import AllowedGroup
from telethon.tl.types import ChannelParticipantsAdmins


async def allowedgroupfilter(e):
    result = await AllowedGroup.find_one(AllowedGroup.clan_id == e.chat_id)
    if result is not None:
        return True
    return False

async def adminfilter(e):
    bot = e.client
    async for user in bot.iter_participants(e.chat_id,filter=ChannelParticipantsAdmins):
        if user.id == e.from_id.user_id:
            return True
    return False


async def agfilter(e):
    result = await AllowedGroup.find_one(AllowedGroup.clan_id == e.chat_id)
    if result is not None:
        if result.gid == '' and result.chess:
            return True
    return False

async def chfilter(e):
    result = await AllowedGroup.find_one(AllowedGroup.clan_id == e.chat_id)
    if result is not None:
        if result.gid != '' and result.chess:
            return True
    return False

def mfilter(*filters):
    async def merged(e):
        key = True
        for filter in filters:
            result = await filter(e)
            key = result and key
            if key == False:
                break
        return key
    return merged
