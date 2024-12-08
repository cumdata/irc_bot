import asyncio
import os

import ollama

import nooscope_rpc.api as api


class ChatBot(api.IrcImpl):
    """LLM Chat plugin"""

    async def on_message(self, target, by, message):
        """Callback method that handles messages from server

        :param str target: target of the message. will be a channel or the bot
            if someone PM'd it.
        :param str by: the user who send the message
        :param str message: the message
        """
        print(target, by, message)
        # do some shit like
        if message == 'hack_a_gibson':
            await self.rpc.send_message(target, 'hacking gibson from RPC')
        elif message.startswith('dieplz'):
            await self.rpc.disconnect()
            exit(1)


async def main():

    while True:
        tcp = api.TcpClient(
            os.environ.get('BOT_IP'),  # use your bots host ip
            12345,
            ChatBot()
        )
        await tcp.connect()
        await tcp.read()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
