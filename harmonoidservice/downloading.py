import httpx
from fastapi.responses import FileResponse, PlainTextResponse
import subprocess
import aiofiles
import aiofiles.os
import os
import sys
import asyncio
import ytmusicapi

MUSICAPI_VERSION = ytmusicapi.__version__


class DownloadHandler:
    async def trackDownload(self, trackId, albumId, trackName):
        if trackId:
            print(f"[server] Download request in ID format.")
        if trackName:
            print(f"[server] Download request in name format.")
            trackId = await self.ytMusic.searchYoutube(trackName, "songs")
            trackId = trackId[0]["videoId"]
        if os.path.isfile(f"{trackId}.webm"):
            print(
                f"[pytube] Track already downloaded for track ID: {trackId}.\n[server] Sending audio binary for track ID: {trackId}."
            )
            return FileResponse(
                f"{trackId}.webm",
                media_type="audio/webm",
                headers={"Accept-Ranges": "bytes"},
            )

        trackInfo = await self.trackInfo(trackId, albumId)
        if type(trackInfo) is dict:
            print(f"[ytmusicapi] Successfully retrieved metadata of track ID: {trackId}.")
            await self.saveAudio(trackId, trackInfo["url"])
            print(f"[server] Sending audio binary for track ID: {trackId}")
            return FileResponse(
                f"{trackId}.webm",
                media_type="audio/webm",
                headers={"Accept-Ranges": "bytes"},
            )
        else:
            print(f"[pytube] Could not retrieve metadata of track ID: {trackId}.")
            print(f"[server] Sending status code 500 for track ID: {trackId}.")
            return PlainTextResponse(
                content=trackInfo,
                status_code=500,
            )

    async def saveAudio(self, trackId, trackUrl):
        filename = f"{trackId}.webm"
        print(f"[download] Downloading track ID: {trackId}.")
        async with httpx.AsyncClient() as client:
            response = await client.get(trackUrl, timeout = None)
            trackBinary = response.content
        async with aiofiles.open(filename, "wb") as file:
            await file.write(trackBinary)
        print(f"[pytube] Track download successful for track ID: {trackId}.")

    """
    Yet to implement...
    """

    async def updateYTMusicAPI(self):
        async with httpx.AsyncClient() as client:
            latestVersion = await client.get(
                "https://api.github.com/repos/sigma67/ytmusicapi/release", timeout = None
            )
        latestVersion = latestVersion.json()[0]["tag_name"]

        global MUSICAPI_VERSION
        updated = latestVersion == MUSICAPI_VERSION
        print(f"[update] Installed ytmusicapi version  : {MUSICAPI_VERSION}.")
        print(f"[update] Latest ytmusicapi Version     : {latestVersion}.")
        if not updated:
            print("[update] Updating ytmusicapi...")
            cmd = f"{sys.executable} -m pip install --upgrade git+https://github.com/sigma67/ytmusicapi@master"

            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            while process.poll() is None:
                await asyncio.sleep(0.1)
            stdout, stderr = process.communicate()
            stdout, stderr = stdout.decode(), stderr.decode()

            if process.poll() == 0:
                MUSICAPI_VERSION = latestVersion
                print(f"[update] Updated To ytmusicapi version : {latestVersion}")
            else:
                print("[update] Failed to update.")
                print("[stdout]", stdout)
                print("[stderr]", stderr)
        else:
            print("[update] ytmusicapi is already updated.")
