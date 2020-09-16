import httpx
from . import async_youtube_dl
import os
from fastapi.responses import FileResponse
from .async_mutagen import MP3
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

        mutagen = MP3(f"{trackId}.mp3", trackInfoJSON, art)
        await mutagen.init()

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
