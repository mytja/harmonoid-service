from youtubesearchpython import SearchVideos
import youtube_dl
import json
from urllib.request import urlopen
from urllib.request import Request
import os
from mutagen.mp4 import MP4, MP4Cover
from flask import make_response, Response

import logging

logger = logging.getLogger(__name__)


class YoutubeHandler:
    def SaveAudio(self, videoId, trackId):
        ydl_opts = {
            "format": "140",
            "cookiefile": "cookies.txt",
            "outtmpl": f"{trackId}.m4a",
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={videoId}"])
        logger.info(f"[download] Track download successful for track ID: {trackId}.")

    def SaveMetaData(self, trackInfoJSON):
        logger.info("[metadata] Getting album art: " + trackInfoJSON["album_art_640"])

        albumArtBinary = urlopen(trackInfoJSON["album_art_640"]).read()

        logger.info("[metadata] Album art retrieved.")

        trackId = trackInfoJSON["track_id"]

        audioFile = MP4(f"{trackId}.m4a")

        audioFile["covr"] = [MP4Cover(albumArtBinary, imageformat=MP4Cover.FORMAT_JPEG)]
        audioFile["\xa9nam"] = trackInfoJSON["track_name"]
        audioFile["\xa9alb"] = trackInfoJSON["album_name"]
        audioFile["\xa9ART"] = "/".join(trackInfoJSON["track_artists"])
        audioFile["aART"] = "/".join(trackInfoJSON["album_artists"])
        audioFile["\xa9day"] = trackInfoJSON["year"]
        audioFile["trkn"] = [
            (trackInfoJSON["track_number"], trackInfoJSON["album_length"])
        ]
        audioFile["\xa9cmt"] = (
            "https://open.spotify.com/track/46qPfZshPjoitCKdKVD6k7/"
            + trackInfoJSON["track_id"]
        )
        audioFile.save()

        logger.info(f"[metadata] Successfully added meta data to track ID: {trackId}.")

    def SearchYoutube(self, keyword, offset, mode, maxResults):
        if keyword != None:
            search = SearchVideos(keyword, offset, mode, maxResults)
            return Response(
                search.result(),
                headers={"Content-Type": "application/json"},
                status=200,
            )
        else:
            return make_response("bad request", 400)

    def TrackDownload(self, trackId, trackName):

        if trackId != None:
            try:
                logger.info(f"[server] Download request in ID format.")
                trackInfo = self.TrackInfo(trackId).json
                logger.info(
                    f"[info] Successfully retrieved metadata of track ID: {trackId}."
                )
                artists = " ".join(trackInfo["album_artists"])
                videoId = self.SearchYoutube(
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
                ).json["search_result"][0]["id"]

                logger.info(f"[search] Search successful. Video ID: {videoId}.")

                self.SaveAudio(videoId, trackId)
                self.SaveMetaData(trackInfo)
                audioFile = open(f"{trackId}.m4a", "rb")
                audioBinary = audioFile.read()
                audioFile.close()
                logger.info(f"[server] Sending audio binary for track ID: {trackId}")

                response = make_response(audioBinary, 200)
                response.headers["track_name"] = trackInfo["track_name"]
                response.headers["album_name"] = trackInfo["album_name"]
                response.headers["Content-Length"] = len(audioBinary)
                response.headers["Content-Type"] = "audio/mp4"
                return response
            except:
                logger.exception("")
                return make_response("internal server error", 500)

        elif trackName != None:
            try:
                logger.info(f"[server] Download request in name format.")
                videoId = self.SearchYoutube(trackName, 1, "json", 1).json[
                    "search_result"
                ][0]["id"]
                logger.info(f"[search] Search successful. Video ID: {videoId}.")
                trackId = self.SearchSpotify(trackName, "track", 0, 1).json["tracks"][
                    0
                ]["track_id"]
                logger.info(
                    f"[tracksearch] Track Search successful. Track ID: {trackId}."
                )
                trackInfo = self.TrackInfo(trackId).json
                logger.info(
                    f"[info] Successfully retrieved metadata of track ID: {trackId}."
                )
                self.SaveAudio(videoId, trackId)
                self.SaveMetaData(trackInfo)
                audioFile = open(f"{trackId}.m4a", "rb")
                audioBinary = audioFile.read()
                audioFile.close()
                logger.info(f"[server] Sending audio binary for track ID: {trackId}")

                response = make_response(audioBinary, 200)
                response.headers["track_name"] = trackInfo["track_name"]
                response.headers["album_name"] = trackInfo["album_name"]
                response.headers["Content-Length"] = len(audioBinary)
                response.headers["Content-Type"] = "audio/mp4"
                return response
            except:
                logger.exception("")
                return make_response("internal server error", 500)
        else:
            return make_response("bad request", 400)
