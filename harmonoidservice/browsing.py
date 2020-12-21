import asyncio
import itertools


class BrowsingHandler:
    async def TrackInfo(self, trackId, albumId):
        try:
            track = await self.ytMusic._get_song(trackId)
            track_artists = [a for a in track["artists"]]
            if not albumId:
                albumId = await self.ytMusic._search(
                    " ".join(track_artists) + " " + track["title"], "songs"
                )
                albumId = albumId[0]["album"]["id"]
            album = await self.ytMusic._get_album(albumId)
            trackNumber = 1

            album_art_64, album_art_300, album_art_640 = SortThumbnails(
                album["thumbnails"]
            )

            for albumTrack in album["tracks"]:
                if albumTrack["title"] == track["title"]:
                    trackNumber = int(albumTrack["index"])
                    break
            album_artists = [a["name"] for a in album["artist"]]
            return {
                "track_id": track["videoId"],
                "track_name": track["title"],
                "track_artists": track_artists,
                "track_number": trackNumber,
                "track_duration": int(track["lengthSeconds"]) * 1000,
                "album_art_640": album_art_640,
                "album_art_300": album_art_300,
                "album_art_64": album_art_64,
                "album_id": albumId,
                "album_name": album["title"],
                "year": track["release"].split("-")[0] if "release" in track else "",
                "album_artists": album_artists,
                "album_length": int(album["trackCount"]),
                "album_type": "single" if len(album["tracks"]) == 1 else "album",
            }
        except:
            return "Internal Server Error.\nytmusicapi Failed.\nERROR: This error has no explaination at the moment & restarting dynos is a possible fix."

    async def AlbumInfo(self, albumId):
        response = await self.ytMusic._get_album(albumId)

        tracks = response["tracks"]

        videoIdList = ["" for index in range(len(tracks))]
        searchQueriesList = [
            track["title"] + " " + track["artists"] for track in tracks
        ]
        await self.AsyncAlbumSearch(searchQueriesList, videoIdList)

        result = [{
                    "track_id": videoIdList[index],
                    "track_name": track["title"],
                    "track_artists": [track["artists"]],
                    "track_number": int(track["index"]),
                    "track_duration": int(track["lengthMs"]),
                } for index, track in enumerate(tracks)]
        return {"tracks": result}

    async def ArtistAlbums(self, artistId):
        artistJson = await self.ytMusic._get_artist(artistId)

        albums = artistJson["albums"]["results"] + artistJson["singles"]["results"]

        albumIdList = [album["browseId"] for album in albums]
        albumLengthList = ["" for album in albums]
        await self.AsyncAlbumLength(albumIdList, albumLengthList)

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
        artistJson = await self.ytMusic._get_artist(artistId)

        tracks = artistJson["songs"]["results"]

        trackTitleList = [track["title"] for track in tracks]
        albumIdList = [track["album"]["id"] for track in tracks]
        trackNumberList = ["" for track in tracks]
        yearList = ["" for track in tracks]
        albumLengthList = ["" for track in tracks]
        albumTypeList = ["" for track in tracks]
        trackIdList = [track["videoId"] for track in tracks]
        trackDurationList = ["" for track in tracks]
        await asyncio.gather(
            self.AsyncTrackStuff(
                trackTitleList,
                albumIdList,
                trackNumberList,
                yearList,
                albumLengthList,
                albumTypeList,
            ),
            self.AsyncTrackDuration(trackIdList, trackDurationList),
        )

        artistTracks = []
        for index, track in enumerate(tracks):
            track_artists = [a["name"] for a in track["artists"]]
            album_artists = track_artists  # UNDEFINED so we use track_artists
            album_art_64, album_art_300, album_art_640 = SortThumbnails(
                track["thumbnails"]
            )
            artistTracks += [
                {
                    "track_id": track["videoId"],
                    "track_name": track["title"],
                    "track_artists": track_artists,
                    "track_number": trackNumberList[index],
                    "track_duration": trackDurationList[index],
                    "album_art_640": album_art_640,
                    "album_art_300": album_art_300,
                    "album_art_64": album_art_64,
                    "album_id": track["album"]["id"],
                    "album_name": track["album"]["name"],
                    "year": yearList[index],
                    "album_artists": album_artists,
                    "album_length": albumLengthList[index],
                    "album_type": albumTypeList[index],
                }
            ]
        return {"albums": artistTracks}

    async def SearchYoutube(self, keyword, mode):
        if mode == "album":
            youtubeResult = await self.ytMusic._search(keyword, "albums")

            albumIdList = [album["browseId"] for album in youtubeResult]
            albumLengthList = ["" for album in youtubeResult]
            await self.AsyncAlbumLength(albumIdList, albumLengthList)

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
            return {"albums": albums}

        if mode == "track":
            youtubeResult = await self.ytMusic._search(keyword, "songs")

            trackTitleList = [track["title"] for track in youtubeResult]
            albumIdList = [track["album"]["id"] for track in youtubeResult]
            trackNumberList = ["" for track in youtubeResult]
            yearList = ["" for track in youtubeResult]
            albumLengthList = ["" for track in youtubeResult]
            albumTypeList = ["" for track in youtubeResult]
            await self.AsyncTrackStuff(
                trackTitleList,
                albumIdList,
                trackNumberList,
                yearList,
                albumLengthList,
                albumTypeList,
            )

            tracks = []
            for index, track in enumerate(youtubeResult):
                album_art_64, album_art_300, album_art_640 = SortThumbnails(
                    track["thumbnails"]
                )
                track_artists = [a["name"] for a in track["artists"]]
                album_artists = track_artists
                tracks += [
                    {
                        "track_id": track["videoId"],
                        "track_name": track["title"],
                        "track_artists": track_artists,
                        "track_number": trackNumberList[index],
                        "track_duration": (
                            int(track["duration"].split(":")[0]) * 60
                            + int(track["duration"].split(":")[1])
                        )
                        * 1000,
                        "album_id": track["album"]["id"],
                        "album_name": track["album"]["name"],
                        "year": yearList[index],
                        "album_artists": album_artists,
                        "album_art_640": album_art_640,
                        "album_art_300": album_art_300,
                        "album_art_64": album_art_64,
                        "album_length": albumLengthList[index],
                        "album_type": albumTypeList[index],
                    }
                ]
            return {"tracks": tracks}

        if mode == "artist":
            youtubeResult = await self.ytMusic._search(keyword, "artists")

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
            return {"artists": artists}

    async def ArrangeVideoIds(self, searchQueriesList, videoIdList, videoIdListIndex):
        youtubeResult = await self.ytMusic._search(
            searchQueriesList[videoIdListIndex], "songs"
        )
        videoIdList[videoIdListIndex] = youtubeResult[0]["videoId"]

    async def AsyncAlbumSearch(self, searchQueriesList, videoIdList):
        args = [
            (searchQueriesList, videoIdList, index)
            for index in range(len(videoIdList))
        ]

        asyncSearchTasks = itertools.starmap(self.ArrangeVideoIds, args)
        await asyncio.gather(*asyncSearchTasks)

    async def ArrangeAlbumLength(
        self, albumIdList, albumLengthList, albumLengthListIndex
    ):
        youtubeResult = await self.ytMusic._get_album(albumIdList[albumLengthListIndex])
        albumLengthList[albumLengthListIndex] = int(youtubeResult["trackCount"])

    async def AsyncAlbumLength(self, albumIdList, albumLengthList):
        args = [
            (albumIdList, albumLengthList, index)
            for index in range(len(albumIdList))
        ]

        asyncSearchTasks = itertools.starmap(self.ArrangeAlbumLength, args)
        await asyncio.gather(*asyncSearchTasks)

    async def ArrangeTrackDuration(
        self, trackIdList, trackDurationList, trackDurationListIndex
    ):
        trackInfo = await self.ytMusic._get_song(trackIdList[trackDurationListIndex])
        trackDurationList[trackDurationListIndex] = (
            int(trackInfo["lengthSeconds"]) * 1000
        )

    async def AsyncTrackDuration(self, trackIdList, trackDurationList):
        args = [
            (trackIdList, trackDurationList, index)
            for index in range(len(trackIdList))
        ]

        asyncSearchTasks = itertools.starmap(self.ArrangeTrackDuration, args)
        await asyncio.gather(*asyncSearchTasks)

    async def ArrangeTrackStuff(
        self,
        trackTitleList,
        albumIdList,
        trackNumberList,
        yearList,
        albumLengthList,
        albumTypeList,
        albumLengthListIndex,
    ):
        youtubeResult = await self.ytMusic._get_album(albumIdList[albumLengthListIndex])
        for track in youtubeResult["tracks"]:
            if track["title"] == trackTitleList[albumLengthListIndex]:
                trackNumberList[albumLengthListIndex] = int(track["index"])
                break
        yearList[albumLengthListIndex] = youtubeResult["releaseDate"]["year"]
        albumLengthList[albumLengthListIndex] = int(youtubeResult["trackCount"])
        albumTypeList[albumLengthListIndex] = (
            "single" if len(youtubeResult["tracks"]) == 1 else "album"
        )

    async def AsyncTrackStuff(
        self,
        trackTitleList,
        albumIdList,
        trackNumberList,
        yearList,
        albumLengthList,
        albumTypeList,
    ):
        args = [(
                trackTitleList,
                albumIdList,
                trackNumberList,
                yearList,
                albumLengthList,
                albumTypeList,
                index,
            ) for index in range(len(albumIdList))]
        asyncSearchTasks = itertools.starmap(self.ArrangeTrackStuff, args)
        await asyncio.gather(*asyncSearchTasks)


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
