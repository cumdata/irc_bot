# IRC BOT

## Getting Started
1. Copy `example_conf.toml` to `config.toml` and update settings appropriately
```bash
cp example_conf.toml config.toml
```

2. Copy `example_admins.toml` to `admins.toml` and update the admin list
```bash
cp example_admins.toml admins.toml
```

3. Create the following files
```bash
echo -en "Hello world.\nThis is the file used for markov." >> chatter.log 
```

4. Generate cacert + key
```bash
cd certs
openssl req -x509 -newkey rsa:2048 -keyout selfsigned.key -nodes -out selfsigned.cert -sha256 -days 1000
```

## Building + Running container

<b>Using docker-compose</b>
```bash
docker-compose up
```

<b>Docker build using CLI</b>
```bash
# Build container
docker build -t <tag> .

# Run container
FOLDER_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
docker run --rm \
-p 12345-12444:12345-12444 \
-v $FOLDER_PATH/ascii_art:/irc_bot/ascii_art \
-v $FOLDER_PATH/chatter.log:/irc_bot/chatter.log \
-v $FOLDER_PATH/trolldb.b64:/irc_bot/trolldb.b64 \
-v $FOLDER_PATH/admins.toml:/irc_bot/admins.toml \
-v $FOLDER_PATH/config.toml:/irc_bot/config.toml \
-v $FOLDER_PATH/bot_modules:/irc_bot/bot_modules \
-t <tag>>
```

### GLHF, CHAT HARD

![alt GNAA Public Health Message](irc-covid-message.png)


License
=======
![name](WTFPL.jpg)

```
            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.

```