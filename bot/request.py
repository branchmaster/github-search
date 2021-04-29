from aiohttp import ClientSession
from typing import Union


async def get(url: str) -> Union[dict, int]:
    async with ClientSession() as session:
        async with session.get(url) as response:
            json: dict = await response.json()
            return json, response.status