from datetime import datetime, timedelta
import aiohttp
import asyncio


def make_params(**kwargs) -> dict:
    return kwargs


async def get_info(request, params) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(request, params=params) as response:
            result = await response.json()
            return result


def get_moscow_time() -> str:
    moscow_time = datetime.utcnow() + timedelta(hours=3)
    moscow_time_iso = moscow_time.isoformat()
    return moscow_time_iso


async def main():
    request = 'https://api.hh.ru/vacancies'
    params = make_params(text='Java',
                         date_from=(datetime.fromisoformat(get_moscow_time()) - timedelta(days=1)).isoformat())
    result = await get_info(request, params)
    print(result)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
