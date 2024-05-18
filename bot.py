import random
import threading
import time
import telebot
from telebot.types import *
from sympy import *
import pymongo
from quotebot import Quote
from CHEMBOT import findbyquery
from quizbot import Quizzer
import datetime
from latextoimage import latextourl
import os
import chess
from stockfish import Stockfish
import urllib
from botconfig import *

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')


FRIENDS = ["FRIEND1"] #Enter friends id

client = pymongo.MongoClient(MONGOURL)

level_cluster = client['Telegram']['Levelling']
poll_cluster = client['Telegram']['Polling']
other_cluster = client['Telegram']['others']
chess_cluster = client['Telegram']['Chess']
user_cluster = client['Telegram']['User']
reply_cluster = client['Telegram']['Replyer']


ALLOWED_GROUPS = []

def updateallowedgroups():
    global ALLOWED_GROUPS
    required_collection = other_cluster.find_one({'name': "Allowed_groups"})
    if required_collection is not None:
        ALLOWED_GROUPS = required_collection['clan_names']

updateallowedgroups()

MYFUNC = lambda message: message.chat.type in ["group", "supergroup"] and message.chat.id in ALLOWED_GROUPS
chess_bot = Stockfish(path=STOCKFISH_PATH,
                      parameters={"Threads": 2, "Minimum Thinking Time": 25})





def setgameboard(clan_id):
    clan = chess_cluster.find_one({'clan_id': clan_id})
    if clan is not None and clan['status'] == "ALIVE":
        current_game = clan['current_game_no']
        game = clan['games'][current_game]
        board = chess.Board(game['fen'])
        return board, board.turn, game['bot_game']
    else:
        return None, None, None


@bot.inline_handler(lambda query: len(query.query) > 0)
def textanswer(query):
    tobefound = query.query
    print("Searching for ", query.query)
    try:
        results = findbyquery(tobefound)
        print(results)
        dumy = []
        for i, result in enumerate(results):
            dumy.append(
                InlineQueryResultArticle(
                    id=i, title=result['Name'], thumb_url=result['Url'],
                    input_message_content=InputTextMessageContent(
                        result['Url'] + "?record_type=2d" + "\n" + result['Description'],
                        disable_web_page_preview=False)))
        bot.answer_inline_query(query.id, dumy, cache_time=20)
    except Exception as e:
        print(e)
        dumy = InlineQueryResultArticle(
            id='1', title='Not Found Give a Correct Query',
            input_message_content=InputTextMessageContent("Nothing"))
        bot.answer_inline_query(query.id, [dumy])


@bot.message_handler(commands=["start"])
def send_welcome(message: Message):
    if message.chat.type in ["group", "supergroup"] and message.chat.id in ALLOWED_GROUPS:
        if message.from_user.first_name == "Sham":
            bot.reply_to(message, "Welcome Master")
        if message.from_user.username in FRIENDS and message.from_user.first_name == "🔥Saran🔥":
            bot.reply_to(message, "Hello My friend")
        if message.from_user.username == "@sabari_h":
            bot.reply_to(message, "Solluda echa")
    elif message.chat.type == "private":
        bot.reply_to(message, "I can only be used in a group")
    else:
        bot.reply_to(message, "Nothing gonna happen")


@bot.message_handler(commands=["help"], func=MYFUNC)
def helper(message: Message):
    query = telebot.util.extract_arguments(message.text).strip()
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
        bot.send_message(message.chat.id, help_description[query])
    else:
        help_message = "<b><u>Command List</u></b> <pre> \n"
        for i in COMMAND_LIST:
            help_message += i + "\n"
        help_message += "</pre> To know more about the command <i> /help [command_name]</i> "
        bot.send_message(chat_id=message.chat.id, text=help_message, parse_mode="HTML")


@bot.message_handler(commands=["rank"], func=MYFUNC)
def mylevel(message):
    chat_id = message.from_user.id
    stats = level_cluster.find_one({'user_id': chat_id})
    if stats is None:
        bot.reply_to(message, "Currently you are not in the rank list! Send some messages and try again")
    else:
        bot.reply_to(message, f"Currently you are in Level<b>{stats['Level']}</b> ! Keep up ")


@bot.message_handler(commands=["leaderboard"], func=MYFUNC)
def leaderboard(message):
    LDRSTRING = "<b><u> TOP RANKINGS </u></b>\n"
    result = level_cluster.find().sort('Exp', pymongo.DESCENDING)
    for j, i in enumerate(result):
        LDRSTRING += f"{j + 1}.<a href='tg://user?id={i['user_id']}'>{i['Name']}</a> = {i['Exp']} \n "
    bot.send_message(message.chat.id, LDRSTRING)


@bot.message_handler(commands=["calc", "compute"], func=MYFUNC)
def calculate(message: Message):
    try:
        expr = telebot.util.extract_arguments(message.text)
        answer = latex(sympify(expr))
        bot.reply_to(message, f"{latextourl(answer)}")
    except Exception:
        bot.reply_to(message, "Invalid Expression")


@bot.message_handler(commands=['quiz', 'randquiz'], func=lambda message: message.from_user.id == 1591179954)
def quizsender(message: Message):
    quiz_question = Quizzer().quiz_question
    options = quiz_question["OPTIONS"]
    answer = quiz_question["CORRECT"]
    poll = bot.send_poll(chat_id=message.chat.id,
                         question=quiz_question["Question"],
                         options=quiz_question["OPTIONS"],
                         allows_multiple_answers=quiz_question["MULTIPLE ANSWER"],
                         is_anonymous=False,
                         explanation=f"The correct answer is {answer}"
                         )
    poll_cluster.insert_one({
        'poll_id': poll.poll.id,
        'chat_id': message.chat.id,
        'answer': answer,
        'options': options,
        'multians': quiz_question["MULTIPLE ANSWER"]
    })


