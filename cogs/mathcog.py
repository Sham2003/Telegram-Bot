import asyncio
import os
from telethon import TelegramClient
from telethon.events import NewMessage
from sympy import Symbol, integrate, preview, sympify, latex
import matplotlib.pyplot as plt
import tempfile

plt.rcParams['text.usetex'] = True


def latex2image(latex_expression, isize=(1, 0.5), fsize=16, dpi=200):
    image_name = None
    with tempfile.NamedTemporaryFile(suffix='.png', dir='.', delete=False) as tmpfile:
        image_name = tmpfile.name
    print("Creating temp file = ", image_name)
    fig = plt.figure(figsize=isize, dpi=dpi)
    fig.text(
        x=0.5,
        y=0.5,
        s=latex_expression,
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=fsize,
    )

    if image_name is None:
        raise ValueError("Image name is none for latex string {}".format(latex_expression))
    plt.savefig(image_name)

    return image_name


EVENTS = []
CALLBACKS = []


async def integralhandler(event: NewMessage.Event):
    bot: TelegramClient = event.client
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
    await bot.send_message(event.chat_id, Help_func_message, parse_mode="HTML")


EVENTS.append(NewMessage(pattern='/integrators'))
CALLBACKS.append(integralhandler)


async def integration(event: NewMessage.Event):
    bot: TelegramClient = event.client
    expression = event.pattern_match.group(1) if event.pattern_match.group(1) else None
    variable = event.pattern_match.group(2) if event.pattern_match.group(2) else None
    lower_limit = event.pattern_match.group(3) if event.pattern_match.group(3) else None
    upper_limit = event.pattern_match.group(4) if event.pattern_match.group(4) else None
    if expression is None:
        await bot.send_message(event.chat_id, "No Expression is given Check help")
        return
    if variable not in expression:
        await bot.send_message(event.chat_id, "Expression not matches with variable given Check help")
        return

    limits = None
    if lower_limit is None or upper_limit is None:
        limits = Symbol(variable)
    else:
        limits = (Symbol(variable), lower_limit, upper_limit)
    expr = integrate(expression, limits)
    latex_string = '$' + latex(expr) + '$'

    file = latex2image(latex_string)
    await bot.send_file(event.chat_id, file, reply_to=event._message_id)
    os.remove(file)


INTEGRAL_PATTERN = r'^\/integrate(?:\s+([^\s]+)(?:\s+([a-zA-Z]+)(?:=([\-a-zA-Z0-9]+)to([\-a-zA-Z0-9]+))?)?)?$'
EVENTS.append(NewMessage(pattern=INTEGRAL_PATTERN))
CALLBACKS.append(integration)


async def calculate(event: NewMessage.Event):
    bot: TelegramClient = event.client
    expression = event.pattern_match.group(2) if event.pattern_match.group(2) else None
    if expression is None:
        await bot.send_message(event.chat_id, "No Expression is given Check help")
        return
    latex_string = '$' + latex(sympify(expression)) + '$'
    file = latex2image(latex_string)
    await bot.send_file(event.chat_id, file, reply_to=event._message_id)
    os.remove(file)


CALC_PATTERN = r"^\/(calc|compute)(.*)"
EVENTS.append(NewMessage(pattern=CALC_PATTERN))
CALLBACKS.append(calculate)


def init_cog(bot: TelegramClient):
    for event, callback in zip(EVENTS, CALLBACKS):
        bot.add_event_handler(callback, event=event)
    print(f"Loaded {len(CALLBACKS)} event handlers from {__name__}")
