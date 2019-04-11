# Chat spammer
this is just a simple chat spammer bot with some configuration

## Features
- very configurable
- auto reconnecting
- anti-afk measures
- randomization
- light weight

## Tutorial

### Requirements
- Python 2.7 or 3.x
- pip (comes by default with python)

### Installation
- open a command window inside the folder of the project
- run ```pip install -r requirements.txt```

### Configuration

#### config.json
- account
    - username (required if not online)
    - email (required for online)
    - password (required for online)
    - online (whether to join in online or offline mode)
- server
    - host (server ip address)
    - port (server port, default 25565)
- walk (anti afk measure)
    - distance (in blocks, will return back to starting position)
    - speed (in ticks, lower means faster)
    - speed_divider (use to smooth walking)
- spawn mode
    - enabled (true or false)
    - speed (in ticks, lower means faster)
- respawn_speed (in ticks, how fast should the bot respawn if killed)
- anti_afk (in ticks, how fast should go through the anti-afk steps)
- message_speed (in ticks, how often to sent a new message)
- rng_events (array of all events that should be randomized, all randomizable events are respawn_speed, anti_afk, message_speed)
- prefix (what you want your messages to start with)

#### messages.csv
its a standard csv with labeled columns
- prefix_flag
    - never (messages will never have a prefix)
    - always (message will always have a prefix)
    - random (when the message is sent it has a random chance to show or hide the prefix)
- message (any message you want)

### Execution
- in the project folder run ```python start.py```

