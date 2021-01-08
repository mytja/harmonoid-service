import asyncio
import json


class BrowsingHandler:
    async def TrackInfo(self, trackId, albumId):
        try:  # TODO: improve try/except
            track = await self.ytMusic.getSong(trackId)
            track_artists = [a for a in track["artists"]]
            if not albumId:
                albumId = await self.ytMusic.searchYoutube(
                    " ".join(track_artists) + " " + track["title"], "songs"
                )
                albumId = albumId[0]["album"]["id"]
            album = await self.ytMusic.getAlbum(albumId)
            trackNumber = 1

            album_art_64, album_art_300, album_art_640 = SortThumbnails(
                album["thumbnails"]
            )

            for albumTrack in album["tracks"]:
                if albumTrack["title"] == track["title"]:
                    trackNumber = int(albumTrack["index"])
                    break
                    
            try:
                lengthSeconds = int(track["lengthSeconds"]) * 1000
            except:
                lengthSeconds = 0

            album_artists = [a["name"] for a in album["artist"]]
            return {
                "track_id": track["videoId"],
                "track_name": track["title"],
                "track_artists": track_artists,
                "track_number": trackNumber,
                "track_duration": lengthSeconds,
                "album_art_640": album_art_640,
                "album_art_300": album_art_300,
                "album_art_64": album_art_64,
                "album_id": albumId,
                "album_name": album["title"],
                "year": track["release"].split("-")[0] if "release" in track else "",
                "album_artists": album_artists,
                "album_length": int(album["trackCount"]),
                "album_type": "single" if len(album["tracks"]) == 1 else "album",
                "url": track["url"],
            }
        except:
            return "Internal Server Error.\nytmusicapi Failed.\nERROR: This error has no explaination at the moment & restarting dynos is a possible fix."

    async def AlbumInfo(self, albumId):
        response = await self.ytMusic.getAlbum(albumId)

        tracks = response["tracks"]

        videoIdList = await self.AsyncAlbumSearch(tracks)
        
        try:
            lengthSeconds = int(track["lengthMs"])
        except:
            lengthSeconds = 0

        result = []
        for index, track in enumerate(tracks):
            result += [
                {
                    "track_id": videoIdList[index],
                    "track_name": track["title"],
                    "track_artists": [track["artists"]],
                    "track_number": int(track["index"]),
                    "track_duration": lengthSeconds,
                }
            ]

        return {"tracks": result}

    async def ArtistAlbums(self, artistId):
        artistJson = await self.ytMusic.getArtist(artistId)

        albums = artistJson["albums"]["results"] + artistJson["singles"]["results"]

        albumLengthList = await self.AsyncAlbumLength(albums)

        artistAlbums = []
        for index, album in enumerate(albums):
            album_art_64, album_art_300, album_art_640 = SortThumbnails(
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
                    "album_length": albumLengthList[index],
                    "album_type": "single" if albumLengthList[index] == 1 else "album",
                }
            ]
        return {"albums": artistAlbums}

    async def ArtistTracks(self, artistId):
        artistJson = await self.ytMusic.getArtist(artistId)

        tracks = artistJson["songs"]["results"]

        trackStuffList, trackDurationList = await asyncio.gather(
            self.AsyncTrackStuff(tracks),
            self.AsyncTrackDuration(tracks),
        )

        artistTracks = []
        for index, track in enumerate(tracks):
            track_artists = [a["name"] for a in track["artists"]]
            album_art_64, album_art_300, album_art_640 = SortThumbnails(
                track["thumbnails"]
            )
            artistTracks += [
                {
                    "track_id": track["videoId"],
                    "track_name": track["title"],
                    "track_artists": track_artists,
                    "track_number": trackStuffList[index][0],
                    "track_duration": trackDurationList[index],
                    "album_art_640": album_art_640,
                    "album_art_300": album_art_300,
                    "album_art_64": album_art_64,
                    "album_id": track["album"]["id"],
                    "album_name": track["album"]["name"],
                    "year": trackStuffList[index][1],
                    "album_artists": trackStuffList[index][2],
                    "album_length": trackStuffList[index][3],
                    "album_type": trackStuffList[index][4],
                }
            ]
        return {"tracks": artistTracks}

    async def ArtistInfo(self, artistId):
        artistJson = await self.ytMusic.getArtist(artistId)
        return {
            "description": artistJson["description"],
            "subscribers": artistJson["subscribers"],
            "views": artistJson["views"],
        }

    async def SearchYoutube(self, keyword, mode):
        if mode == "album":
            youtubeResult = await self.ytMusic.searchYoutube(keyword, "albums")

            albumLengthList = await self.AsyncAlbumLength(youtubeResult)

            albums = []
            for index, album in enumerate(youtubeResult):
                album_art_64, album_art_300, album_art_640 = SortThumbnails(
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
                        "album_length": albumLengthList[index],
                        "album_type": "single"
                        if albumLengthList[index] == 1
                        else "album",
                    }
                ]
            return json.dumps({"albums": albums}, indent=4)

        if mode == "track":
            youtubeResult = await self.ytMusic.searchYoutube(keyword, "songs")

            trackStuffList = await self.AsyncTrackStuff(youtubeResult)

            tracks = []
            for index, track in enumerate(youtubeResult):
                album_art_64, album_art_300, album_art_640 = SortThumbnails(
                    track["thumbnails"]
                )
                track_artists = [a["name"] for a in track["artists"]]
                tracks += [
                    {
                        "track_id": track["videoId"],
                        "track_name": track["title"],
                        "track_artists": track_artists,
                        "track_number": trackStuffList[index][0],
                        "track_duration": (
                            int(track["duration"].split(":")[0]) * 60
                            + int(track["duration"].split(":")[1])
                        )
                        * 1000,
                        "album_id": track["album"]["id"],
                        "album_name": track["album"]["name"],
                        "year": trackStuffList[index][1],
                        "album_artists": trackStuffList[index][2],
                        "album_art_640": album_art_640,
                        "album_art_300": album_art_300,
                        "album_art_64": album_art_64,
                        "album_length": trackStuffList[index][3],
                        "album_type": trackStuffList[index][4],
                    }
                ]
            return json.dumps({"tracks": tracks}, indent=4)

        if mode == "artist":
            youtubeResult = await self.ytMusic.searchYoutube(keyword, "artists")

            artists = []
            for artist in youtubeResult:
                artist_art_64, artist_art_300, artist_art_640 = SortThumbnails(
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
            return json.dumps({"artists": artists}, indent=4)

    # 🎉 Other Functions For YouTube Music
    async def ArrangeVideoIds(self, track):
        title = track["artists"] + " " + track["title"]
        youtubeResult = await self.ytMusic.searchYoutube(title, "songs")
        if track["title"] in youtubeResult[0]["title"]:
            return youtubeResult[0]["videoId"]
        else:
            return track["videoId"]

    async def AsyncAlbumSearch(self, tracks):
        tasks = [self.ArrangeVideoIds(track) for track in tracks]
        return await asyncio.gather(*tasks)

    async def ArrangeAlbumLength(self, album):
        youtubeResult = await self.ytMusic.getAlbum(album["browseId"])
        return int(youtubeResult["trackCount"])

    async def AsyncAlbumLength(self, albums):
        tasks = [self.ArrangeAlbumLength(album) for album in albums]
        return await asyncio.gather(*tasks)

    async def ArrangeTrackDuration(self, track):
        trackInfo = await self.ytMusic.getSong(track["videoId"])
        return int(trackInfo["lengthSeconds"]) * 1000

    async def AsyncTrackDuration(self, tracks):
        tasks = [self.ArrangeTrackDuration(track) for track in tracks]
        return await asyncio.gather(*tasks)

    async def ArrangeTrackStuff(self, track):
        youtubeResult = await self.ytMusic.getAlbum(track["album"]["id"])
        for result_track in youtubeResult["tracks"]:
            if result_track["title"] == track["title"]:
                number = int(result_track["index"])
                break
        year = youtubeResult["releaseDate"]["year"]
        artists = [a["name"] for a in youtubeResult["artist"]]
        length = int(youtubeResult["trackCount"])
        type = "single" if len(youtubeResult["tracks"]) == 1 else "album"

        return (number, year, artists, length, type)

    async def AsyncTrackStuff(self, tracks):
        tasks = [self.ArrangeTrackStuff(track) for track in tracks]
        return await asyncio.gather(*tasks)


def SortThumbnails(thumbnails):
    thumbs = {}
    for thumbnail in thumbnails:
        wh = thumbnail["width"] * thumbnail["height"]
        thumbs[wh] = thumbnail["url"]
    resolutions = sorted(list(thumbs.keys()))
    max = resolutions[-1]
    mid = resolutions[-2] if len(resolutions) > 2 else max
    min = resolutions[0]

    return (thumbs[min], thumbs[mid], thumbs[max])
