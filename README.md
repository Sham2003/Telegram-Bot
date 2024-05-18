# Telegram Bot
This is a branch of my telegram bot 
This is created using telebot which uses the HTTPS Protocol

This bot uses mongoDB server to store info about users etc..


## Prerequisites
selenium>=3.141.0
pymongo[tls,srv]>=3.11.4
sympy>=1.6.2
requests>=2.24.0
telebot
dnspython==2.1.0
chess

## Setup
 ### Clone the repository:


```bash
git clone https://github.com/Sham2003/Telegram-Bot.git
cd Telegram-Bot
```

 ### Install Requirements:


```bash
pip install -r requirements.txt
```

 ### Edit Config File

Open the botconfig.py file

Edit the variables

```
TOKEN = "ENTER BOT TOKEN"
OWNER = 1 #Enter owner id in integer
MONGOURL = "mongodb://localhost:27017/Telegram" #enter your mongodb url
.......
```

 ### Run the bot

```
python bot.py
```