@bot.message_handler(commands=['authorize'], func=lambda message: message.from_user.id == 1591179954)
def authentication(message: Message):
    global ALLOWED_GROUPS
    auth_groups = other_cluster.find_one({'name': "Allowed_groups"})
    if message.chat.id in auth_groups['clan_names']:
        bot.reply_to(message, "ALready Authenticated")
    else:
        other_cluster.update_one({'name': "Allowed_groups"}, {'$addToSet': {'clan_names': message.chat.id}})
        bot.reply_to(message, "Authenticated successfully")
        raise ValueError("Rerunning")


@bot.message_handler(commands=['unauthorize'], func=lambda message: message.from_user.id == 1591179954)
def unauthentication(message: Message):
    global ALLOWED_GROUPS
    auth_groups = other_cluster.find_one({'name': "Allowed_groups"})
    if not message.chat.id in auth_groups['clan_names']:
        bot.reply_to(message, "First u have to authorize and then deauthorize")
    else:
        other_cluster.update_one({'name': "Allowed_groups"}, {'$pull': {'clan_names': message.chat.id}})
        bot.reply_to(message, "Unauthenticated successfully")
        raise ValueError("Rerunning")


@bot.message_handler(commands=["quote"], func=MYFUNC)
def sendquote(message: Message):
    try:
        query = telebot.util.extract_arguments(message.text)
        quotes = Quote(query)
        selected_quote = random.choice(quotes)
        quote_message = f"{selected_quote['Quote']} \n \t-<b><u>{selected_quote['Author']}</u></b>"
        bot.send_message(message.chat.id, quote_message)
    except Exception:
        bot.send_message(message.chat.id, "Invalid Query")


@bot.message_handler(commands=['askquizhere'], func=MYFUNC)
def askquizhere(message: Message):
    found = other_cluster.find_one({'name': "quiz_groups"})
    ids = found["Allowed"]
    if message.chat.id in ids:
        bot.reply_to(message, "Already subscribed !!!")
    else:
        other_cluster.update_one({'name': "quiz_groups"}, {"$addToSet": {"Allowed": message.chat.id}})
        bot.reply_to(message, "Already subscribed")


@bot.message_handler(commands=['stopquizhere'], func=MYFUNC)
def stopquizhere(message: Message):
    found = other_cluster.find_one({'name': "quiz_groups"})
    ids = found["Allowed"]
    if message.chat.id not in ids:
        bot.reply_to(message, "Not in the subscriber list")
    else:
        other_cluster.update_one({'name': "quiz_groups"}, {"$pull": {"Allowed": message.chat.id}})
        bot.reply_to(message, "succesfully unsubscribed")


@bot.message_handler(commands=['integrators'], func=MYFUNC)
def sendhelfuncs(message: Message):
    Help_func_message = """<code> <b>Allowed Functions</b>:
    <u>Note: All should be Case Sensitive </u>
    \n <i>root(x,n)</i> : The n-th root of arg like root(x,2) for square root 
    \n <i>Abs(x)</i> : The absolute value function |x| 
    \n <i>sqrt(x)</i> : The square root function
    \n <i>log(x)</i> : The natural log function
    \n <i>log(x,base)</i>: The log function for other bases
    \n <i>floor(x)</i>: The greatest integer function
    \n <i>sin(x)</i>: The sine function 
    \n <i>cos(x)</i>: The cosine function
    \n <i>tan(x)</i>:The tangent function 
    \n <i>sec(x)</i>: The secant function
    \n <i>csc(x)</i>:The cosecant function
    \n <i>cot(x)</i>: The cotangent function
    \n <i>asin(x)</i>: The inverse sine function
    \n <i>acos(x)</i>: The inverse cosine function
    \n <i>atan(x)</i>: The inverse cotangent function
    \n <i>asec(x)</i> : The inverse secant function
    \n <i>acsc(x)</i> : The inverse cosecant function
    \n <i>acot(x)</i> : The inverse cotangent function
    \n <i>oo</i> : For infinity
    \n <i>pi</i> : For pi value like pi/3,pi/6
    \n <i>E</i> : For e value like E**2,2*E
    </code>"""
    bot.send_message(message.chat.id, Help_func_message)


@bot.message_handler(commands=['integrate'], func=MYFUNC)
def firstintegration(message: Message):
    message_text = telebot.util.extract_arguments(message.text)
    args = message_text.split()
    args_dict = dict()
    try:
        for i in args:
            print(i, i.split('='))
            key, value = i.split('=')
            if key == 'expr':
                args_dict['Expression'] = value
            if key == 'ul':
                if value.__contains__("oo"):
                    args_dict['UpperLimit'] = oo
                elif value.__contains__('pi'):
                    args_dict['UpperLimit'] = sympify(value)
                elif value.__contains__('e') or value.__contains__('E'):
                    value = value.replace('e', 'E')
                    args_dict['UpperLimit'] = sympify(value)
                else:
                    args_dict['UpperLimit'] = sympify(value)
            if key == 'll':
                if value.__contains__("oo"):
                    args_dict['LowerLimit'] = oo
                elif value.__contains__('pi'):
                    args_dict['LowerLimit'] = sympify(value)
                elif value.__contains__('e') or value.__contains__('E'):
                    value = value.replace('e', 'E')
                    args_dict['LowerLimit'] = sympify(value)
                else:
                    args_dict['LowerLimit'] = sympify(value)
    except Exception as error:
        bot.send_message(message.chat.id, error)
    print(args_dict)
    if 'Expression' in args_dict.keys():
        if 'UpperLimit' in args_dict.keys() and 'LowerLimit' in args_dict.keys():
            try:
                x = Symbol('x')
                expr = sympify(args_dict['Expression'])
                latex_arg = latex(integrate(expr, (x, args_dict['LowerLimit'], args_dict['UpperLimit'])))
                bot.send_photo(message.chat.id, latextourl(latex_arg))
            except Exception as error:
                print(error)
        else:
            try:
                x = Symbol('x')
                expr = sympify(args_dict['Expression'])
                latex_arg = latex(integrate(expr)) + ' + C'
                bot.send_photo(message.chat.id, latextourl(latex_arg))
            except Exception as error:
                print(error)
    else:
        bot.send_message(message.chat.id, "Use it correctly Check help")


