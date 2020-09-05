import httpx
import base64
from fastapi import HTTPException
import logging
import ytmusicapi

logger = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(self, message):
        self.message = message


class BrowsingHandler:

    async def TrackInfo(self, trackId):
        track = await self.request(f"tracks/{trackId}")
        album_art_640 = ""
        album_art_300 = ""
        album_art_64 = ""
        for image in track["album"]["images"]:
            if image["height"] == 640:
                album_art_640 = image["url"]
            elif image["height"] == 300:
                album_art_300 = image["url"]
            elif image["height"] == 64:
                album_art_64 = image["url"]
        a_artists = track["album"]["artists"]
        album_artists = []
        for artist in a_artists:
            album_artists += [
                artist["name"]
            ]
        t_artists = track["artists"]
        track_artists = []
        for artist in t_artists:
            track_artists += [
                artist["name"]
            ]
        return {
            "track_id": track["id"],
            "track_name": track["name"],
            "track_artists": track_artists,
            "track_number": track["track_number"],
            "track_duration": track["duration_ms"],
            "album_art_640": album_art_640,
            "album_art_300": album_art_300,
            "album_art_64": album_art_64,
            "album_id": track["album"]["id"],
            "album_name": track["album"]["name"],
            "year": track["album"]["release_date"].split("-")[0],
            "album_artists": album_artists,
            "album_length": track["album"]["total_tracks"],
            "album_type": track["album"]["album_type"],
        }

    async def AlbumInfo(self, albumId):
        response = await self.request(
            f"albums/{albumId}/tracks", {"limit": 50, "offset": 0}
        )
        tracks = response["items"]
        result = []
        for track in tracks:
            t_artists = track["artists"]
            track_artists = []
            for artist in t_artists:
                track_artists += [
                    artist["name"]
                ]
            result += [
                {
                    "track_id": track["id"],
                    "track_name": track["name"],
                    "track_artists": track_artists,
                    "track_number": track["track_number"],
                    "track_duration": track["duration_ms"],
                }
            ]
        return {"tracks": result}

    async def ArtistAlbums(self, artistId):
        artistAlbumsJson = await self.request(f"artists/{artistId}/albums")
        artistAlbums = []
        albums = []
        for album in artistAlbumsJson["items"]:
            album_art_640 = ""
            album_art_300 = ""
            album_art_64 = ""
            album_artists = []
            a_artists = album["artists"]
            for artist in a_artists:
                album_artists += [
                    artist["name"]
                ]
            for image in album["images"]:
                if image["height"] == 640:
                    album_art_640 = image["url"]
                elif image["height"] == 300:
                    album_art_300 = image["url"]
                elif image["height"] == 64:
                    album_art_64 = image["url"]
            artistAlbums += [
                {
                    "album_id": album["id"],
                    "album_name": album["name"],
                    "year": album["release_date"].split("-")[0],
                    "album_artists": album_artists,
                    "album_art_640": album_art_640,
                    "album_art_300": album_art_300,
                    "album_art_64": album_art_64,
                    "album_length": album["total_tracks"],
                    "album_type": album["album_type"],
                }
            ]
        return {"albums": artistAlbums}

    async def ArtistTracks(self, artistId, country):
        artistTracksJson = await self.request(
            f"artists/{artistId}/top-tracks?country={country}"
        )
        artistTracks = []
        albums = []
        for track in artistTracksJson["tracks"]:
            album_art_640 = ""
            album_art_300 = ""
            album_art_64 = ""
            album_artists = []
            a_artists = track["artists"]
            for artist in a_artists:
                album_artists += [
                    artist["name"]
                ]
            t_artists = track["artists"]
            track_artists = []
            for artist in t_artists:
                track_artists += [
                    artist["name"]
                ]
            for image in track["album"]["images"]:
                if image["height"] == 640:
                    album_art_640 = image["url"]
                elif image["height"] == 300:
                    album_art_300 = image["url"]
                elif image["height"] == 64:
                    album_art_64 = image["url"]
            artistTracks += [
                {
                    "track_id": track["id"],
                    "track_name": track["name"],
                    "track_artists": track_artists,
                    "track_number": track["track_number"],
                    "track_duration": track["duration_ms"],
                    "album_art_640": track["album"]["images"][0]["url"],
                    "album_art_300": track["album"]["images"][1]["url"],
                    "album_art_64": track["album"]["images"][2]["url"],
                    "album_id": track["album"]["id"],
                    "album_name": track["album"]["name"],
                    "year": track["album"]["release_date"].split("-")[0],
                    "album_artists": album_artists,
                    "album_length": track["album"]["total_tracks"],
                    "album_type": track["album"]["album_type"],
                }
            ]
        return {"albums": artistTracks}

    async def SearchSpotify(self, keyword, mode, offset, limit):
        if mode == "album":
            youtubeResult = self.ytmusic.search(keyword, filter = "albums")
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
                        "album_artists": album["artist"],
                        "album_art_640": album_art_640,
                        "album_art_300": album_art_300,
                        "album_art_64": album_art_64,
                        "album_type": album["type"].lower(),
                    }
                ]
            return {"albums": albums}

        if mode == "track":
            youtubeResult = self.ytmusic.search(keyword, filter = "songs")
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
                t_artists = track["artists"]
                track_artists = []
                for artist in t_artists:
                    track_artists += [
                        artist["name"]
                    ]
                tracks += [
                    {
                        "track_id": track["videoId"],
                        "track_name": track["title"],
                        "track_artists": track_artists,
                        "track_duration": (int(track["duration"].split(":")[0]) * 60 + int(track["duration"].split(":")[1])) * 1000,
                        "album_id": track["album"]["id"],
                        "album_name": track["album"]["name"],
                        "album_art_640": album_art_640,
                        "album_art_300": album_art_300,
                        "album_art_64": album_art_64,
                    }
                ]
            return {"tracks": tracks}

        if mode == "artist":
            youtubeResult = self.ytmusic.search(keyword, filter = "artists")
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
