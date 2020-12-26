import httpx
from fastapi.responses import FileResponse, PlainTextResponse
import subprocess
import aiofiles
import aiofiles.os
import os
import sys
import asyncio
from .async_mutagen import MP3
from pytube import YouTube
import ytmusicapi
import time

MUSICAPI_VERSION = ytmusicapi.__version__


class DownloadHandler:
    async def UpdateYTMusicAPI(self):
        async with httpx.AsyncClient() as client:
            latestVersion = await client.get(
                "https://api.github.com/repos/sigma67/ytmusicapi/release"
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

    def _getUrl(self, trackId):
        # (url, extension)
        yt = YouTube("https://youtube.com/watch?v=" + trackId)
        yt_streams = yt.streams.filter(only_audio=True).order_by("abr").desc()
        print(f"[pytube] {len(yt_streams)} YT streams avaiable")
        stream = yt_streams.first()
        if stream:
            return (stream.url, stream.default_filename.split(".")[-1])
        return (None, None)

    async def SaveAudio(self, trackId):
        # (status, reason)
        loop = asyncio.get_running_loop()
        url, ext = await loop.run_in_executor(None, self._getUrl, trackId)

        if not url:
            return (False, "Stream not found")

        filename = f"{trackId}.{ext}"

        print("[downloading] Downloading to " + filename)
        async with httpx.AsyncClient() as client:
            # simple, but eats RAM:
            # async with aiofiles.open(filename, "wb") as file:
            #     await file.write(await client.get(url))
            async with client.stream("GET", url) as response:
                async with aiofiles.open(filename, "wb") as file:
                    async for chunk in response.aiter_bytes():
                        await file.write(chunk)

        if ext != "mp3":
            print("[conversion] Stream isn't mp3. Converting")
            cmd = 'ffmpeg -i "' + filename + '" ' + trackId + ".mp3"

            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            while process.poll() is None:
                await asyncio.sleep(0.1)
            stdout, stderr = process.communicate()
            stdout, stderr = stdout.decode(), stderr.decode()
            if process.poll() != 0:
                print("[stdout]", stdout)
                print("[stderr]", stderr)
                return (False, "Couldn't convert")

            asyncio.create_task(aiofiles.os.remove(filename))

        print(f"[youtube] Track download successful for track ID: {trackId}.")
        return (True, None)

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

    async def TrackDownload(self, trackId, albumId, trackName):
        start_time = time.time()

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
            print(
                "[speed] Returning already downloaded file took %s seconds"
                % (time.time() - start_time)
            )
            return FileResponse(
                f"{trackId}.mp3",
                media_type="audio/mpeg",
                headers={"Accept-Ranges": "bytes"},
            )

        trackInfo = await self.TrackInfo(trackId, albumId)
        if type(trackInfo) == dict:
            print(f"[youtube] Successfully retrieved metadata of track ID: {trackId}.")

            status, reason = await self.SaveAudio(trackId)
            if status:
                await self.SaveMetaData(trackInfo)

                print(f"[server] Sending audio binary for track ID: {trackId}")
                print(
                    "[speed] Downloading, adding metadata and returning took %s seconds"
                    % (time.time() - start_time)
                )
                return FileResponse(
                    f"{trackId}.mp3",
                    media_type="audio/mpeg",
                    headers={"Accept-Ranges": "bytes"},
                )
            else:
                return PlainTextResponse(
                    content=reason,
                    status_code=500,
                )
        else:
            print(f"[youtube] Could not retrieve metadata of track ID: {trackId}.")
            print(f"[server] Sending status code 500 for track ID: {trackId}.")
            print("[speed] Fail took %s seconds" % (time.time() - start_time))
            return PlainTextResponse(
                content=trackInfo,
                status_code=500,
            )
