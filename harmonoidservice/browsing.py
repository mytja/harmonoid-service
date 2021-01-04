import asyncio
import json


class BrowsingHandlerInternal:
    async def arrangeVideoIds(self, track):
        title = track["artists"] + " " + track["title"]
        youtubeResult = await self.ytMusic.searchYoutube(title, "songs")
        if track["title"] in youtubeResult[0]["title"]:
            return youtubeResult[0]["videoId"]
        else:
            return track["videoId"]

    async def asyncAlbumSearch(self, tracks):
        tasks = [self.arrangeVideoIds(track) for track in tracks]
        return await asyncio.gather(*tasks)

    async def arrangeAlbumLength(self, album):
        youtubeResult = await self.ytMusic.getAlbum(album["browseId"])
        return int(youtubeResult["trackCount"])

    async def asyncAlbumLength(self, albums):
        tasks = [self.arrangeAlbumLength(album) for album in albums]
        return await asyncio.gather(*tasks)

    async def arrangeTrackDuration(self, track):
        trackInfo = await self.ytMusic.getSong(track["videoId"])
        return int(trackInfo["lengthSeconds"])

    async def asyncTrackDuration(self, tracks):
        tasks = [self.arrangeTrackDuration(track) for track in tracks]
        return await asyncio.gather(*tasks)

    async def arrangeTrackStuff(self, track):
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

    async def asyncTrackStuff(self, tracks):
        tasks = [self.arrangeTrackStuff(track) for track in tracks]
        return await asyncio.gather(*tasks)

    def sortThumbnails(self, thumbnails):
        thumbs = {}
        for thumbnail in thumbnails:
            wh = thumbnail["width"] * thumbnail["height"]
            thumbs[wh] = thumbnail["url"]
        resolutions = sorted(list(thumbs.keys()))
        max = resolutions[-1]
        mid = resolutions[-2] if len(resolutions) > 2 else max
        min = resolutions[0]

        return (thumbs[min], thumbs[mid], thumbs[max])