@bot.message_handler(commands=['currentgame'], func=MYFUNC)
def get_current_game(message: Message):
    clan = chess_cluster.find_one({'clan_id': message.chat.id})
    if not clan is None and clan['status'] == "DEAD":
        bot.send_message(message.chat.id, 'Currently No Games Played')
    elif clan is not None and clan['status'] == "ALIVE":
        game = clan['games'][clan['current_game_no']]
        player1 = user_cluster.find_one({'user_id': game['players']["WHITE"]})
        player2 = user_cluster.find_one({'user_id': game['players']["BLACK"]})
        gametime = game['gametime']
        gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
        now: datetime.timedelta = datetime.datetime.now() - gamestime
        gametime += now.total_seconds()

        info_string = f"""
        \n CHESS GAME \n <b>Name</b>: {game['name']} 
        \n {player1['firstname']} Versus {player2['firstname']}
        \n <b>Gametime</b>: {gametime / 3600:.2f} hrs
        \n <b> Total Moves</b>: {len(game['moves'])}"""
        bot.send_message(message.chat.id, info_string)
        chess_cluster.update_one({'clan_id': message.chat.id},
                                 {'$set': {'games.%[game].time': datetime.datetime.now().strftime('%D %H %M %S')},
                                  '$set': {'games.%[game].gametime': gametime}},
                                 array_filters=[{'game.unique_id': game['unique_id']}])


@bot.message_handler(commands=['playchesswith', 'startchess'], func=MYFUNC)
def startchess(message: Message):
    text = telebot.util.extract_arguments(message.text)
    if not text == '' and len(text) > 2:
        if text.startswith('@'):
            text = text[1:]
        all_users = user_cluster.find()
        found_user = None
        for user in all_users:
            if user['username'] is not None and user['firstname'] is not None:
                if text in user['username'] or text in user['firstname']:
                    found_user = user
            elif user['username'] is None:
                if text in user['firstname']:
                    found_user = user
            else:
                found_user = None
        else:
            if text == BOT['username']:
                found_user = BOT
        if not found_user is None:
            clan = chess_cluster.find_one({'clan_id': message.chat.id})
            if clan is None:
                if found_user == BOT:
                    game = {
                        'unique_id': "".join(random.choices('qwertyuiopasdfghjklzxcvbnm1234567890', k=9)),
                        'name': f"{message.chat.title}-{1}",
                        'players': {"WHITE": message.from_user.id, "BLACK": BOT['id']},
                        'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                        'moves': [],
                        'bot_game': True,
                        'gameover': False,
                        'outcome': None,
                        'gametime': 0,
                        'winner': None,
                        'time': datetime.datetime.now().strftime('%D %H %M %S')
                    }
                    chess_cluster.insert_one({
                        'clan_id': message.chat.id,
                        'game_count': 1,
                        'games_finished': 0,
                        'status': 'ALIVE',
                        'requests': 0,
                        'current_game_no': 0,
                        'games': [game]
                    })
                    url = 'https://chessboardimage.com/{0}.png'.format(
                        chess.Board().fen().replace(' ', '%20'))
                    bot.send_photo(message.chat.id, url, caption="Chess Board Initiated")
                else:
                    mtbs = f"The <a href='tg://user?id={found_user['user_id']}'>other player</a> must also accept .He must reply to this message with (/yes or /accept) or (/no or /decline)"
                    msg = bot.send_message(message.chat.id, mtbs)
                    reply_cluster.insert_one({
                        'unique_id': "".join(random.choices('qwertyuiopasdfghjklzxcvbnm1234567890', k=9)),
                        'chat': message.chat.id,
                        'who': found_user['user_id'],
                        'reason': "CHESS_START",
                        'msg_id': msg.message_id,
                        'gametime': 0,
                        'time': datetime.datetime.now().strftime('%H:%M:%S'),
                        'other': message.from_user.id
                    })
                    chess_cluster.insert_one({
                        'clan_id': message.chat.id,
                        'game_count': 0,
                        'games_finished': 0,
                        'status': 'DEAD',
                        'requests': 1,
                        'current_game_no': None,
                        'games': []
                    })
            else:
                if clan['status'] == 'ALIVE':
                    bot.send_message(message.chat.id, "Already Games running")
                elif found_user == BOT:
                    nowth = clan['game_count'] + 1
                    game = {
                        'unique_id': "".join(random.choices('qwertyuiopasdfghjklzxcvbnm1234567890', k=9)),
                        'name': f"{message.chat.title}-{nowth}",
                        'players': {"WHITE": message.from_user.id, "BLACK": BOT['id']},
                        'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                        'moves': [],
                        'bot_game': True,
                        'gameover': False,
                        'outcome': None,
                        'gametime': 0,
                        'winner': None,
                        'time': datetime.datetime.now().strftime('%D %H %M %S')
                    }
                    chess_cluster.update_one({'clan_id': message.chat.id}, {'$inc': {'game_count': 1}})
                    chess_cluster.update_one({'clan_id': message.chat.id}, {'$addToSet': {'games': game}})
                    chess_cluster.update_one({'clan_id': message.chat.id},
                                             {'$set': {'current_game_no': nowth - 1},
                                              '$set': {'status': "ALIVE"}
                                              })
                    url = 'https://chessboardimage.com/{0}.png'.format(
                        chess.Board().fen().replace(' ', '%20'))
                    bot.send_photo(message.chat.id, url, caption="Chess Board Initiated")
                else:
                    mtbs = f"The <a href='tg://user?id={found_user['user_id']}'>other player</a> must also accept .He must reply to this message with (/yes or /accept) or (/no or /decline)"
                    msg = bot.send_message(message.chat.id, mtbs)
                    reply_cluster.insert_one({
                        'unique_id': "".join(random.choices('qwertyuiopasdfghjklzxcvbnm1234567890', k=9)),
                        'chat': message.chat.id,
                        'who': found_user['user_id'],
                        'reason': "CHESS_START",
                        'msg_id': msg.message_id,
                        'time': datetime.datetime.now().strftime('%H:%M:%S'),
                        'other': message.from_user.id
                    })
                    chess_cluster.update_one({'clan_id': message.chat.id}, {'$inc': {'requests': 1}})
    else:
        bot.send_message(message.chat.id, "Mention a user or mention me but iam tough")


