import asyncio
import os
import re

import ollama

import nooscope_rpc.api as api


history = []

system_prompt = f"""
You are a chatter on IRC. You are to respond but keep your responses brief 
and blend in with the chat room. Make sure to answer any technical questions.
If the user is asking a technical question ignore the chat_history and answer
their question instead.


Here are some previous chats from uses to get a sense of the chatroom:

<chat_history>
{history}
</chat_history>

"""


def add_history(user, msg):
    history.append(
        {'USER': user, 'MESSAGE': msg}
    )
    if len(history) > 100:
        history.pop(0)


async def handle_query(msg):
    messages = [
        {"role": "system", "content": system_prompt},  # Custom system prompt
        {"role": "user", "content": msg}  # User's message
    ]
    client = ollama.AsyncClient()
    full_message = ''  # Accumulate the message content

    try:
        # Perform the chat call with streaming enabled
        parts = await client.chat(
            model='llama3.1',
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
            add_history(by, message)
            if message.startswith("zheani ") or message.startswith("zheani: "):
                user_query = message.replace('zheani ', '').replace('zheani: ', '')
                full_message = await handle_query(user_query)
                await self.rpc.send_message(target, full_message)
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
