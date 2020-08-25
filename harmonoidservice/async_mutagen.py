import asyncio
from mutagen.mp4 import MP4, MP4Cover

class MP4(MP4):
    def __init__(self, filename):
        self.filename = filename

    async def init(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, super().__init__, self.filename)

    async def _save(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.save)

class MP4Cover(MP4Cover):
    def __init__(self, binary, imageformat=None):
        self.binary = binary
        self.imageformat = imageformat

    async def init(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, super().__init__, self.binary, self.imageformat)