@bot.message_handler(commands=['stopchess', 'pausechess'], func=MYFUNC)
def stopgame(message: Message):
    clan = chess_cluster.find_one({'clan_id': message.chat.id})
    if clan is None:
        pass
    elif clan['status'] == 'DEAD':
        bot.send_message(message.chat.id, 'CURRENTLY NO GAMES ALIVE')
    else:
        game = clan['games'][clan['current_game_no']]
        players: dict = game['players']
        is_bot_game = game['bot_game']
        if is_bot_game:
            if message.from_user.id == players["WHITE"]:
                chess_cluster.update_one({'clan_id': message.chat.id}, {'$set': {'status': False}})
                bot.send_message(message.chat.id, "Game Stopped")
            elif message.from_user.id == 1591179954:
                gametime = game['gametime']
                gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                now: datetime.timedelta = datetime.datetime.now() - gamestime
                gametime += now.total_seconds()
                chess_cluster.update_one({'clan_id': message.chat.id},
                                         {'$set': {'games.$[id].gametime': gametime},
                                          '$set': {'games.$[id].time': None},
                                          '$set': {'status': "DEAD"},
                                          '$set': {'current_game_no': None}},
                                         array_filters=[{'id.unique_id': game['unique_id']}])
                bot.send_message(message.chat.id, "Game Stopped by BOT OWNER")
            else:
                ownercheck: ChatMember = bot.get_chat_member(message.chat.id, message.from_user.id)
                if ownercheck.status == 'creator':
                    gametime = game['gametime']
                    gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                    now: datetime.timedelta = datetime.datetime.now() - gamestime
                    gametime += now.total_seconds()
                    chess_cluster.update_one({'clan_id': message.chat.id},
                                             {'$set': {'games.$[id].gametime': gametime},
                                              '$set': {'games.$[id].time': None},
                                              '$set': {'status': "DEAD"},
                                              '$set': {'current_game_no': None}},
                                             array_filters=[{'id.unique_id': game['unique_id']}])
                    bot.send_message(message.chat.id, "Game Stopped by Group OWNER")
                else:
                    bot.send_message(message.chat.id,
                                     "Game could only be stopped by players or bot owner or group owner")
        else:
            if message.from_user.id in players.values():
                mtbs = "The Other player must also accept \n Reply to this message with (/yes,/accept) or (/no,decline)"
                if message.from_user.id == players["WHITE"]:
                    msg = bot.send_message(message.chat.id, mtbs)
                    reply_cluster.insert_one({
                        'unique_id': "".join(random.choices('qwertyuiopasdfghjklzxcvbnm1234567890', k=9)),
                        'chat': message.chat.id,
                        'who': players["BLACK"],
                        'reason': "CHESS_TERMINATE",
                        'msg_id': msg.message_id,
                        'time': datetime.datetime.now().strftime('%H:%M:%S'),
                        'game_name': game['unique_id']
                    })
                    chess_cluster.update_one({'clan_id': message.chat.id}, {'$inc': {'requests': 1}})
                elif message.from_user.id == players["BLACK"]:
                    msg = bot.send_message(message.chat.id, mtbs)
                    reply_cluster.insert_one({
                        'unique_id': "".join(random.choices('qwertyuiopasdfghjklzxcvbnm1234567890', k=9)),
                        'chat': message.chat.id,
                        'who': players["WHITE"],
                        'reason': "CHESS_TERMINATE",
                        'msg_id': msg.message_id,
                        'time': datetime.datetime.now().strftime('%H:%M:%S'),
                        'game_name': game['unique_id']

                    })
                    chess_cluster.update_one({'clan_id': message.chat.id}, {'$inc': {'requests': 1}})
                else:
                    pass
            elif message.from_user.id == 1591179954:
                chess_cluster.update_one({'clan_id': message.chat.id}, {'$set': {'status': False}})
                bot.send_message(message.chat.id, "Game Stopped by BOT OWNER")
            else:
                ownercheck: ChatMember = bot.get_chat_member(message.chat.id, message.from_user.id)
                if ownercheck.status == 'creator':
                    chess_cluster.update_one({'clan_id': message.chat.id}, {'$set': {'status': False}})
                    bot.send_message(message.chat.id, "Game Stopped by Group OWNER")
                else:
                    bot.send_message(message.chat.id,
                                     "Game could only be stopped by players or bot owner or group owner")


