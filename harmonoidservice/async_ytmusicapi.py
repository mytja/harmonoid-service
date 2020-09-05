from ytmusicapi import YTMusic
import asyncio


class YTMusic(YTMusic):
    def __init__(self):
        self.initialized = False

    async def run(self, method, *args):
        if not self.initialized:
            await self.init()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, method, *args)

    async def init(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, super().__init__)
        self.initialized = True

    async def _search(self, query, filter):
        return await self.run(self.search, query, filter)

    async def _get_artist(self, channel_id):
        return await self.run(self.get_artist, channel_id)

    async def _get_album(self, browse_id):
        return await self.run(self.get_album, browse_id)

    async def _get_song(self, video_id):
        return await self.run(self.get_song, video_id)
