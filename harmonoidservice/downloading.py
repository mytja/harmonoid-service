import httpx
from fastapi.responses import FileResponse, PlainTextResponse
import subprocess
import aiofiles.os
import os
import sys
import asyncio
from .async_mutagen import MP3
import youtube_dl
from pytube import YouTube

#CURRENT_VERSION = pytube.version.__version__  # just to avoid reimports


class DownloadHandler:
    """
    async def UpdatePyTube(self):
        async with httpx.AsyncClient() as client:
            latestVersion = await client.get("https://api.github.com/repos/nficano/pytube/releases")
        latestVersion = latestVersion.text[0]["tag_name"]

        global CURRENT_VERSION
        updated = latestVersion == CURRENT_VERSION
        print(f"[update] Installed PyTube version  : {CURRENT_VERSION}.")
        print(f"[update] Latest PyTube Version     : {latestVersion}.")
        if not updated:
            print("[update] Updating PyTube...")
            cmd = f"{sys.executable} -m pip install --upgrade pytube"

            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            while process.poll() is None:
                await asyncio.sleep(0.1)
            stdout, stderr = process.communicate()
            stdout, stderr = stdout.decode(), stderr.decode()

            if process.poll() == 0:
                CURRENT_VERSION = latestVersion
                print(f"[update] Updated To PyTube version : {latestVersion}")
            else:
                print("[update] Failed to update.")
                print("[stdout]", stdout)
                print("[stderr]", stderr)
        else:
            print("[update] PyTube is already updated.")
    """
    async def SaveAudio(self, trackId):
        try:
            yt = YouTube('http://youtube.com/watch?v='+trackId).streams.filter(only_audio=True).first().download()
            cmd = "ffmpeg -i "+yt+" "+trackId+".mp3"
            print("[conversion] CMD line: "+cmd
            os.system(cmd)
            os.rename(yt, trackId+".mp3")
            print(f"[youtube] Track download successful for track ID: {trackId}.")
            return (True, None)
        #RP
        except:
            print(f"[youtube] Track download unsuccessful for track ID: {trackId}.")
            print(f"[metadata] Skipped adding metadata to track ID: {trackId}.")
            return (False, None)

    async def SaveMetaData(self, trackInfoJSON):
        art = (
            trackInfoJSON["album_art_640"]
            or trackInfoJSON["album_art_300"]
            or trackInfoJSON["album_art_64"]
        )

        trackId = trackInfoJSON["track_id"]

        audioFile = MP3(f"{trackId}.mp3", trackInfoJSON, art)
        await audioFile.init()

        print(f"[metadata] Successfully added metadata to track ID: {trackId}.")

    async def TrackDownload(self, trackId, albumId, trackName, retry=True):
        if trackId:
            print(f"[server] Download request in ID format.")
        if trackName:
            print(f"[server] Download request in name format.")
            trackId = await self.ytMusic._search(trackName, "songs")
            trackId = trackId[0]["videoId"]

        if os.path.isfile(f"{trackId}.mp3"):
            print(
                f"[youtube] Track already downloaded for track ID: {trackId}.\n[server] Sending audio binary for track ID: {trackId}."
            )
            return FileResponse(
                f"{trackId}.mp3",
                media_type="audio/mpeg",
                headers={"Accept-Ranges": "bytes"},
            )

        trackInfo = await self.TrackInfo(trackId, albumId)
        if type(trackInfo) == dict:
            print(f"[youtube] Successfully retrieved metadata of track ID: {trackId}.")

            status, error = await self.SaveAudio(trackId)
            if status:
                await self.SaveMetaData(trackInfo)

                print(f"[server] Sending audio binary for track ID: {trackId}")
                return FileResponse(
                    f"{trackId}.mp3",
                    media_type="audio/mpeg",
                    headers={"Accept-Ranges": "bytes"},
                )
            else:
                 if retry:
                     print("\n[diagnosis] (1/1) Deleting cookies file.")
                     await aiofiles.os.remove("cookies.txt")
                     print(f"[diagnosis] Retrying download for track ID: {trackId}.\n")
                     updatedResponse = await self.TrackDownload(
                         trackId, albumId, trackName, retry=False
                     )
                     return updatedResponse
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