@bot.message_handler(commands=['yes', 'accept', 'no', 'decline'], func=MYFUNC)
def acceptreply(message: Message):
    if not message.reply_to_message is None:
        replys = reply_cluster.find({'chat': message.chat.id})
        for reply in replys:
            if reply['msg_id'] == message.reply_to_message.id:
                if message.from_user.id == reply['who']:
                    if reply['reason'] == "CHESS_TERMINATE":
                        if message.text == '/yes' or message.text == '/accept':
                            clan = chess_cluster.find_one({'clan_id': message.chat.id})
                            if clan['status'] == "ALIVE":
                                game = clan['games'][clan['current_game_no']]
                                gametime = game['gametime']
                                gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                                now: datetime.timedelta = datetime.datetime.now() - gamestime
                                gametime += now.total_seconds()
                                chess_cluster.update_one({'clan_id': message.chat.id},
                                                         {'$set': {'games.$[id].gametime': gametime},
                                                          '$set': {'games.$[id].time': None},
                                                          '$set': {'status': "DEAD"},
                                                          '$set': {'current_game_no': None}},
                                                         array_filters=[{'id.unique_id': game['unique_id']}])
                                bot.send_message(message.chat.id, "Game Stopped")
                            reply_cluster.delete_one({'unique_id': reply['unique_id']})
                        else:
                            bot.send_message(message.chat.id, "Request declined")
                            reply_cluster.delete_one({'unique_id': reply['unique_id']})
                    elif reply['reason'] == "CHESS_START":
                        clan = chess_cluster.find_one({'clan_id': message.chat.id})
                        if not clan['status'] == 'ALIVE':
                            if message.text == '/yes' or message.text == '/accept':
                                chess_cluster.update_one({'clan_id': message.chat.id}, {'$set': {'status': 'ALIVE'}})
                                nowth = clan['game_count'] + 1
                                game = {
                                    'unique_id': "".join(random.choices('qwertyuiopasdfghjklzxcvbnm', k=9)),
                                    'name': f"{message.chat.title}-{nowth}",
                                    'players': {"WHITE": reply['other'], "BLACK": message.from_user.id},
                                    'fen': chess.Board().fen(),
                                    'moves': [],
                                    'bot_game': False,
                                    'gameover': False,
                                    'outcome': None,
                                    'winner': None,
                                    'gametime': 0,
                                    'time': datetime.datetime.now().strftime('%D %H %M %S')
                                }
                                chess_cluster.update_one({'clan_id': message.chat.id}, {'$inc': {'game_count': 1}})
                                chess_cluster.update_one({'clan_id': message.chat.id}, {'$addToSet': {'games': game}})
                                chess_cluster.update_one({'clan_id': message.chat.id},
                                                         {'$set': {'current_game_no': nowth - 1}})
                                chess_cluster.update_one({'clan_id': message.chat.id}, {'$inc': {'requests': -1}})
                                url = 'https://chessboardimage.com/{0}.png'.format(
                                    chess.Board().fen().replace(' ', '%20'))
                                bot.send_photo(message.chat.id, url, caption="Chess Board Initiated")
                                reply_cluster.delete_one({'unique_id': reply['unique_id']})
                            elif message.text == '/no' or message.text == '/decline':
                                bot.send_message(message.chat.id, "Request Declined")
                                reply_cluster.delete_one({'unique_id': reply['unique_id']})
                                chess_cluster.update_one({'clan_id': message.chat.id}, {'$inc': {'requests': -1}})
                            else:
                                pass


