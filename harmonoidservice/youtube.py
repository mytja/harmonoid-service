from .async_youtubesearchpython import SearchVideos
import httpx
from . import async_youtube_dl
from aiofile import AIOFile
import json
import os
from .async_mutagen import MP4, MP4Cover
from flask import make_response, Response

import logging

logger = logging.getLogger(__name__)


class YoutubeHandler:
    async def SaveAudio(self, videoId, trackId):
        await async_youtube_dl.download(
            f"https://www.youtube.com/watch?v={videoId}", f"{trackId}.m4a"
        )
        logger.info(f"[download] Track download successful for track ID: {trackId}.")

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
        audioFile["aART"] = "/".join(trackInfoJSON["album_artists"])
        audioFile["\xa9day"] = trackInfoJSON["year"]
        audioFile["trkn"] = [
            (trackInfoJSON["track_number"], trackInfoJSON["album_length"])
        ]
        audioFile["\xa9cmt"] = (
            "https://open.spotify.com/track/" + trackInfoJSON["track_id"]
        )
        await audioFile._save()

        logger.info(f"[metadata] Successfully added meta data to track ID: {trackId}.")

    async def SearchYoutube(self, keyword, offset, mode, maxResults):
        # BUG: mode can be only JSON
        if keyword == None:
            return make_response("bad request", 400)

        search = SearchVideos(keyword, offset, mode, maxResults)
        await search.main()
        return Response(
            search.result(), headers={"Content-Type": "application/json"}, status=200,
        )

    async def TrackDownload(self, trackId, trackName):
        # OPTIMIZE: same code twice
        if trackId != None:
            try:
                logger.info(f"[server] Download request in ID format.")
                trackInfo = await self.TrackInfo(trackId)
                trackInfo = trackInfo.json
                logger.info(
                    f"[info] Successfully retrieved metadata of track ID: {trackId}."
                )
                artists = " ".join(trackInfo["track_artists"])
                videoId = await self.SearchYoutube(
                    "lyrics "
                    + trackInfo["track_name"]
                    .split("(")[0]
                    .strip()
                    .split("-")[0]
                    .strip()
                    + " "
                    + artists,
                    1,
                    "json",
                    1,
                )
                videoId = videoId.json["search_result"][0]["id"]

                logger.info(f"[search] Search successful. Video ID: {videoId}.")

                await self.SaveAudio(videoId, trackId)
                await self.SaveMetaData(trackInfo)
                async with AIOFile(f"{trackId}.m4a", "rb") as audioFile:
                    audioBinary = await audioFile.read()

                logger.info(f"[server] Sending audio binary for track ID: {trackId}")

                response = make_response(audioBinary, 200)  # TODO: replace with FastAPI
                response.headers["Content-Length"] = len(audioBinary)
                response.headers["Content-Type"] = "audio/mp4"
                return response
            except:
                logger.exception("")
                return make_response(
                    "internal server error", 500
                )  # TODO: replace with FastAPI

        elif trackName != None:
            try:
                logger.info(f"[server] Download request in name format.")
                videoId = await self.SearchYoutube(trackName, 1, "json", 1)
                videoId = videoId.json["search_result"][0]["id"]
                logger.info(f"[search] Search successful. Video ID: {videoId}.")
                trackId = await self.SearchSpotify(trackName, "track", 0, 1)
                trackId = trackId.json["tracks"][0]["track_id"]
                logger.info(
                    f"[tracksearch] Track Search successful. Track ID: {trackId}."
                )

                trackInfo = await self.TrackInfo(trackId)
                trackInfo = trackInfo.json
                logger.info(
                    f"[info] Successfully retrieved metadata of track ID: {trackId}."
                )
                await self.SaveAudio(videoId, trackId)
                await self.SaveMetaData(trackInfo)
                async with AIOFile(f"{trackId}.m4a", "rb") as audioFile:
                    audioBinary = await audioFile.read()
                logger.info(f"[server] Sending audio binary for track ID: {trackId}")

                response = make_response(audioBinary, 200) # BUG: RuntimeError: Working outside of application context.
                response.headers["Content-Length"] = len(audioBinary)
                response.headers["Content-Type"] = "audio/mp4"
                return response
            except:
                logger.exception("")
                return make_response(
                    "internal server error", 500
                )  # TODO: replace with FastAPI
        else:
            return make_response("bad request", 400)  # TODO: replace with FastAPI