class BrowsingHandler(BrowsingHandlerInternal):
    async def trackInfo(self, trackId, albumId):
        track = await self.ytMusic.getSong(trackId)
        trackArtistNames = [a for a in track["artists"]]
        """
        Searching for track & fetching albumId if it is None.
        """
        if not albumId:
            albumId = await self.ytMusic.searchYoutube(
                " ".join(trackArtistNames) + " " + track["title"], "songs"
            )
            albumId = albumId[0]["album"]["id"]
        album = await self.ytMusic.getAlbum(albumId)
        trackNumber = 1

        albumArtLow, albumArtMedium, albumArtHigh = self.sortThumbnails(
            album["thumbnails"]
        )

        for albumTrack in album["tracks"]:
            if albumTrack["title"] == track["title"]:
                trackNumber = int(albumTrack["index"])
                break

        albumArtistName = [a["name"] for a in album["artist"]]
        return {
            "trackId": track["videoId"],
            "trackName": track["title"],
            "trackArtistNames": trackArtistNames,
            "trackNumber": trackNumber,
            "trackDuration": int(track["lengthSeconds"]),
            "albumArtHigh": albumArtHigh,
            "albumArtMedium": albumArtMedium,
            "albumArtLow": albumArtLow,
            "albumId": albumId,
            "albumName": album["title"],
            "year": track["release"].split("-")[0] if "release" in track else "",
            "albumArtistName": albumArtistName[0],
            "albumLength": int(album["trackCount"]),
            "albumType": "single" if len(album["tracks"]) == 1 else "album",
            "url": track["url"],
        }

    async def albumInfo(self, albumId):
        response = await self.ytMusic.getAlbum(albumId)

        tracks = response["tracks"]

        videoIdList = await self.asyncAlbumSearch(tracks)

        result = []
        for index, track in enumerate(tracks):
            result += [
                {
                    "trackId": videoIdList[index],
                    "trackName": track["title"],
                    "trackArtistNames": [track["artists"]],
                    "trackNumber": int(track["index"]),
                    "trackDuration": int(track["lengthMs"]),
                }
            ]

        return {"tracks": result}

    async def artistAlbums(self, artistId):
        artistJson = await self.ytMusic.getArtist(artistId)

        albums = artistJson["albums"]["results"] + artistJson["singles"]["results"]

        albumLengthList = await self.asyncAlbumLength(albums)

        artistAlbums = []
        for index, album in enumerate(albums):
            albumArtLow, albumArtMedium, albumArtHigh = self.sortThumbnails(
                album["thumbnails"]
            )
            artistAlbums += [
                {
                    "albumId": album["browseId"],
                    "albumName": album["title"],
                    "year": album["year"],
                    "albumArtistName": [artistJson["name"]][0],
                    "albumArtHigh": albumArtHigh,
                    "albumArtMedium": albumArtMedium,
                    "albumArtLow": albumArtLow,
                    "albumLength": albumLengthList[index],
                    "albumType": "single" if albumLengthList[index] == 1 else "album",
                }
            ]
        return {"albums": artistAlbums}

    async def artistTracks(self, artistId):
        artistJson = await self.ytMusic.getArtist(artistId)

        tracks = artistJson["songs"]["results"]

        trackStuffList, trackDurationList = await asyncio.gather(
            self.asyncTrackStuff(tracks),
            self.asyncTrackDuration(tracks),
        )

        artistTracks = []
        for index, track in enumerate(tracks):
            trackArtistNames = [a["name"] for a in track["artists"]]
            albumArtLow, albumArtMedium, albumArtHigh = self.sortThumbnails(
                track["thumbnails"]
            )
            artistTracks += [
                {
                    "trackId": track["videoId"],
                    "trackName": track["title"],
                    "trackArtistNames": trackArtistNames,
                    "trackNumber": trackStuffList[index][0],
                    "trackDuration": trackDurationList[index],
                    "albumArtHigh": albumArtHigh,
                    "albumArtMedium": albumArtMedium,
                    "albumArtLow": albumArtLow,
                    "albumId": track["album"]["id"],
                    "albumName": track["album"]["name"],
                    "year": trackStuffList[index][1],
                    "albumArtistName": trackStuffList[index][2][0],
                    "albumLength": trackStuffList[index][3],
                    "albumType": trackStuffList[index][4],
                }
            ]
        return {"tracks": artistTracks}

    async def artistInfo(self, artistId):
        artistJson = await self.ytMusic.getArtist(artistId)
        return {
            "description": artistJson["description"],
            "subscribers": artistJson["subscribers"],
            "views": artistJson["views"],
        }

    async def searchYoutube(self, keyword, mode):
        if mode == "album":
            youtubeResult = await self.ytMusic.searchYoutube(keyword, "albums")

            albumLengthList = await self.asyncAlbumLength(youtubeResult)

            albums = []
            for index, album in enumerate(youtubeResult):
                albumArtLow, albumArtMedium, albumArtHigh = self.sortThumbnails(
                    album["thumbnails"]
                )
                albums += [
                    {
                        "albumId": album["browseId"],
                        "albumName": album["title"],
                        "year": album["year"],
                        "albumArtistName": album["artist"],
                        "albumArtHigh": albumArtHigh,
                        "albumArtMedium": albumArtMedium,
                        "albumArtLow": albumArtLow,
                        "albumLength": albumLengthList[index],
                        "albumType": "single"
                        if albumLengthList[index] == 1
                        else "album",
                    }
                ]
            return {"albums": albums}

        if mode == "track":
            youtubeResult = await self.ytMusic.searchYoutube(keyword, "songs")

            trackStuffList = await self.asyncTrackStuff(youtubeResult)

            tracks = []
            for index, track in enumerate(youtubeResult):
                albumArtLow, albumArtMedium, albumArtHigh = self.sortThumbnails(
                    track["thumbnails"]
                )
                trackArtistNames = [a["name"] for a in track["artists"]]
                tracks += [
                    {
                        "trackId": track["videoId"],
                        "trackName": track["title"],
                        "trackArtistNames": trackArtistNames,
                        "trackNumber": trackStuffList[index][0],
                        "trackDuration": (
                            int(track["duration"].split(":")[0]) * 60
                            + int(track["duration"].split(":")[1])
                        ),
                        "albumId": track["album"]["id"],
                        "albumName": track["album"]["name"],
                        "year": trackStuffList[index][1],
                        "albumArtistName": trackStuffList[index][2][0],
                        "albumArtHigh": albumArtHigh,
                        "albumArtMedium": albumArtMedium,
                        "albumArtLow": albumArtLow,
                        "albumLength": trackStuffList[index][3],
                        "albumType": trackStuffList[index][4],
                    }
                ]
            return {"tracks": tracks}

        if mode == "artist":
            youtubeResult = await self.ytMusic.searchYoutube(keyword, "artists")

            artists = []
            for artist in youtubeResult:
                albumArtLow, albumArtMedium, albumArtHigh = self.sortThumbnails(
                    artist["thumbnails"]
                )
                artists += [
                    {
                        "artist_id": artist["browseId"],
                        "artist_name": artist["artist"],
                        "albumArtHigh": albumArtHigh,
                        "albumArtMedium": albumArtMedium,
                        "albumArtLow": albumArtLow,
                    }
                ]
            return {"artists": artists}

    async def getLyrics(self, trackId, trackName):
        if not trackId:
            trackId = await self.searchYoutube(trackName, "songs")[0]["videoId"]
        watchPlaylist = await self.ytMusic.getWatchPlaylist(trackId)
        watchPlaylistId = watchPlaylist["lyrics"]
        return await self.ytMusic.getLyrics(watchPlaylistId)
