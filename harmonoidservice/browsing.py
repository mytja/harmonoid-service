import httpx
import base64
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(self, message):
        self.message = message


class BrowsingHandler:
    async def TrackInfo(self, trackId):
        track = await self.ytMusic._get_song(trackId)
        album_art_640 = ""
        album_art_300 = ""
        album_art_64 = ""
        for image in track["thumbnail"]["thumbnails"]: # UNDEFINED: 16:9 ratio
            if image["height"] == 544:
                album_art_640 = image["url"]
            elif image["height"] == 226:
                album_art_300 = image["url"]
            elif image["height"] == 60:
                album_art_64 = image["url"]
        track_artists = track.get("artists", [track["author"]])
        album_artists = track_artists  # UNDEFINED so we use track_artists
        return {
            "track_id": track["videoId"],
            "track_name": track["title"],
            "track_artists": track_artists,
            "track_number": 1,  # UNDEFINED
            "track_duration": int(track["lengthSeconds"]) * 1000,
            "album_art_640": album_art_640,
            "album_art_300": album_art_300,
            "album_art_64": album_art_64,
            "album_id": "",  # UNDEFINED
            "album_name": "",  # UNDEFINED
            "year": track["release"].split("-")[0] if "release" in track else "",
            "album_artists": album_artists,
            "album_length": 1,  # UNDEFINED
            "album_type": "album",  # UNDEFINED
        }

    async def AlbumInfo(self, albumId):
        response = await self.ytMusic._get_album(albumId)
        tracks = response["tracks"]
        result = []
        for track in tracks:
            result += [
                {
                    "track_id": track["videoId"],
                    "track_name": track["title"],
                    "track_artists": [track["artists"]],
                    "track_number": track["index"],
                    "track_duration": int(track["lengthMs"]),
                }
            ]
        return {"tracks": result}

    async def ArtistAlbums(self, artistId):
        # обьединить с singles
        artistJson = await self.ytMusic._get_artist(artistId)
        artistAlbums = []
        for album in artistJson["albums"]["results"]:
            album_art_640 = ""
            album_art_300 = ""
            album_art_64 = ""
            for image in album["thumbnails"]:
                if image["height"] == 544:
                    album_art_640 = image["url"]
                elif image["height"] == 226:
                    album_art_300 = image["url"]
                elif image["height"] == 60:
                    album_art_64 = image["url"]
            artistAlbums += [
                {
                    "album_id": album["browseId"],
                    "album_name": album["title"],
                    "year": album["year"],
                    "album_artists": [artistJson["name"]],
                    "album_art_640": album_art_640,
                    "album_art_300": album_art_300,
                    "album_art_64": album_art_64,
                    "album_length": 1,  # UNDEFINED
                    "album_type": "album",  # UNDEFINED
                }
            ]
        return {"albums": artistAlbums}

    async def ArtistTracks(self, artistId):
        artistJson = await self.ytMusic._get_artist(artistId)
        artistTracks = []
        for track in artistJson["songs"]["results"]:
            album_art_640 = ""
            album_art_300 = ""
            album_art_64 = ""
            track_artists = [a["name"] for a in track["artists"]]
            album_artists = track_artists  # UNDEFINED so we use track_artists
            for image in track["thumbnails"]:
                if image["height"] == 544:
                    album_art_640 = image["url"]
                elif image["height"] == 120:
                    album_art_300 = image["url"]
                elif image["height"] == 60:
                    album_art_64 = image["url"]
            artistTracks += [
                {
                    "track_id": track["videoId"],
                    "track_name": track["title"],
                    "track_artists": track_artists,
                    "track_number": 1,  # UNDEFINED
                    "track_duration": 1,  # UNDEFINED
                    "album_art_640": album_art_640,
                    "album_art_300": album_art_300,
                    "album_art_64": album_art_64,
                    "album_id": track["album"]["id"],
                    "album_name": track["album"]["name"],
                    "year": "0000",  # UNDEFINED
                    "album_artists": album_artists,
                    "album_length": 1,  # UNDEFINED
                    "album_type": "album",  # UNDEFINED
                }
            ]
        return {"albums": artistTracks}

    async def SearchYoutube(self, keyword, mode):
        if mode == "album":
            youtubeResult = await self.ytMusic._search(keyword, "albums")
            albums = []
            for album in youtubeResult:
                album_art_640 = ""
                album_art_300 = ""
                album_art_64 = ""
                for image in album["thumbnails"]:
                    if image["height"] == 544:
                        album_art_640 = image["url"]
                    elif image["height"] == 226:
                        album_art_300 = image["url"]
                    elif image["height"] == 60:
                        album_art_64 = image["url"]
                albums += [
                    {
                        "album_id": album["browseId"],
                        "album_name": album["title"],
                        "year": album["year"],
                        "album_artists": [album["artist"]],
                        "album_art_640": album_art_640,
                        "album_art_300": album_art_300,
                        "album_art_64": album_art_64,
                        "album_length": 1, # UNDEFINED
                        "album_type": album["type"].lower(),
                    }
                ]
            return {"albums": albums}

        if mode == "track":
            youtubeResult = await self.ytMusic._search(keyword, "songs")
            tracks = []
            for track in youtubeResult:
                album_art_640 = ""
                album_art_300 = ""
                album_art_64 = ""
                for image in track["thumbnails"]:
                    if image["height"] == 544:
                        album_art_640 = image["url"]
                    elif image["height"] == 226:
                        album_art_300 = image["url"]
                    elif image["height"] == 60:
                        album_art_64 = image["url"]
                track_artists = [a["name"] for a in track["artists"]]
                tracks += [
                    {
                        "track_id": track["videoId"],
                        "track_name": track["title"],
                        "track_artists": track_artists,
                        "track_duration": (
                            int(track["duration"].split(":")[0]) * 60
                            + int(track["duration"].split(":")[1])
                        )
                        * 1000,
                        "album_id": track["album"]["id"],
                        "album_name": track["album"]["name"],
                        "album_art_640": album_art_640,
                        "album_art_300": album_art_300,
                        "album_art_64": album_art_64,
                    }
                ]
            return {"tracks": tracks}

        if mode == "artist":
            youtubeResult = await self.ytMusic._search(keyword, "artists")
            artists = []
            for artist in youtubeResult:
                artist_art_640 = ""
                artist_art_300 = ""
                artist_art_64 = ""
                for image in artist["thumbnails"]:
                    if image["height"] == 544:
                        artist_art_640 = image["url"]
                    elif image["height"] == 226:
                        artist_art_300 = image["url"]
                    elif image["height"] == 60:
                        artist_art_64 = image["url"]
                artists += [
                    {
                        "artist_id": artist["browseId"],
                        "artist_name": artist["artist"],
                        "artist_art_640": artist_art_640,
                        "artist_art_300": artist_art_300,
                        "artist_art_64": artist_art_64,
                    }
                ]
            return {"artists": artists}
