# comptrain-telegram-bot

## Intro

Forked from elbaulp/comptrain-bot 

Support several training plans:

  - Open prep
  - Games prep
  - Home gym with equipment
  - Home gym without equipment

## Usage

### Installation

```
pip3 install -r requirements.txt
```

### Open prep config

```
TELEGRAM_TOKEN=xxxx TELEGRAM_CHAT_ID="@comptrain_open_prep" WOD=open python comptrain-telegram-bot.py
```

### Games prep config

```
TELEGRAM_TOKEN=xxxx TELEGRAM_CHAT_ID="@comptrain_games_prep" WOD=games python comptrain-telegram-bot.py
```

### Home gym with equipment config

```
TELEGRAM_TOKEN=xxxx TELEGRAM_CHAT_ID="@comptrain_home_gym_1" WOD=home1 python comptrain-telegram-bot.py
```

### Home gym without equipment config

```
TELEGRAM_TOKEN=xxxx TELEGRAM_CHAT_ID="@comptrain_home_gym_2" WOD=home2 python comptrain-telegram-bot.py
```
