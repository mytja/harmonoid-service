from .async_youtubesearchpython import SearchVideos
import httpx
from . import async_youtube_dl
import os
from .async_mutagen import MP4, MP4Cover
from fastapi import HTTPException
from fastapi.responses import FileResponse

import logging

logger = logging.getLogger(__name__)


class YoutubeHandler:
    async def SaveAudio(self, videoId, trackId):
        result = await async_youtube_dl.download(
            f"https://www.youtube.com/watch?v={videoId}", f"{trackId}.m4a"
        )
        if result:
            logger.info(
                f"[download] Track download successful for track ID: {trackId}."
            )
        else:
            raise HTTPException(500, "Couldn't download video " + videoId)

    async def SaveMetaData(self, trackInfoJSON):
        logger.info("[metadata] Getting album art: " + trackInfoJSON["album_art_640"])

        async with httpx.AsyncClient() as client:
            response = await client.get(trackInfoJSON["album_art_640"])

        albumArtBinary = response.content

        logger.info("[metadata] Album art retrieved.")

        trackId = trackInfoJSON["track_id"]

        audioFile = MP4(f"{trackId}.m4a")
        await audioFile.init()

        cover = MP4Cover(albumArtBinary, imageformat=MP4Cover.FORMAT_JPEG)
        await cover.init()

        audioFile["covr"] = [cover]
        audioFile["\xa9nam"] = trackInfoJSON["track_name"]
        audioFile["\xa9alb"] = trackInfoJSON["album_name"]
        audioFile["\xa9ART"] = "/".join(trackInfoJSON["track_artists"])
        audioFile["aART"] = trackInfoJSON["album_artists"][0]
        audioFile["\xa9day"] = trackInfoJSON["year"]
        audioFile["trkn"] = [
            (trackInfoJSON["track_number"], trackInfoJSON["album_length"])
        ]
        audioFile["\xa9cmt"] = (
            "https://open.spotify.com/track/" + trackInfoJSON["track_id"]
        )
        await audioFile._save()

        logger.info(f"[metadata] Successfully added meta data to track ID: {trackId}.")

    async def SearchYoutube(self, keyword, offset, maxResults, mode="json"):
        search = SearchVideos(keyword, offset, mode, maxResults)
        await search.main()
        return search.result()

    async def TrackDownload(self, trackId, trackName):
        if trackId:
            if os.path.isfile(f"{trackId}.m4a"):
                return FileResponse(f"{trackId}.m4a")

            logger.info(f"[server] Download request in ID format.")
            trackInfo = await self.TrackInfo(trackId)
            logger.info(
                f"[info] Successfully retrieved metadata of track ID: {trackId}."
            )
            artists = " ".join(trackInfo["track_artists"])
            videoId = await self.SearchYoutube(
                "lyrics "
                + trackInfo["track_name"].split("(")[0].strip().split("-")[0].strip()
                + " "
                + artists,
                1,
                1,
                "dict",
            )
            videoId = videoId["search_result"][0]["id"]

            logger.info(f"[search] Search successful. Video ID: {videoId}.")
        if trackName:
            logger.info(f"[server] Download request in name format.")
            videoId = await self.SearchYoutube(trackName, 1, "json", 1)
            videoId = videoId["search_result"][0]["id"]
            logger.info(f"[search] Search successful. Video ID: {videoId}.")
            trackId = await self.SearchSpotify(trackName, "track", 0, 1)
            trackId = trackId["tracks"][0]["track_id"]
            logger.info(f"[tracksearch] Track Search successful. Track ID: {trackId}.")

            if os.path.isfile(f"{trackId}.m4a"):
                return FileResponse(f"{trackId}.m4a")

            trackInfo = await self.TrackInfo(trackId)
            logger.info(
                f"[info] Successfully retrieved metadata of track ID: {trackId}."
            )

        await self.SaveAudio(videoId, trackId)
        await self.SaveMetaData(trackInfo)
        logger.info(f"[server] Sending audio binary for track ID: {trackId}")
        return FileResponse(f"{trackId}.m4a")
