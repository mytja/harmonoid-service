import asyncio
from mutagen.mp4 import MP4
from mutagen.id3 import TIT2, TALB, TPE1, COMM, TDRC, TRCK, APIC, TPE2
import httpx


class MP4(MP4):
    def __init__(self, filename, trackInfoJSON, art):
        self.filename = filename
        self.trackInfoJSON = trackInfoJSON
        self.art = art

    async def init(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, super().__init__, self.filename)

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
