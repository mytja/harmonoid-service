from fastapi import HTTPException
import asyncio
import logging

logger = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(self, message):
        self.message = message


class BrowsingHandler:
    async def TrackInfo(self, trackId):
        track = await self.ytMusic._get_song(trackId)

        album_art_64, album_art_300, album_art_640 = sort_thumbnails(
            track["thumbnail"]["thumbnails"]
        )

        track_artists = track.get("artists", [track["author"]])
        album_artists = track_artists  # UNDEFINED so we use track_artists
        return {
            "track_id": track["videoId"],
            "track_name": track["title"],
            "track_artists": track_artists,
            # "track_number": 1,  # UNDEFINED
            "track_duration": int(track["lengthSeconds"]) * 1000,
            "album_art_640": album_art_640,
            "album_art_300": album_art_300,
            "album_art_64": album_art_64,
            # "album_id": "",  # UNDEFINED
            # "album_name": "",  # UNDEFINED
            "year": track["release"].split("-")[0] if "release" in track else "",
            "album_artists": album_artists,
            # "album_length": 1,  # UNDEFINED
            # "album_type": "album",  # UNDEFINED
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
                    "track_number": int(track["index"]),
                    "track_duration": int(track["lengthMs"]),
                }
            ]
        return {"tracks": result}

    async def ArtistAlbums(self, artistId):
        # обьединить с singles
        artistJson = await self.ytMusic._get_artist(artistId)

        artistAlbums = []
        for album in artistJson["albums"]["results"]:
            album_art_64, album_art_300, album_art_640 = sort_thumbnails(
                album["thumbnails"]
            )
            artistAlbums += [
                {
                    "album_id": album["browseId"],
                    "album_name": album["title"],
                    "year": album["year"],
                    "album_artists": [artistJson["name"]],
                    "album_art_640": album_art_640,
                    "album_art_300": album_art_300,
                    "album_art_64": album_art_64,
                    # "album_length": 1,  # UNDEFINED
                    # "album_type": "album",  # UNDEFINED
                }
            ]
        return {"albums": artistAlbums}

    async def ArtistTracks(self, artistId):
        artistJson = await self.ytMusic._get_artist(artistId)

        artistTracks = []
        for track in artistJson["songs"]["results"]:
            track_artists = [a["name"] for a in track["artists"]]
            album_artists = track_artists  # UNDEFINED so we use track_artists
            album_art_64, album_art_300, album_art_640 = sort_thumbnails(
                track["thumbnails"]
            )
            artistTracks += [
                {
                    "track_id": track["videoId"],
                    "track_name": track["title"],
                    "track_artists": track_artists,
                    # "track_number": 1,  # UNDEFINED
                    # "track_duration": 1,  # UNDEFINED
                    "album_art_640": album_art_640,
                    "album_art_300": album_art_300,
                    "album_art_64": album_art_64,
                    "album_id": track["album"]["id"],
                    "album_name": track["album"]["name"],
                    # "year": "0000",  # UNDEFINED
                    "album_artists": album_artists,
                    # "album_length": 1,  # UNDEFINED
                    # "album_type": "album",  # UNDEFINED
                }
            ]
        return {"albums": artistTracks}

    async def SearchYoutube(self, keyword, mode):
        if mode == "album":
            youtubeResult = await self.ytMusic._search(keyword, "albums")

            albums = []
            for album in youtubeResult:
                album_art_64, album_art_300, album_art_640 = sort_thumbnails(
                    album["thumbnails"]
                )
                albums += [
                    {
                        "album_id": album["browseId"],
                        "album_name": album["title"],
                        "year": album["year"],
                        "album_artists": [album["artist"]],
                        "album_art_640": album_art_640,
                        "album_art_300": album_art_300,
                        "album_art_64": album_art_64,
                        # "album_length": 1,  # UNDEFINED
                        "album_type": album["type"].lower(),
                    }
                ]
            return {"albums": albums}

        if mode == "track":
            youtubeResult = await self.ytMusic._search(keyword, "songs")

            tracks = []
            for track in youtubeResult:
                album_art_64, album_art_300, album_art_640 = sort_thumbnails(
                    track["thumbnails"]
                )
                track_artists = [a["name"] for a in track["artists"]]
                album_artists = track_artists  # UNDEFINED so we use track_artists
                tracks += [
                    {
                        "track_id": track["videoId"],
                        "track_name": track["title"],
                        "track_artists": track_artists,
                        # "track_number": 1, # UNDEFINED
                        "track_duration": (
                            int(track["duration"].split(":")[0]) * 60
                            + int(track["duration"].split(":")[1])
                        )
                        * 1000,
                        "album_id": track["album"]["id"],
                        "album_name": track["album"]["name"],
                        # "album_year": "", # UNDEFINED
                        "album_artists": album_artists,
                        "album_art_640": album_art_640,
                        "album_art_300": album_art_300,
                        "album_art_64": album_art_64,
                        # "album_length": 11, # UNDEFINED
                        # "album_type": "album" # UNDEFINED
                    }
                ]
            return {"tracks": tracks}

        if mode == "artist":
            youtubeResult = await self.ytMusic._search(keyword, "artists")

            artists = []
            for artist in youtubeResult:
                album_art_64, album_art_300, album_art_640 = sort_thumbnails(
                    artist["thumbnails"]
                )
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


def sort_thumbnails(thumbnails):
    thumbs = {}
    for thumbnail in thumbnails:
        wh = thumbnail["width"] * thumbnail["height"]
        thumbs[wh] = thumbnail["url"]
    resolutions = sorted(list(thumbs.keys()))
    max = resolutions[-1]
    mid = resolutions[-2] if len(resolutions) > 2 else max
    min = resolutions[0]

    return (thumbs[min], thumbs[mid], thumbs[max])
