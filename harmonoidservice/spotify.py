import httpx
import base64
import json
from flask import Response

import logging

logger = logging.getLogger(__name__)

class ApiError(Exception):
    def __init__(self, message):
        self.message = message

class SpotifyHandler:
    async def request(self, endpoint, parameters=None):
        token = await self.AccessToken()
        url = f"https://api.spotify.com/v1/{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url, params=parameters, headers={"Authorization": f"Bearer {token}"}
            )
        json = response.json()
        if "error" in json:
            raise ApiError(str(json))
        return json

    async def AccessToken(self):
        encoded = base64.b64encode(
            bytes(self.clientId + ":" + self.clientSecret, encoding="utf_8")
        ).decode("utf_8")
        data = {"grant_type": "client_credentials"}
        headers = {"Authorization": f"Basic {encoded}"}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://accounts.spotify.com/api/token",
                data=data,
                headers=headers,
            )
        return response.json()["access_token"]

    async def TrackInfo(self, trackId):
        if trackId == None:
            return Response("bad request", status=400)  # TODO: replace with FastAPI

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
                artist["name"].split("(")[0].strip().split("-")[0].strip()
            ]
        t_artists = track["artists"]
        track_artists = []
        for artist in t_artists:
            track_artists += [
                artist["name"].split("(")[0].strip().split("-")[0].strip()
            ]
        return Response(  # TODO: replace with FastAPI
            json.dumps(
                {
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
                },
                indent=4,
            ),
            headers={"Content-Type": "application/json"},
            status=200,
        )

    async def AlbumInfo(self, albumId):
        if albumId == None:
            return Response("bad request", status=400)  # TODO: replace with FastAPI

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
                    artist["name"].split("(")[0].strip().split("-")[0].strip()
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
        return Response(  # TODO: replace with FastAPI
            json.dumps({"tracks": result}, indent=4),
            headers={"Content-Type": "application/json"},
            status=200,
        )

    async def ArtistRelated(self, artistId):
        if artistId == None:
            return Response("bad request", status=400)  # TODO: replace with FastAPI

        relatedArtistsJson = await self.request(f"artists/{artistId}/related-artists")
        relatedArtists = []
        albums = []
        for artist in relatedArtistsJson["artists"]:
            artist_art_640 = ""
            artist_art_300 = ""
            artist_art_64 = ""
            for image in artist["images"]:
                if image["height"] == 640:
                    artist_art_640 = image["url"]
                elif image["height"] == 300:
                    artist_art_300 = image["url"]
                elif image["height"] == 64:
                    artist_art_64 = image["url"]
            relatedArtists += [
                {
                    "artist_id": artist["id"],
                    "artist_name": artist["name"]
                    .split("(")[0]
                    .strip()
                    .split("-")[0]
                    .strip(),
                    "artist_popularity": artist["popularity"],
                    "artist_art_640": artist_art_640,
                    "artist_art_300": artist_art_300,
                    "artist_art_64": artist_art_64,
                }
            ]
        return Response(  # TODO: replace with FastAPI
            json.dumps({"artists": relatedArtists}, indent=4),
            headers={"Content-Type": "application/json"},
            status=200,
        )

    async def ArtistAlbums(self, artistId):
        if artistId == None:
            return Response("bad request", status=400)

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
                    artist["name"].split("(")[0].strip().split("-")[0].strip()
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
        return Response(
            json.dumps({"albums": artistAlbums}, indent=4),
            headers={"Content-Type": "application/json"},
            status=200,
        )

    async def ArtistTracks(self, artistId):
        if artistId == None:
            return Response("bad request", status=400)  # TODO: replace with FastAPI

        artistTracksJson = await self.request(
            f"artists/{artistId}/top-tracks?country=us"
        )  # TODO: allow changing country
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
                    artist["name"].split("(")[0].strip().split("-")[0].strip()
                ]
            t_artists = track["artists"]
            track_artists = []
            for artist in t_artists:
                track_artists += [
                    artist["name"].split("(")[0].strip().split("-")[0].strip()
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
        return Response(  # TODO: replace with FastAPI
            json.dumps({"albums": artistTracks}, indent=4),
            headers={"Content-Type": "application/json"},
            status=200,
        )

    async def SearchSpotify(self, keyword, mode, offset, limit):
        if keyword == None:
            return Response("bad request", status=400)

        response = await self.request(
            "search", {"q": keyword, "type": mode, "limit": limit, "offset": offset}
        )
        if mode == "album":
            albums = []
            for album in response["albums"]["items"]:
                album_art_640 = ""
                album_art_300 = ""
                album_art_64 = ""
                for image in album["images"]:
                    if image["height"] == 640:
                        album_art_640 = image["url"]
                    elif image["height"] == 300:
                        album_art_300 = image["url"]
                    elif image["height"] == 64:
                        album_art_64 = image["url"]
                a_artists = album["artists"]
                album_artists = []
                for artist in a_artists:
                    album_artists += [
                        artist["name"].split("(")[0].strip().split("-")[0].strip()
                    ]
                albums += [
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
            return Response(  # TODO: replace with FastAPI
                json.dumps({"albums": albums}, indent=4),
                headers={"Content-Type": "application/json"},
                status=200,
            )
        if mode == "track":
            tracks = []
            for track in response["tracks"]["items"]:
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
                        artist["name"].split("(")[0].strip().split("-")[0].strip()
                    ]
                t_artists = track["artists"]
                track_artists = []
                for artist in t_artists:
                    track_artists += [
                        artist["name"].split("(")[0].strip().split("-")[0].strip()
                    ]
                tracks += [
                    {
                        "track_id": track["id"],
                        "track_name": track["name"],
                        "track_artists": album_artists,
                        "track_number": track["track_number"],
                        "track_duration": track["duration_ms"],
                        "album_id": track["album"]["id"],
                        "album_name": track["album"]["name"],
                        "year": track["album"]["release_date"].split("-")[0],
                        "album_artists": album_artists,
                        "album_art_640": album_art_640,
                        "album_art_300": album_art_300,
                        "album_art_64": album_art_64,
                        "album_length": track["album"]["total_tracks"],
                        "album_type": track["album"]["album_type"],
                    }
                ]
            return Response(  # TODO: replace with FastAPI
                json.dumps({"tracks": tracks}, indent=4),
                headers={"Content-Type": "application/json"},
                status=200,
            )
        if mode == "artist":
            artists = []
            for artist in response["artists"]["items"]:
                artist_art_640 = ""
                artist_art_300 = ""
                artist_art_64 = ""
                for image in artist["images"]:
                    if image["height"] == 640:
                        artist_art_640 = image["url"]
                    elif image["height"] == 300:
                        artist_art_300 = image["url"]
                    elif image["height"] == 64:
                        artist_art_64 = image["url"]
                artists += [
                    {
                        "artist_id": artist["id"],
                        "artist_name": artist["name"]
                        .split("(")[0]
                        .strip()
                        .split("-")[0]
                        .strip(),
                        "artist_popularity": artist["popularity"],
                        "artist_art_640": artist_art_640,
                        "artist_art_300": artist_art_300,
                        "artist_art_64": artist_art_64,
                    }
                ]
            return Response(  # TODO: replace with FastAPI
                json.dumps({"artists": artists}, indent=4),
                headers={"Content-Type": "application/json"},
                status=200,
            )

        return Response("bad request", status=400)  # TODO: replace with FastAPI
