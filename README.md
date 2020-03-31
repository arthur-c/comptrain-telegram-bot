# comptrain-telegram-bot

## Intro

Forked from elbaulp/comptrain-bot 

Support several training plans:

  - Open prep - https://t.me/comptrain_open_prep
  - Games prep - https://t.me/comptrain_games_prep
  - Home gym with equipment - https://t.me/comptrain_home_gym
  - Home gym without equipment - https://t.me/comptrain_home_gym

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
