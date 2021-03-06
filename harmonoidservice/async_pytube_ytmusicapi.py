import asyncio
import httpx
import codecs
from typing import Dict
from urllib.parse import parse_qs
import json
from pytube.__main__ import apply_descrambler, apply_signature
from pytube import YouTube, extract
import pytube
from ytmusicapi import YTMusic

STREAM_ITAG = 251


class YouTube(YouTube):
    """
    Overrided parent's constructor.
    """

    def __init__(self):
        self.js_url = None
        self.js = None

    async def getStream(self, playerResponse: dict, itag: int):
        """
        Saving playerResponse inside a dictionary with key "player_response" for apply_descrambler & apply_signature methods.
        """
        self.player_response = {"player_response": playerResponse}
        self.video_id = playerResponse["videoDetails"]["videoId"]
        await self.decipher()
        for stream in self.player_response["url_encoded_fmt_stream_map"]:
            if stream["itag"] == itag:
                return stream["url"]

    """
    This method is derived from YouTube.prefetch.
    This method fetches player JavaScript & its URL from /watch endpoint on YouTube.
    Removed unnecessary methods & web requests as we already have metadata.
    Uses httpx.AsyncClient in place of requests.
    """

    async def getJS(self) -> None:
        async with httpx.AsyncClient() as client:
            """
            Removed v parameter from the query. (No idea about why PyTube bothered with that)
            """
            response = await client.get("https://www.youtube.com/", timeout=None)
            watch_html = response.text
        self.js_url = extract.js_url(watch_html)
        if pytube.__js_url__ != self.js_url:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.js_url, timeout=None)
                self.js = response.text
            pytube.__js__ = self.js
            pytube.__js_url__ = self.js_url
        else:
            self.js = pytube.__js__

    async def decipher(self, retry: bool = False):
        """
        Not fetching for new player JavaScript if pytube.__js__ is not None or exception is not caused.
        """
        if not pytube.__js__ or retry:
            await self.getJS()
        try:
            """
            These two are the main methods being used from PyTube.
            Used to decipher the stream URLs using player JavaScript & the player_response passed from the getStream method of this derieved class.
            These methods operate on the value of "player_response" key in dictionary of self.player_response & save deciphered information in the "url_encoded_fmt_stream_map" key.
            """
            apply_descrambler(self.player_response, "url_encoded_fmt_stream_map")
            apply_signature(
                self.player_response, "url_encoded_fmt_stream_map", pytube.__js__
            )
        except:
            """
            Fetch updated player JavaScript to get new cipher algorithm.
            """
            await self.decipher(retry=True)


class YTMusic(YTMusic):
    def __init__(
        self,
        auth: str = None,
        user: str = None,
        proxies: dict = None,
        language: str = "en",
    ):
        super().__init__(auth=auth, user=user, proxies=proxies, language=language)
        self.youtube = YouTube()

    """
    This method is derived from BrowsingMixin.get_song.
    It adds url key with direct stream URL to the result dictionary.
    Uses httpx.AsyncClient in place of requests.
    """

    async def getSong(self, videoId: str) -> Dict:
        endpoint = "https://www.youtube.com/get_video_info"
        params = {"video_id": videoId, "hl": self.language, "el": "detailpage"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                endpoint, params=params, headers=self.headers, timeout=None
            )
        text = parse_qs(response.text)
        if "player_response" not in text:
            return text
        player_response = json.loads(text["player_response"][0])
        song_meta = player_response["videoDetails"]
        """
        Get the stream URL using derieved YouTube class by parsing player_response & stream's ITAG.
        This method makes zero network requests (multiple additional requests being made by using vanilla PyTube & YTMusic). (*cough. Considering player JavaScript doesn't update out of nowhere)
        """
        url = await self.youtube.getStream(player_response, STREAM_ITAG)
        song_meta["url"] = url
        song_meta["category"] = player_response["microformat"][
            "playerMicroformatRenderer"
        ]["category"]
        if song_meta["shortDescription"].endswith("Auto-generated by YouTube."):
            try:
                description = song_meta["shortDescription"].split("\n\n")
                for i, detail in enumerate(description):
                    description[i] = codecs.escape_decode(detail)[0].decode("utf-8")
                song_meta["provider"] = description[0].replace(
                    "Provided to YouTube by ", ""
                )
                song_meta["artists"] = [
                    artist for artist in description[1].split(" · ")[1:]
                ]
                song_meta["copyright"] = description[3]
                song_meta["release"] = (
                    None
                    if len(description) < 5
                    else description[4].replace("Released on: ", "")
                )
                song_meta["production"] = (
                    None
                    if len(description) < 6
                    else [pub for pub in description[5].split("\n")]
                )
            except (KeyError, IndexError):
                pass
        return song_meta

    async def searchYoutube(self, query, filter):
        return await self.__run(self.search, query, filter)

    async def getArtist(self, channelId):
        return await self.__run(self.get_artist, channelId)

    async def getAlbum(self, browseId):
        return await self.__run(self.get_album, browseId)

    async def getWatchPlaylist(self, videoId):
        return await self.__run(self.get_watch_playlist, videoId)

    async def getLyrics(self, watchPlaylistId):
        return await self.__run(self.get_lyrics, watchPlaylistId)

    """
    Made run_in_executor method private.
    """

    async def __run(self, method, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, method, *args)
