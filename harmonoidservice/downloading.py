import httpx
from . import async_youtube_dl
import os
from .async_mutagen import MP4, MP4Cover
from fastapi import HTTPException
from fastapi.responses import FileResponse

import logging

logger = logging.getLogger(__name__)


class DownloadHandler:
    async def SaveAudio(self, trackId):
        result = await async_youtube_dl.download(
            f"https://www.youtube.com/watch?v={trackId}", f"{trackId}.m4a"
        )
        if result:
            logger.info(
                f"[download] Track download successful for track ID: {trackId}."
            )
        else:
            raise HTTPException(500, "Couldn't download video " + trackId)

    async def SaveMetaData(self, trackInfoJSON):
        art = (
            trackInfoJSON["album_art_640"]
            or trackInfoJSON["album_art_300"]
            or trackInfoJSON["album_art_64"]
        )

        trackId = trackInfoJSON["track_id"]

        audioFile = MP4(f"{trackId}.m4a")
        await audioFile.init()

        if art:
            logger.info("[metadata] Getting album art: " + art)
            async with httpx.AsyncClient() as client:
                response = await client.get(art)
            albumArtBinary = response.content
            logger.info("[metadata] Album art retrieved.")
            cover = MP4Cover(albumArtBinary, imageformat=MP4Cover.FORMAT_JPEG)
            await cover.init()
            audioFile["covr"] = [cover]
        else:
            logger.info("[metadata] Album art is not found.")

        audioFile["\xa9nam"] = trackInfoJSON["track_name"]
        audioFile["\xa9alb"] = trackInfoJSON["album_name"]
        audioFile["\xa9ART"] = "/".join(trackInfoJSON["track_artists"])
        audioFile["aART"] = trackInfoJSON["album_artists"][0]
        audioFile["\xa9day"] = trackInfoJSON["year"]
        audioFile["trkn"] = [
            (trackInfoJSON["track_number"], trackInfoJSON["album_length"])
        ]
        audioFile["\xa9cmt"] = (
            "https://music.youtube.com/watch?v=" + trackInfoJSON["track_id"]
        )
        await audioFile._save()

        logger.info(f"[metadata] Successfully added meta data to track ID: {trackId}.")

    async def TrackDownload(self, trackId, trackName):
        if trackId:
            logger.info(f"[server] Download request in ID format.")
        if trackName:
            logger.info(f"[server] Download request in name format.")
            trackId = await self.ytMusic._search(trackInfo["track_name"], "songs")
            trackId = trackId[0]["videoId"]

        if os.path.isfile(f"{trackId}.m4a"):
            return FileResponse(
                f"{trackId}.m4a",
                media_type="audio/mp4",
                headers={"Accept-Ranges": "bytes"},
            )

        trackInfo = await self.TrackInfo(trackId)
        logger.info(f"[info] Successfully retrieved metadata of track ID: {trackId}.")
        await self.SaveAudio(trackId)
        await self.SaveMetaData(trackInfo)

        logger.info(f"[server] Sending audio binary for track ID: {trackId}")
        return FileResponse(
            f"{trackId}.m4a",
            media_type="audio/mp4",
            headers={"Accept-Ranges": "bytes"},
        )
