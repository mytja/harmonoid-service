import asyncio
from mutagen.mp3 import MP3
from mutagen.id3 import TIT2, TALB, TPE1, COMM, TDRC, TRCK, APIC, TPE2
import httpx
import logging

logger = logging.getLogger(__name__)


class MP3(MP3):
    def __init__(self, filename, trackInfoJSON, art):
        self.filename = filename
        self.trackInfoJSON = trackInfoJSON
        self.art = art

    async def init(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, super().__init__, self.filename)

        if self.art:
            logger.info("[metadata] Getting album art: " + self.art)
            async with httpx.AsyncClient() as client:
                response = await client.get(self.art)
            albumArtBinary = response.content
            logger.info("[metadata] Album art retrieved.")
            self["APIC"] = APIC(
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=albumArtBinary,
            )
        else:
            logger.info("[metadata] Album art is not found.")

        self["TIT2"] = TIT2(encoding=3, text=self.trackInfoJSON["track_name"])
        self["TALB"] = TALB(encoding=3, text=self.trackInfoJSON["album_name"])
        self["COMM"] = COMM(
            encoding=3,
            lang="eng",
            desc="https://music.youtube.com/watch?v=" + self.trackInfoJSON["track_id"],
            text="https://music.youtube.com/watch?v=" + self.trackInfoJSON["track_id"],
        )
        self["TPE1"] = TPE1(
            encoding=3, text="/".join(self.trackInfoJSON["track_artists"])
        )
        if len(self.trackInfoJSON["album_artists"]) != 0:
            self["TPE2"] = TPE2(encoding=3, text=self.trackInfoJSON["album_artists"][0])
        self["TDRC"] = TDRC(encoding=3, text=self.trackInfoJSON["year"])
        self["TRCK"] = TRCK(encoding=3, text=str(self.trackInfoJSON["track_number"]))

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.save)