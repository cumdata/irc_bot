import asyncio
import datetime
import os
import re

import ollama

import nooscope_rpc.api as api

# BEGIN COLORS
WHITE = '00'
BLACK = '01'
BLUE = '02'
GREEN = '03'
RED = '04'
BROWN = '05'
PURPLE = '06'
ORANGE = '07'
YELLOW = '08'
LIME = '09'
TEAL = '10'
CYAN = '11'
LIGHT_BLUE = '12'
PINK = '13'
GREY = '14'
SILVER = '15'

# SPECIAL
BLUE_TWITTER = '47'

CONTROL_COLOR = '\x03'
BOLD = '\x02'
UNDERLINE = '\x1F'
ITALIC = '\x1D'
# END COLORS


model = "mistral-nemo:12b-instruct-2407-q4_1"
chat_history = []

system_prompt = """
You are a midwit who is all about that helter skelter back and forth banter. \n
You are to respond to users but keep your responses brief and on topic with the most recent chat messages. \n
If someone is bothering you, make fun of them and use the chat history as ammo. \n

Provided in <chat_history> is the last 10 messages from users in the IRC channel  
with the oldest messages first.\n

The chat history contains the timestamp | user | message. \n
Here is an example of the structure of chat_history: \n

<example>
1733696912838 | tinky | i love lasers! they are awesome\n
1733697110835 | baxter | shut up nerd\n
1733697209622 | play_games | yea shut up nerd lol\n
<example>\n

Here is the chat history which may contain between 0 to 10 entries: \n

<chat_history>
{history}
</chat_history> \n

Respond with just a message. Do not put the message in quotes. keep it brief, 
no more than 3 sentences.
"""


def _ts() -> int:
    """make now timestamp"""
    return int(datetime.datetime.utcnow().timestamp() * 1000)


def _add_history(user: str, msg: str):
    """Add history

    :param str user: the user
    :param str msg: the message
    """
    chat_history.append(
        f"{_ts()} | {user} | {msg}"
    )
    if len(chat_history) > 10:
        chat_history.pop(0)


def _format_history() -> str:
    """Returns the history

    :returns: formatted chat history
    """
    fmt_history = "\n".join(chat_history)
    print(fmt_history)
    return fmt_history


def _get_system_prompt():
    """Returns the system prompt"""
    return system_prompt.format(history=_format_history())


async def handle_query(msg) -> str:
    messages = [
        {"role": "system", "content": _get_system_prompt()},  # Custom system prompt
        {"role": "user", "content": msg}  # User's message
    ]
    client = ollama.AsyncClient()
    full_message = ''  # Accumulate the message content

    try:
        # Perform the chat call with streaming enabled
        parts = await client.chat(
            model=model,
            messages=messages,
            stream=True
        )

        # Stream the response and accumulate the full message
        async for part in parts:
            if 'message' in part:
                full_message += part['message']['content']

        return full_message  # Return the accumulated message after streaming

    except Exception as e:
        print(f"Error in handle_query: {e}")
        return "Error processing your request"  # Return a default error message


def colorize(text, fg, bg=None):
    """Colorizes text

    :param str text: text to colorize
    :param str fg: foreground color code (see colors above)
    :param str|None bg: background color code (see colors above)

    :returns: colorized text
    :rtype: str
    """
    if not bg:
        return f'{CONTROL_COLOR}{fg}{text}{CONTROL_COLOR}'
    else:
        return f'{CONTROL_COLOR}{fg},{bg}{text}{CONTROL_COLOR}'


def _post_fix(m: str) -> str:
    return m.lstrip('\"').rstrip('\"')


class ChatBot(api.IrcImpl):
    """LLM Chat plugin"""

    async def on_message(self, target, by, message):
        """Callback method that handles messages from the server

        :param str target: target of the message. will be a channel or the bot
            if someone PM'd it.
        :param str by: the user who sent the message
        :param str message: the message
        """
        try:
            print(target, by, message)
            if CONTROL_COLOR in message:
                print("message contained ctrl char")
                return

            _add_history(by, message)

            if message.startswith("zheani ") or message.startswith("zheani: "):
                user_query = message.replace('zheani ', '').replace('zheani: ', '')
                full_message = await handle_query(user_query)
                full_message = colorize(full_message, fg=PINK)
                await self.rpc.send_message(target, _post_fix(full_message))

            elif message.startswith('dieplz'):
                await self.rpc.disconnect()
                exit(1)  # Ideally handle exit more gracefully
        except Exception as e:
            print(f"Error processing message from {by}: {e}")


async def main():
    while True:
        try:
            tcp = api.TcpClient(
                os.environ.get('BOT_IP'),  # use your bot's host IP
                12345,
                ChatBot()
            )
            await tcp.connect()
            await tcp.read()
        except (asyncio.TimeoutError, ConnectionError) as e:
            # Handle specific connection-related exceptions
            print(f"Connection error occurred: {e}")
            # Optionally, wait before retrying to avoid spamming the server
            await asyncio.sleep(5)
        except Exception as e:
            # Handle unexpected exceptions
            print(f"Unexpected error: {e}")
            # You can decide whether to terminate or keep trying to reconnect
            await asyncio.sleep(5)

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    print("Bot terminated by user.")
finally:
    loop.close()
