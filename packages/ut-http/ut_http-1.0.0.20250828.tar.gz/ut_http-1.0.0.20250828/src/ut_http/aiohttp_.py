# coding=utf-8
"""
Kosakya Appliction Utilities Package
Kosakya Async http Module
contains the Kosakya Async Http Class
"""

from aiohttp import ClientSession
import asyncio


class AsyncHttp:

    @staticmethod
    async def fetch_uri(uri):
        async with ClientSession() as session:
            async with session.get(uri) as resp:
                data = await resp.json()
        return data

    @classmethod
    async def get_uris(cls, uris):
        tasks = [asyncio.create_task(cls.fetch_site(s)) for s in uris]
        return await asyncio.gather(*tasks)

    @classmethod
    async def run_get_uris(cls, uris):
        data = asyncio.run(cls, cls.get_uris(uris))
        return data
