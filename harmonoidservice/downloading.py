import httpx
from . import async_youtube_dl
import os
from fastapi.responses import FileResponse
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, COMM, TDRC, TRCK, APIC, TPE2

import logging

logger = logging.getLogger(__name__)


class DownloadHandler:
    async def SaveAudio(self, trackId):
        await async_youtube_dl.download(
            f"https://www.youtube.com/watch?v={trackId}", f"{trackId}"
        )

    async def SaveMetaData(self, trackInfoJSON):
        art = (
            trackInfoJSON["album_art_640"]
            or trackInfoJSON["album_art_300"]
            or trackInfoJSON["album_art_64"]
        )

        trackId = trackInfoJSON["track_id"]

        audioFile = MP3(f"{trackId}.mp3", ID3 = ID3)

        if art:
            logger.info("[metadata] Getting album art: " + art)
            async with httpx.AsyncClient() as client:
                response = await client.get(art)
            albumArtBinary = response.content
            logger.info("[metadata] Album art retrieved.")
            audioFile.tags.add(
                APIC(
                    mime="image/jpeg",
                    type=3,
                    desc="Cover",
                    data=albumArtBinary,
                )
            )
        else:
            logger.info("[metadata] Album art is not found.")

        audioFile["TIT2"] = TIT2(encoding=3, text=trackInfoJSON["track_name"])
        audioFile["TALB"] = TALB(encoding=3, text=trackInfoJSON["album_name"])
        audioFile["COMM"] = COMM(
            encoding=3,
            lang="eng",
            desc="https://music.youtube.com/watch?v=" + trackInfoJSON["track_id"],
            text="https://music.youtube.com/watch?v=" + trackInfoJSON["track_id"],
        )
        audioFile["TPE1"] = TPE1(
            encoding=3, text="/".join(trackInfoJSON["track_artists"])
        )
        if len(trackInfoJSON["album_artists"]) != 0:
            audioFile["TPE2"] = TPE2(encoding=3, text=trackInfoJSON["album_artists"][0])
        audioFile["TDRC"] = TDRC(encoding=3, text=trackInfoJSON["year"])
        audioFile["TRCK"] = TRCK(encoding=3, text=str(trackInfoJSON["track_number"]))

        audioFile.save()

        logger.info(f"[metadata] Successfully added meta data to track ID: {trackId}.")

    async def TrackDownload(self, trackId, albumId, trackName):
        if trackId:
            logger.info(f"[server] Download request in ID format.")
        if trackName:
            logger.info(f"[server] Download request in name format.")
            trackId = await self.ytMusic._search(trackName, "songs")
            trackId = trackId[0]["videoId"]

        if os.path.isfile(f"{trackId}.mp3"):
            return FileResponse(
                f"{trackId}.mp3",
                media_type="audio/mpeg",
                headers={"Accept-Ranges": "bytes"},
            )

        trackInfo = await self.TrackInfo(trackId, albumId)
        logger.info(f"[info] Successfully retrieved metadata of track ID: {trackId}.")

        await self.SaveAudio(trackId)
        await self.SaveMetaData(trackInfo)

        logger.info(f"[server] Sending audio binary for track ID: {trackId}")
        return FileResponse(
            f"{trackId}.mp3",
            media_type="audio/mpeg",
            headers={"Accept-Ranges": "bytes"},
        )
