import httpx
from fastapi.responses import FileResponse, PlainTextResponse
import subprocess
import aiofiles.os
import os
import sys
import asyncio
from .async_mutagen import MP4, MP4Cover
import youtube_dl

CURRENT_VERSION = youtube_dl.version.__version__  # just to avoid reimports

class DownloadHandler:
    async def UpdateYoutubeDl(self):
        async with httpx.AsyncClient() as client:
            latestVersion = await client.get("https://yt-dl.org/update/LATEST_VERSION")
        latestVersion = latestVersion.text

        global CURRENT_VERSION
        updated = (latestVersion == CURRENT_VERSION)
        print(f"[update] Installed YouTube-DL version  : {CURRENT_VERSION}.")
        print(f"[update] Latest YouTube-DL Version     : {latestVersion}.")
        if not updated:
            print("[update] Updating YouTube-DL...")
            cmd = f"{sys.executable} -m pip install --upgrade youtube_dl"

            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            while process.poll() is None:
                await asyncio.sleep(0.1)
            stdout, stderr = process.communicate()
            stdout, stderr = stdout.decode(), stderr.decode()

            if process.poll() == 0:
                CURRENT_VERSION = latestVersion
                print(
                    f"[update] Updated To YouTube-DL version : {latestVersion}"
                )
            else:
                print("[update] Failed to update.")
                print("[stdout]", stdout)
                print("[stderr]", stderr)
        else:
            print("[update] YouTube-DL is already updated.")

    async def SaveAudio(self, trackId):
        COMMAND = 'youtube-dl -i --format "140" --extract-audio --audio-format m4a --no-playlist --cookies cookies.txt -x -o "{output}.%(ext)s" "{url}"'

        cmd = COMMAND.format(output=trackId, url=f"https://www.youtube.com/watch?v={trackId}")
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        while process.poll() is None:
            await asyncio.sleep(0.1)
        stdout, stderr = process.communicate()
        stdout, stderr = stdout.decode(), stderr.decode()

        print("[stdout]", stdout)
        print("[stderr]", stderr)  # sometimes YT-DL returns status code 0 even with an error occurred

        if process.poll() == 0 and "ERROR" not in stderr:
            print(f"[youtube] Track download successful for track ID: {trackId}.")
            return (True, None)
        else:
            print(f"[youtube] Track download unsuccessful for track ID: {trackId}.")
            print(f"[metadata] Skipped adding metadata to track ID: {trackId}.")
            return (False, stderr)

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
            print("[metadata] Getting album art: " + art)
            async with httpx.AsyncClient() as client:
                response = await client.get(art)
            albumArtBinary = response.content
            print("[metadata] Album art retrieved.")
            cover = MP4Cover(albumArtBinary, imageformat=MP4Cover.FORMAT_JPEG)
            await cover.init()
            audioFile["covr"] = [cover]
        else:
            print("[metadata] Album art is not found.")

        audioFile["\xa9nam"] = trackInfoJSON["track_name"]
        audioFile["\xa9alb"] = trackInfoJSON["album_name"]
        audioFile["\xa9ART"] = "/".join(trackInfoJSON["track_artists"])
        if len(trackInfoJSON["album_artists"]) != 0:
            audioFile["aART"] = trackInfoJSON["album_artists"][0]
        audioFile["\xa9day"] = trackInfoJSON["year"]
        audioFile["trkn"] = [
            (trackInfoJSON["track_number"], trackInfoJSON["album_length"])
        ]
        audioFile["\xa9cmt"] = (
            "https://music.youtube.com/watch?v=" + trackInfoJSON["track_id"]
        )
        await audioFile._save()

        print(f"[metadata] Successfully added metadata to track ID: {trackId}.")

    async def TrackDownload(self, trackId, albumId, trackName, retry=True):
        if trackId:
            print(f"[server] Download request in ID format.")
        if trackName:
            print(f"[server] Download request in name format.")
            trackId = await self.ytMusic._search(trackName, "songs")
            trackId = trackId[0]["videoId"]

        if os.path.exists(f"{trackId}.m4a"):
            print(
                f"[youtube] Track already downloaded for track ID: {trackId}.\n[server] Sending audio binary for track ID: {trackId}."
            )
            return FileResponse(
                f"{trackId}.m4a",
                media_type="audio/mp4",
                headers={"Accept-Ranges": "bytes"},
            )

        trackInfo = await self.TrackInfo(trackId, albumId)

        if type(trackInfo) == dict:
            print(f"[youtube] Successfully retrieved metadata of track ID: {trackId}.")

            status, error = await self.SaveAudio(trackId)
            if status is True:
                await self.SaveMetaData(trackInfo)
                print(f"[server] Sending audio binary for track ID: {trackId}.")
                return FileResponse(
                    f"{trackId}.m4a",
                    media_type="audio/mp4",
                    headers={"Accept-Ranges": "bytes"},
                )
            else:
                if retry:
                    print("\n[diagnosis] (1/2) Deleting cookies file.")
                    await aiofiles.os.remove("cookies.txt")
                    print("[diagnosis] (2/2) Attempting to update YouTube-DL.")
                    await self.UpdateYoutubeDl()
                    print(f"[diagnosis] Retrying download for track ID: {trackId}.\n")
                    updatedResponse = await self.TrackDownload(
                        trackId, albumId, trackName, retry=False
                    )
                    return updatedResponse
                else:
                    print(f"[server] Sending status code 500 for track ID: {trackId}.")
                    return PlainTextResponse(
                        content=f"Internal Server Error.\nYouTube-DL Failed.\n{str(error)}",
                        status_code=500,
                    )
        else:
            print(f"[youtube] Could not retrieve metadata of track ID: {trackId}.")
            print(f"[server] Sending status code 500 for track ID: {trackId}.")
            return PlainTextResponse(
                content=trackInfo,
                status_code=500,
            )
