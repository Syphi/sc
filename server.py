import os
import jinja2
import asyncio
import aiofiles
import datetime
import aiohttp.web
import aiohttp_jinja2
from pathlib import Path


HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))
mu = os.getenv('mu', 0)
sigma = os.getenv('sigma', 1)
here = Path(__file__).resolve().parent


@aiohttp_jinja2.template('template/index.html')
async def web_handle(request):
    return {"succses": True}


async def web_soc_handle(request):
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    while True:
        file = await aiofiles.open('error.txt', 'r')
        res = await file.read()
        await ws.send_json({'error_msg': res})
        await asyncio.sleep(1)


async def websocket_handler(request):
    app = request
    ws = aiohttp.web.WebSocketResponse(heartbeat=5, autoping=True)
    await ws.prepare(request)

    while True:
        json_data = await ws.receive_json()
        print("-")
        if "normal_distribution_number" and "sequence_number" not in json_data.keys():
            await ws.send_str('Wrong data format!')
        else:
            number = json_data['normal_distribution_number']

            if 2*(mu - sigma) >= number or number >= 2*(mu + sigma):

                error_str = f"current timestamp - {datetime.datetime.now()},  number - {number}," \
                            f" and its sequence number - {json_data['sequence_number']}"
                print(error_str)
                file = await aiofiles.open('error.txt', 'a')
                await file.write(error_str+'\n')
                await file.close()

            await ws.send_str('Answer!')


def main():
    loop = asyncio.get_event_loop()
    app = aiohttp.web.Application(loop=loop)
    app.router.add_route('GET', '/', web_handle)
    app.router.add_route('GET', '/brouser', web_soc_handle)
    app.router.add_route('GET', '/ws', websocket_handler)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(here)))
    aiohttp.web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
