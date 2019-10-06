import os
import random
import asyncio
import aiohttp


HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))
mu = os.getenv('mu', 0)
sigma = os.getenv('sigma', 1)
URL = f'http://{HOST}:{PORT}/ws'


async def main():
    counter = 0
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL, autoclose=True) as ws:
        while True:
            counter = await prompt_and_send(ws, counter)
            if not counter:
                print("Could not ping server")
                break
            await asyncio.sleep(1)

            msg = await ws.receive()
            if msg.type in (aiohttp.WSMsgType.CLOSED,
                            aiohttp.WSMsgType.ERROR):
                break


async def prompt_and_send(ws, counter):
    json_to_send = {
        "normal_distribution_number": random.normalvariate(mu, sigma),
        # "normal_distribution_number": 22,
        "sequence_number": counter
    }
    await ws.send_json(json_to_send)
    return counter + 1


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