@bot.message_handler(commands=['makemove', 'movepiece','mkm'], func=MYFUNC)
def movemaker(message: Message):
    clan = chess_cluster.find_one({'clan_id': message.chat.id})
    if not clan is None and clan['status'] == 'ALIVE':
        board, turn, botgame = setgameboard(message.chat.id)
        if not botgame:
            if turn == chess.WHITE:
                game = clan['games'][clan['current_game_no']]
                if message.from_user.id == game['players']['WHITE']:
                    move = telebot.util.extract_arguments(message.text)
                    try:
                        move__ = board.parse_san(move)
                        found = move__ in board.legal_moves
                    except:
                        found = False
                    if found:
                        board.push(move__)
                        chess_cluster.update_one({'clan_id': message.chat.id},
                                                 {'$addToSet': {'games.$[id].moves': move__.uci()},
                                                  '$set': {'games.$[id].fen': board.fen()}},
                                                 array_filters=[{"id.unique_id": game['unique_id']}])
                        if board.is_game_over():
                            outcome = board.outcome()
                            players = game['players']
                            if outcome.winner == chess.WHITE:
                                user = user_cluster.find_one({'user_id': players["WHITE"]})
                                win_message = f"Congralutations {user['username']} , You Have won by Check Mate"
                                url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                                bot.send_photo(message.chat.id, url, caption=win_message)
                                gametime = game['gametime']
                                gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                                now: datetime.timedelta = datetime.datetime.now() - gamestime
                                gametime += now.total_seconds()
                                chess_cluster.update_one({'clan_id': message.chat.id},
                                                         {'$set': {'games.$[id].gameover': True,
                                                                   'games.$[id].winner': True,
                                                                   'games.$[id].gametime': gametime,
                                                                   'games.$[id].time': None,
                                                                   'status': "DEAD",
                                                                   'current_game_no': None},
                                                          '$inc': {'games_finished': 1}},
                                                         array_filters=[{'id.unique_id': game['unique_id']}])
                            if outcome.winner is None:
                                url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                                bot.send_photo(message.chat.id, url, caption="The game has ended in a draw")
                                gametime = game['gametime']
                                gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                                now: datetime.timedelta = datetime.datetime.now() - gamestime
                                gametime += now.total_seconds()
                                chess_cluster.update_one({'clan_id': message.chat.id},
                                                         {'$set': {'games.$[id].gameover': True,
                                                                   'games.$[id].winner': None,
                                                                   'games.$[id].gametime': gametime,
                                                                   'games.$[id].time': None,
                                                                   'status': "DEAD",
                                                                   'current_game_no': None},
                                                          '$inc': {'games_finished': 1}},
                                                         array_filters=[{'id.unique_id': game['unique_id']}])
                                chess_cluster.update_one({'clan_id': message.chat.id},
                                                         {'$set': {'games.$[id].gameover': True},
                                                          '$set': {'games.$[id].winner': None},
                                                          '$set': {'games.$[id].gametime': gametime},
                                                          '$set': {'games.$[id].time': None},
                                                          '$set': {'games.$[id].outcome': str(outcome.termination)},
                                                          '$set': {'status': "DEAD"},
                                                          '$set': {'current_game_no': None},
                                                          '$inc': {'games_finished': 1}},
                                                         array_filters=[{'id.unique_id': game['unique_id']}])
                        elif board.is_check():
                            url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                            user = user_cluster.find_one({'user_id': message.from_user.id})
                            bot.send_photo(message.chat.id, url, caption=f"CHECK made by '{user['username']}'")
                        else:
                            url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                            bot.send_photo(message.chat.id, url)
                    else:
                        bot.send_message(message.chat.id, "Neither a valid or legal move ,White Player")
                elif message.from_user.id == game['players']['BLACK']:
                    bot.send_message(message.chat.id, 'Not your turn ,Black Player')
                else:
                    bot.send_message(message.chat.id, 'who are you to make a move here')
            elif turn == chess.BLACK:
                game = clan['games'][clan['current_game_no']]
                if message.from_user.id == game['players']['BLACK']:
                    move = telebot.util.extract_arguments(message.text)
                    move__ = None
                    try:
                        move__ = board.parse_san(move)
                        found = move__ in board.legal_moves
                    except ValueError:
                        found = False
                    if found:
                        board.push(move__)
                        chess_cluster.update_one({'clan_id': message.chat.id},
                                                 {'$addToSet': {'games.$[id].moves': move__.uci()},
                                                  '$set': {'games.$[id].fen': board.fen()}},
                                                 array_filters=[{"id.unique_id": game['unique_id']}])
                        if board.is_game_over():
                            outcome = board.outcome()
                            players = game['players']
                            if outcome.winner == chess.WHITE:
                                user = user_cluster.find_one({'user_id': players["WHITE"]})
                                win_message = f"Congralutations {user['username']} , You Have won by Check Mate"
                                url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                                bot.send_photo(message.chat.id, url, caption=win_message)
                                gametime = game['gametime']
                                gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                                now: datetime.timedelta = datetime.datetime.now() - gamestime
                                gametime += now.total_seconds()
                                chess_cluster.update_one({'clan_id': message.chat.id},
                                                         {'$set': {'games.$[id].gameover': True},
                                                          '$set': {'games.$[id].winner': True},
                                                          '$set': {'games.$[id].gametime': gametime},
                                                          '$set': {'games.$[id].time': None},
                                                          '$set': {'status': "DEAD"},
                                                          '$set': {'current_game_no': None},
                                                          '$inc': {'games_finished': 1}},
                                                         array_filters=[{'id.unique_id': game['unique_id']}])
                            if outcome.winner is None:
                                url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                                bot.send_photo(message.chat.id, url, caption="The game has ended in a draw")
                                gametime = game['gametime']
                                gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                                now: datetime.timedelta = datetime.datetime.now() - gamestime
                                gametime += now.total_seconds()
                                chess_cluster.update_one({'clan_id': message.chat.id},
                                                         {'$set': {'games.$[id].gameover': True},
                                                          '$set': {'games.$[id].winner': None},
                                                          '$set': {'games.$[id].gametime': gametime},
                                                          '$set': {'games.$[id].time': None},
                                                          '$set': {'games.$[id].outcome': str(outcome.termination)},
                                                          '$set': {'status': "DEAD"},
                                                          '$set': {'current_game_no': None},
                                                          '$inc': {'games_finished': 1}},
                                                         array_filters=[{'id.unique_id': game['unique_id']}])
                        elif board.is_check():
                            url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                            user = user_cluster.find_one({'user_id': message.from_user.id})
                            bot.send_photo(message.chat.id, url, caption=f"CHECK made by '{user['username']}'")
                        else:
                            url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                            bot.send_photo(message.chat.id, url)
                    else:
                        bot.send_message(message.chat.id, "Neither a valid or legal move ,Black Player")
                elif message.from_user.id == game['players']['WHITE']:
                    bot.send_message(message.chat.id, 'Not your turn ,White Player')
                else:
                    bot.send_message(message.chat.id, 'who are you to make a move here')
            else:
                pass
        else:
            game = clan['games'][clan['current_game_no']]
            if message.from_user.id == game['players']['WHITE']:
                move = telebot.util.extract_arguments(message.text)
                try:
                    move__ = board.parse_san(move)
                    found = move__ in board.legal_moves
                except ValueError:
                    found = False
                if found:
                    board.push(move__)
                    chess_cluster.update_one({'clan_id': message.chat.id},
                                             {'$addToSet': {'games.$[id].moves': move__.uci()},
                                              '$set': {'games.$[id].fen': board.fen()}},
                                             array_filters=[{"id.unique_id": game['unique_id']}])
                    if board.is_game_over():
                        outcome = board.outcome()
                        players = game['players']
                        if outcome.winner == chess.WHITE:
                            user = user_cluster.find_one({'user_id': players["WHITE"]})
                            win_message = f"Congralutations {user['username']} , You Have Defeated Me"
                            url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                            bot.send_photo(message.chat.id, url, caption=win_message)
                            gametime = game['gametime']
                            gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                            now: datetime.timedelta = datetime.datetime.now() - gamestime
                            gametime += now.total_seconds()
                            chess_cluster.update_one({'clan_id': message.chat.id},
                                                     {'$set': {'games.$[id].gameover': True},
                                                      '$set': {'games.$[id].winner': True},
                                                      '$set': {'games.$[id].gametime': gametime},
                                                      '$set': {'games.$[id].time': None},
                                                      '$set': {'status': "DEAD"},
                                                      '$set': {'current_game_no': None},
                                                      '$inc': {'games_finished': 1}},
                                                     array_filters=[{'id.unique_id': game['unique_id']}])
                        if outcome.winner is None:
                            url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                            bot.send_photo(message.chat.id, url, caption="The game has ended in a draw")
                            gametime = game['gametime']
                            gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                            now: datetime.timedelta = datetime.datetime.now() - gamestime
                            gametime += now.total_seconds()
                            chess_cluster.update_one({'clan_id': message.chat.id},
                                                     {'$set': {'games.$[id].gameover': True},
                                                      '$set': {'games.$[id].winner': None},
                                                      '$set': {'games.$[id].gametime': gametime},
                                                      '$set': {'games.$[id].time': None},
                                                      '$set': {'games.$[id].outcome': str(outcome.termination)},
                                                      '$set': {'status': "DEAD"},
                                                      '$set': {'current_game_no': None},
                                                      '$inc': {'games_finished': 1}},
                                                     array_filters=[{'id.unique_id': game['unique_id']}])
                    elif board.is_check():
                        url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                        user = user_cluster.find_one({'user_id': message.from_user.id})
                        bot.send_photo(message.chat.id, url, caption=f"CHECK MADE BY {user['username']}")
                    else:
                        url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                        bot.send_photo(message.chat.id, url)
                    if not board.is_game_over():
                        time.sleep(5)
                        bot.send_message(message.chat.id, "NOW MY TURN")
                        chess_bot.set_fen_position(board.fen())
                        board.push(chess.Move.from_uci(chess_bot.get_best_move()))
                        chess_cluster.update_one({'clan_id': message.chat.id},
                                                 {'$addToSet': {'games.$[id].moves': move__.uci()},
                                                  '$set': {'games.$[id].fen': board.fen()}},
                                                 array_filters=[{"id.name": game['name']}])
                        if board.is_game_over():
                            outcome = board.outcome()
                            players = game['players']
                            if outcome.winner == chess.WHITE:
                                user = user_cluster.find_one({'user_id': players["WHITE"]})
                                win_message = f"Congralutations {user['username']} , You have defeated me"
                                url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                                bot.send_photo(message.chat.id, url, caption=win_message)
                                gametime = game['gametime']
                                gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                                now: datetime.timedelta = datetime.datetime.now() - gamestime
                                gametime += now.total_seconds()
                                chess_cluster.update_one({'clan_id': message.chat.id},
                                                         {'$set': {'games.$[id].gameover': True},
                                                          '$set': {'games.$[id].winner': True},
                                                          '$set': {'games.$[id].gametime': gametime},
                                                          '$set': {'games.$[id].time': None},
                                                          '$set': {'status': "DEAD"},
                                                          '$set': {'current_game_no': None},
                                                          '$inc': {'games_finished': 1}},
                                                         array_filters=[{'id.unique_id': game['unique_id']}])
                            elif outcome.winner == chess.BLACK:
                                user = user_cluster.find_one({'user_id': players["WHITE"]})
                                win_message = f"{user['username']} ,Haha!!! You Lost "
                                url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                                bot.send_photo(message.chat.id, url, caption=win_message)
                                gametime = game['gametime']
                                gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                                now: datetime.timedelta = datetime.datetime.now() - gamestime
                                gametime += now.total_seconds()
                                chess_cluster.update_one({'clan_id': message.chat.id},
                                                         {'$set': {'games.$[id].gameover': True},
                                                          '$set': {'games.$[id].winner': False},
                                                          '$set': {'games.$[id].gametime': gametime},
                                                          '$set': {'games.$[id].time': None},
                                                          '$set': {'games.$[id].outcome': "CHECKMATE"},
                                                          '$set': {'status': "DEAD"},
                                                          '$set': {'current_game_no': None},
                                                          '$inc': {'games_finished': 1}},
                                                         array_filters=[{'id.unique_id': game['unique_id']}])
                            else:
                                url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                                bot.send_photo(message.chat.id, url, caption="The game has ended in a draw")
                                gametime = game['gametime']
                                gamestime = datetime.datetime.strptime(game['time'], '%m/%d/%y %H %M %S')
                                now: datetime.timedelta = datetime.datetime.now() - gamestime
                                gametime += now.total_seconds()
                                chess_cluster.update_one({'clan_id': message.chat.id},
                                                         {'$set': {'games.$[id].gameover': True},
                                                          '$set': {'games.$[id].winner': None},
                                                          '$set': {'games.$[id].gametime': gametime},
                                                          '$set': {'games.$[id].time': None},
                                                          '$set': {'games.$[id].outcome': str(outcome.termination)},
                                                          '$set': {'status': "DEAD"},
                                                          '$set': {'current_game_no': None},
                                                          '$inc': {'games_finished': 1}},
                                                         array_filters=[{'id.unique_id': game['unique_id']}])
                        elif board.is_check():
                            url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                            bot.send_photo(message.chat.id, url, caption=f"CHECK made by me")
                        else:
                            url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
                            bot.send_photo(message.chat.id, url)
                else:
                    bot.send_message(message.chat.id, "Neither a valid or legal move ,White Player")
    else:
        bot.send_message(message.chat.id, "No Game, No move")


