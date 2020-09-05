from ytmusicapi import YTMusic
import asyncio

class YTMusic(YTMusic):
    def __init__(self):
        self.initialized = False

    async def init(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, super().__init__)
        self.initialized = True

    async def _search(self, *args):
        if not self.initialized:
            await self.init()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.search, *args)
