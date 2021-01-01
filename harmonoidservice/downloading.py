import httpx
from fastapi.responses import FileResponse, PlainTextResponse
import subprocess
import aiofiles.os
import os
import sys
import asyncio
from .async_mutagen import MP3
from pytube import *
import ytmusicapi
import time

#CURRENT_VERSION = __version__  # just to avoid reimports
MUSICAPI_VERSION = ytmusicapi.__version__


class DownloadHandler:
    async def UpdateYTMusicAPI(self):
        async with httpx.AsyncClient() as client:
            latestVersion = await client.get("https://api.github.com/repos/sigma67/ytmusicapi/release")
        latestVersion = latestVersion.text
        
        jsonLoad = json.loads(latestVersion)[0]["tag_name"]
        
        updated = (jsonLoad == MUSICAPI_VERSION)
        print(f"[update] Installed ytmusicapi version  : {MUSICAPI_VERSION}.")
        print(f"[update] Latest ytmusicapi Version     : {jsonLoad}.")
        if not updated:
            print("[update] Updating ytmusicapi...")
            cmd = f"{sys.executable} -m pip install --upgrade ytmusicapi"

            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            while process.poll() is None:
                await asyncio.sleep(0.1)
            stdout, stderr = process.communicate()
            stdout, stderr = stdout.decode(), stderr.decode()

            if process.poll() == 0:
                MUSICAPI_VERSION = jsonLoad
                print(
                    f"[update] Updated To ytmusicapi version : {latestVersion}"
                )
            else:
                print("[update] Failed to update.")
                print("[stdout]", stdout)
                print("[stderr]", stderr)
        else:
            print("[update] ytmusicapi is already updated.")
    async def SaveAudio(self, trackId):
        # Download
        yt = YouTube('https://youtube.com/watch?v='+trackId)
        yt_streams = yt.streams.filter(only_audio=True).order_by("abr").desc()
        print("[pytube] YT streams avaiable")
        print(yt_streams)
        yt_streams = yt_streams.first().download()
        
        cmd = 'mv "'+yt_streams+'" '+trackId+".webm"
        print("[cmd] Command: "+cmd)
        os.system(cmd)
        
        #Success!
        print(f"[youtube] Track download successful for track ID: {trackId}.")
        return (True, None)
        #RP
        #except:
            #print(f"[youtube] Track download unsuccessful for track ID: {trackId}.")
            #print(f"[metadata] Skipped adding metadata to track ID: {trackId}.")
            #return (False, None)

    async def SaveMetaData(self, trackInfoJSON):
        art = (
            trackInfoJSON["album_art_640"]
            or trackInfoJSON["album_art_300"]
            or trackInfoJSON["album_art_64"]
        )

        trackId = trackInfoJSON["track_id"]

        audioFile = MP3(f"{trackId}.webm", trackInfoJSON, art)
        await audioFile.init()

        print(f"[metadata] Successfully added metadata to track ID: {trackId}.")

    async def TrackDownload(self, trackId, albumId, trackName, retry=True):
        start_time = time.time()
        
        if trackId:
            print(f"[server] Download request in ID format.")
        if trackName:
            print(f"[server] Download request in name format.")
            trackId = await self.ytMusic._search(trackName, "songs")
            trackId = trackId[0]["videoId"]

        if os.path.isfile(f"{trackId}.webm"):
            print(
                f"[youtube] Track already downloaded for track ID: {trackId}.\n[server] Sending audio binary for track ID: {trackId}."
            )
            print("[speed] Returning already downloaded file took %s seconds" % (time.time() - start_time))
            return FileResponse(
                f"{trackId}.webm",
                media_type="audio/opus",
                headers={"Accept-Ranges": "bytes"},
            )

        trackInfo = await self.TrackInfo(trackId, albumId)
        if type(trackInfo) == dict:
            print(f"[youtube] Successfully retrieved metadata of track ID: {trackId}.")

            status, error = await self.SaveAudio(trackId)
            if status:
                #await self.SaveMetaData(trackInfo)

                print(f"[server] Sending audio binary for track ID: {trackId}")
                print("[speed] Downloading, adding metadata and returning took %s seconds" % (time.time() - start_time))
                return FileResponse(
                    f"{trackId}.webm",
                    media_type="audio/opus",
                    headers={"Accept-Ranges": "bytes"},
                )
            else:
                 if retry:
                     print("\n[diagnosis] (1/2) Deleting cookies file.")
                     await aiofiles.os.remove("cookies.txt")
                     print("\n[diagnosis] (2/2) Updating YTMusicAPI.")
                     await UpdateYTMusicAPI()
                     print(f"[diagnosis] Retrying download for track ID: {trackId}.\n")
                     updatedResponse = await self.TrackDownload(
                         trackId, albumId, trackName, retry=False
                     )
                     return updatedResponse
                 print("\n[diagnosis] Diagnosis finished without success!")
                 print(f"[server] Sending status code 500 for track ID: {trackId}.")
                 print("[speed] Fail with diagnosis took %s seconds" % (time.time() - start_time))
                 return PlainTextResponse(
                    content=f"Internal Server Error.\nYouTube-DL Failed.\n{str(error)}",
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