@bot.message_handler(commands=['helpmoves', 'legalmoves'], func=MYFUNC)
def get_moves(message: Message):
    board, turn, botgame = setgameboard(message.chat.id)
    if board is None and turn is None:
        bot.send_message(message.chat.id, 'No Games ,No suggestions')
    else:
        moves = list(map(lambda x: board.san(x), list(board.legal_moves)))
        moves_string = "<b><u>LEGAL MOVES</u></b> \n" + "\t".join(moves)
        bot.send_message(message.chat.id, moves_string)


@bot.message_handler(commands=['board'], func=MYFUNC)
def send_board(message: Message):
    board, turn, botgame = setgameboard(message.chat.id)
    if board is not None and turn is not None:
        url = 'https://chessboardimage.com/{0}.png'.format(board.fen().replace(' ', '%20'))
        bot.send_photo(message.chat.id, url)


@bot.message_handler(func=MYFUNC, content_types=CONTENT_TYPES)
def level(message: Message):
    if not message.from_user.is_bot:
        chat_id = message.from_user.id
        stats = level_cluster.find_one({'user_id': chat_id})
        user_stat = user_cluster.find_one({'user_id': chat_id})
        if user_stat is None:
            new_stat = {
                'user_id': chat_id,
                'username': message.from_user.username,
                'firstname': message.from_user.first_name,
                'clan_ids': [message.chat.id]
            }
            user_cluster.insert_one(new_stat)
        else:
            user_cluster.update_one({'user_id': chat_id}, {'$set': {'user_id': chat_id},
                                                           '$set': {'username': message.from_user.username},
                                                           '$set': {'firstname': message.from_user.first_name}})
            if not message.chat.id in user_stat['clan_ids']:
                user_cluster.update_one({'user_id': chat_id}, {'$addToSet': {'clan_ids': message.chat.id}})
        if stats is None:
            new_user = {'user_id': chat_id,
                        'Level': 0,
                        'Exp': 1,
                        'Name': message.from_user.username}
            level_cluster.insert_one(new_user)
        if message.content_type == "text":
            level_cluster.update_one({'user_id': chat_id}, {'$inc': {'Exp': 10}})
        elif message.content_type == "sticker":
            level_cluster.update_one({'user_id': chat_id}, {'$inc': {'Exp': 20}})
        else:
            level_cluster.update_one({'user_id': chat_id}, {'$inc': {'Exp': 5}})
        stats = level_cluster.find_one({'user_id': chat_id})
        level_start = stats['Level']
        xp = stats['Exp']
        lvl = 0
        while True:
            if xp < (50 * (lvl ** 2) + 50 * lvl):
                break
            lvl += 1
        level_cluster.update_one({'user_id': chat_id}, {'$max': {'Level': lvl}})


