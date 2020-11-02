import httpx
from urllib.request import urlopen
from fastapi.responses import FileResponse, PlainTextResponse
import subprocess
import os
import sys
from .async_mutagen import MP4, MP4Cover


class DownloadHandler:
    def UpdateYoutubeDl(self):
        import youtube_dl

        latestVersion = [
            element[2:-1]
            for element in urlopen("http://youtube-dl.org/")
            .read()
            .decode("utf_8")
            .split(" ")
            if element[0:2] == "(v"
        ][0]
        updated = latestVersion == youtube_dl.version.__version__
        print(
            f"[update] Installed YouTube-DL version  : {youtube_dl.version.__version__}.\n[update] Latest YouTube-DL Version     : {latestVersion}."
        )
        if not updated:
            print("[update] Updating YouTube-DL...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", "youtube_dl"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

            modules = []
            for module in sys.modules.keys():
                if module.startswith("youtube_dl"):
                    modules += [module]
            for module in modules:
                del sys.modules[module]
            import youtube_dl

            print(
                f"[update] Updated To YouTube-DL version : {youtube_dl.version.__version__}"
            )
        else:
            print("[update] YouTube-DL is already updated.")

    async def SaveAudio(self, trackId):
        import youtube_dl

        try:
            ydl_opts = {
                "format": "140",
                "cookiefile": "cookies.txt",
                "outtmpl": f"{trackId}.m4a",
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={trackId}"])
            print(f"[youtube] Track download successful for track ID: {trackId}.")
            return [True, None]
        except Exception as error:
            print(
                f"[youtube] Track download unsuccessful for track ID: {trackId}.\n[metadata] Skipped adding metadata to track ID: {trackId}."
            )
            return [False, error]

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

    async def TrackDownload(self, trackId, albumId, trackName, reTry=True):

        if os.path.exists(f"{trackId}.m4a"):
            print(
                f"[youtube] Track already downloaded for track ID: {trackId}.\n[server] Sending audio binary for track ID: {trackId}."
            )
            return FileResponse(
                f"{trackId}.m4a",
                media_type="audio/mp4",
                headers={"Accept-Ranges": "bytes"},
            )

        if trackId:
            print(f"[server] Download request in ID format.")
        if trackName:
            print(f"[server] Download request in name format.")
            trackId = await self.ytMusic._search(trackName, "songs")
            trackId = trackId[0]["videoId"]

        trackInfo = await self.TrackInfo(trackId, albumId)

        if type(trackInfo) == dict:
            print(f"[youtube] Successfully retrieved metadata of track ID: {trackId}.")

            downloadResult = await self.SaveAudio(trackId)
            if downloadResult[0]:
                await self.SaveMetaData(trackInfo)
                print(f"[server] Sending audio binary for track ID: {trackId}.")
                return FileResponse(
                    f"{trackId}.m4a",
                    media_type="audio/mp4",
                    headers={"Accept-Ranges": "bytes"},
                )
            else:
                if reTry:
                    print("\n[diagnosis] (1/2) Deleting cookies file.")
                    os.remove("cookies.txt")
                    print("[diagnosis] (2/2) Attempting to update YouTube-DL.")
                    self.UpdateYoutubeDl()
                    print(f"[diagnosis] Retrying download for track ID: {trackId}.\n")
                    updatedResponse = await self.TrackDownload(
                        trackId, albumId, trackName, reTry=False
                    )
                    return updatedResponse
                else:
                    print(f"[server] Sending status code 500 for track ID: {trackId}.")
                    return PlainTextResponse(
                        content=f"Internal Server Error.\nYouTube-DL Failed.\n{str(downloadResult[1])}",
                        status_code=500,
                    )
        else:
            print(f"[youtube] Could not retrieve metadata of track ID: {trackId}.")
            print(f"[server] Sending status code 500 for track ID: {trackId}.")
            return PlainTextResponse(
                content=trackInfo,
                status_code=500,
            )
