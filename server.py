import os
import jinja2
import asyncio
import datetime
import aioredis
import aiohttp.web
import aiohttp_jinja2
from pathlib import Path


redis_host = os.getenv('redis_host', '172.17.0.2')
mu = int(os.getenv('mu', 0))
sigma = int(os.getenv('sigma', 1))
redis_key = "RDS_KEY"
here = Path(__file__).resolve().parent


@aiohttp_jinja2.template('template/index.html')
async def web_handle(request):
    return {"succses": True}


async def web_soc_handle(request):
    app = request.app
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    while True:

        res = await app['redis'].get(redis_key, encoding='utf-8')
        await ws.send_json({'error_msg': str(res)})
        await asyncio.sleep(1)


async def websocket_handler(request):
    app = request.app
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

                privios_res = await app['redis'].get(redis_key, encoding='utf-8')

                if not privios_res:
                    privios_res = ""

                await app['redis'].set(redis_key, f"{privios_res} |||||| {error_str}")

            await ws.send_str('Answer!')


async def main(loop_):
    app = aiohttp.web.Application(loop=loop_)
    app.router.add_route('GET', '/', web_handle)
    app.router.add_route('GET', '/brouser', web_soc_handle)
    app.router.add_route('GET', '/ws', websocket_handler)
    redis = await aioredis.create_redis_pool(f'redis://{redis_host}', loop=loop_)
    app['redis'] = redis
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(here)))
    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    aiohttp.web.run_app(main(loop))
