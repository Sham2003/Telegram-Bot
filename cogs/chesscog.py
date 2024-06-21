import os
import tempfile

from chess import Board, svg, InvalidMoveError
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl import types
from models.dbmodels import AllowedGroup, ChessGame
from mfilters import agfilter, chfilter, adminfilter

EVENTS = []
CALLBACKS = []


def board2image(board: Board):
    with tempfile.TemporaryFile(suffix='.svg', dir='.', delete=False) as f:
        f.write(svg.board(board, size=400).encode('utf-8'))
    drawing = svg2rlg(f.name)
    os.remove(f.name)
    with tempfile.NamedTemporaryFile(suffix='.png', dir='.', delete=False) as tmpfile:
        image_name = tmpfile.name
    if image_name is None:
        raise ValueError("Image name is none for chess board")
    renderPM.drawToFile(drawing, image_name, fmt="PNG")
    return image_name


async def startchess(event: NewMessage.Event):
    bot: TelegramClient = event.client
    if len(event.message.entities) <= 1:
        await event.reply("Mention a user or mention me but iam tough")
        return
    if type(event.message.entities[1]) not in [types.MessageEntityMention, types.MessageEntityMentionName]:
        await event.reply("Mention a user or mention me but iam tough")
        return
    u2 = -1
    user = None
    if isinstance(event.message.entities[1], types.MessageEntityMentionName):
        u2 = event.message.entities[1].user_id
        user = await bot.get_entity(u2)
    if isinstance(event.message.entities[1], types.MessageEntityMention):
        m = event.message.entities[1]
        user = await bot.get_entity(event.message.message[m.offset:m.offset + m.length])
        u2 = user.id
    if u2 == -1:
        await event.reply("Not a valid User ...")
        return
    MTEXT = "Hey <a href='tg://user?id={}'>{}</a>\n You have {} seconds to reply with yes"
    name = user.first_name + user.last_name if user.last_name is not None else ""
    ACCEPTED = False
    async with bot.conversation(event.chat_id) as conv:
        msgs = []
        m1 = await conv.send_message(MTEXT.format(u2, name, 10), parse_mode="HTML")
        msgs.append(m1)
        for i in range(9, 0, -1):
            try:
                m2 = await conv.get_reply(message=m1, timeout=1)
                msgs.append(m2)
                if str.lower(m2.message) == 'yes':
                    ACCEPTED = True
                    break
            except TimeoutError:
                pass
            await bot.edit_message(event.chat_id, m1, MTEXT.format(u2, name, i), parse_mode="HTML")
        await bot.delete_messages(event.chat_id, msgs)

    if not ACCEPTED:
        await bot.send_message(event.chat_id, "The request is declined...")
        return
    u1 = event.message.from_id.user_id
    g = ChessGame(
        clan_id=event.chat_id,
        p1=u1,
        p2=u2
    )

    group = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id)
    if group.gid != '':
        await bot.send_message(event.chat_id, "Already a game is happening !!!")
        await g.delete()
        return
    group.gid = g.gid
    await group.save()
    await g.save()
    await bot.send_message(event.chat_id, "The challenge is accepted !!!")


EVENTS.append(NewMessage(pattern=r'/(play|start|)(ch|chess)(.*)', func=agfilter))
CALLBACKS.append(startchess)


async def show_board(event: NewMessage.Event):
    bot = event.client
    group = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id)
    game = await ChessGame.find_one(ChessGame.gid == group.gid)
    board = Board(fen=game.fen)
    file = board2image(board)
    await bot.send_file(event.chat_id, file)
    os.remove(file)


EVENTS.append(NewMessage(pattern=r'/board', func=chfilter))
CALLBACKS.append(show_board)


async def valid_moves(event: NewMessage.Event):
    bot = event.client
    group = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id)
    game = await ChessGame.find_one(ChessGame.gid == group.gid)
    board = Board(fen=game.fen)
    moves = board.legal_moves
    text = "<b>Valid Moves:</b>\n"
    for move in moves:
        text += board.san(move) + ','
    await bot.send_message(event.chat_id, text, parse_mode="HTML")


EVENTS.append(NewMessage(pattern=r'/validmoves', func=chfilter))
CALLBACKS.append(valid_moves)


async def move_maker(event: NewMessage.Event):
    bot = event.client
    group = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id)
    game = await ChessGame.find_one(ChessGame.gid == group.gid)
    user_id = event.message.from_id.user_id
    board = Board(fen=game.fen)
    if ((board.turn and user_id != game.p1)
            or (not board.turn and user_id != game.p2)):
        await bot.send_message(event.chat_id, "This is not your turn to play !!!")
        return
    san = event.pattern_match.group(1).strip()
    try:
        move = board.parse_san(san)
        board.push(move)
        game.moves.append(move.uci())
        game.fen = board.fen()
    except ValueError:
        bot.send_message(event.chat_id, f"<a href='tg://user?id={user_id}'>@Player</a>This is not a valid move....", parse_mode="HTML")
        return
    file = board2image(board)
    await bot.send_file(event.chat_id, file)
    os.remove(file)
    outcome = board.outcome(claim_draw=True)
    if outcome is not None:
        if outcome.result() == '1-0' or outcome.result() == '0-1':
            await bot.send_message(event.chat_id, "Game is over You have won!!!")
            game.winner = int(outcome.result()[0])
            game.gameover = True
            group.gid = ''
    await game.save()
    await group.save()


EVENTS.append(NewMessage(pattern=r'/move(.*)', func=chfilter))
CALLBACKS.append(move_maker)


async def pause_game(event: NewMessage.Event):
    bot = event.client
    group = await AllowedGroup.find_one(AllowedGroup.clan_id == event.chat_id)
    game = await ChessGame.find_one(ChessGame.gid == group.gid)
    user_id = event.message.from_id.user_id
    if not (game.p1 == user_id or game.p2 == user_id) and not adminfilter(event):
        bot.send_message(event.chat_id, "You cannot pause the game!!!")
        return
    other_id = game.p1
    if game.p1 == user_id:
        other_id = game.p2
    user = await bot.get_entity(other_id)
    RTEXT = "Hey <a href='tg://user?id={}'>{}</a>\nReply with yes to pause within {} seconds"
    name = user.first_name + user.last_name if user.last_name is not None else ""
    ACCEPTED = False
    async with bot.conversation(event.chat_id) as conv:
        msgs = []
        m1 = await conv.send_message(RTEXT.format(other_id, name, 10), parse_mode="HTML")
        msgs.append(m1)
        for i in range(9, 0, -1):
            try:
                m2 = await conv.get_reply(message=m1, timeout=1)
                msgs.append(m2)
                if str.lower(m2.message) == 'yes':
                    ACCEPTED = True
                    break
            except TimeoutError:
                pass
            await bot.edit_message(event.chat_id, m1, RTEXT.format(other_id, name, i), parse_mode="HTML")
        await bot.delete_messages(event.chat_id, msgs)

    if not ACCEPTED:
        await bot.send_message(event.chat_id, "The request is declined...")
        return
    group.gid = ''
    await group.save()
    game.gameover = True
    await game.save()
    await bot.send_message(event.chat_id, "The game is stopped..")

EVENTS.append(NewMessage(pattern=r'/stop', func=chfilter))
CALLBACKS.append(pause_game)

def init_cog(bot: TelegramClient):
    for event, callback in zip(EVENTS, CALLBACKS):
        bot.add_event_handler(callback, event=event)

    print(f"Loaded {len(CALLBACKS)} event handlers from {__name__}")