@bot.poll_answer_handler(func=lambda poll: True)
def pollanshandler(poll):
    poll_id = poll.poll_id
    founded = poll_cluster.find_one({'poll_id': poll_id})
    if founded is not None:
        answered_option = poll.options_ids
        options = founded['options']
        if not founded['multians']:
            if len(answered_option) == 1:
                answered_option = answered_option[0]
            if options[answered_option] == founded['answer']:
                win_message = f"<a href='tg://user?id={poll.user.id}'>{poll.user.first_name}</a> has answered correctly"
                bot.send_message(founded['chat_id'], win_message)
                level_cluster.update_one({'user_id': poll.user.id}, {'$inc': {'Exp': 10}})
            else:
                lose_message = f"<a href='tg://user?id={poll.user.id}'>{poll.user.first_name}</a> has answered wrong"
                bot.send_message(founded['chat_id'], lose_message)
                bot.send_message(poll.user.id, f"The correct answer is {founded['answer']}")
                level_cluster.update_one({'user_id': poll.user.id}, {'$inc': {'Exp': -5}})
        else:
            correctly_answered = 0
            wrongly_answered = 0
            total_answered = len(answered_option)
            for j, i in enumerate(answered_option):
                if options[i] in founded['answer']:
                    correctly_answered += 1
                else:
                    wrongly_answered += 1
            last_message = f"<a href='tg://user?id={poll.user.id}'>{poll.user.first_name}</a> has answered {correctly_answered} out of his {total_answered} chosen answers"
            bot.send_message(founded['chat_id'], last_message)
            bot.send_message(poll.user.id, f"The correct answers are {founded['answer']}")
            marks = correctly_answered * 10 - wrongly_answered * 5
            level_cluster.update_one({'user_id': poll.user.id}, {'$inc': {'Exp': marks}})


def quizasker():
    while True:
        thismoment = datetime.datetime.now()
        Allowed_hours = [10, 11, 12, 14, 15, 16, 17, 18]
        if thismoment.hour in Allowed_hours and thismoment.minute == 0 and thismoment.second == 0:
            print("QUIZ TIME")
            found = other_cluster.find_one({'name': "quiz_groups"})
            ids = found["Allowed"]
            for id in ids:
                bot.send_message(id, "QUIZ TIME")
                quiz_question = Quizzer().quiz_question
                options = quiz_question["OPTIONS"]
                answer = quiz_question["CORRECT"]
                poll = bot.send_poll(chat_id=id,
                                     question=quiz_question["Question"],
                                     options=quiz_question["OPTIONS"],
                                     allows_multiple_answers=quiz_question["MULTIPLE ANSWER"],
                                     is_anonymous=False,
                                     explanation=f"The correct answer is {answer}"
                                     )
                poll_cluster.insert_one({
                    'poll_id': poll.poll.id,
                    'chat_id': id,
                    'answer': answer,
                    'options': options,
                    'multians': quiz_question["MULTIPLE ANSWER"]
                })
        time.sleep(1)


def runner():
    while True:
        print("BOT RUNNING")
        threading.Thread(target=quizasker).start()
        bot.polling(True)
        """except Exception as e:
            print("Upadating allowed groups")
            updateallowedgroups()
            print(e)"""


if __name__ == "__main__":
    runner()
