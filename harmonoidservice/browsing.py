import asyncio


class BrowsingHandler:
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
        if track["album"] != None:
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
    
    async def trackInfo(self, trackId, albumId):
        if trackId and albumId:
            """
            Making simultaneous request if both albumId & trackId are present.
            """
            track, album = await asyncio.gather(self.ytMusic.getSong(trackId), self.ytMusic.getAlbum(albumId))
        else:
            track = await self.ytMusic.getSong(trackId)
            """
            Searching for track & fetching albumId if it is None.
            """
            albumId = await self.ytMusic.searchYoutube(
                " ".join([artist for artist in track["artists"]]) + " " + track["title"], "songs"
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
            "track_id": track["videoId"],
            "track_name": track["title"],
            "track_artists": [artist for artist in track["artists"]],
            "track_number": trackNumber,
            "track_duration": int(track["lengthSeconds"]) if track["lengthSeconds"] else 0,
            "album_art_640": albumArtHigh,
            "album_art_300": albumArtMedium,
            "album_art_64": albumArtLow,
            "album_id": albumId,
            "album_name": album["title"],
            "year": album["releaseDate"]["year"],
            "album_artists": albumArtistName[0],
            "album_length": int(album["trackCount"]),
            "album_type": "single" if len(album["tracks"]) == 1 else "album",
            "url": track["url"],
        }

    async def albumInfo(self, albumId):
        response = await self.ytMusic.getAlbum(albumId)
        tracks = response["tracks"]
        """
        For replacing video IDs of music videos with video IDs of tracks.
        """
        videoIdList = await self.asyncAlbumSearch(tracks)
        result = []
        for index, track in enumerate(tracks):
            result += [
                {
                    "track_id": videoIdList[index],
                    "track_name": track["title"],
                    "track_artists": [track["artists"]],
                    "track_number": int(track["index"]),
                    "track_duration": int(track["lengthMs"]) // 1000 if track["lengthMs"] else 0,
                }
            ]
        return {"tracks": result}

    async def artistAlbums(self, artistId):
        artistJson = await self.ytMusic.getArtist(artistId)
        albums = artistJson["albums"]["results"] + artistJson["singles"]["results"]
        artistAlbums = []
        for index, album in enumerate(albums):
            albumArtLow, albumArtMedium, albumArtHigh = self.sortThumbnails(
                album["thumbnails"]
            )
            
            albumLengthList = await self.AsyncAlbumLength(albums)
            
            artistAlbums += [
                {
                    "album_id": album["browseId"],
                    "album_name": album["title"],
                    "year": album["year"],
                    "album_artists": [artistJson["name"]][0],
                    "album_art_640": albumArtHigh,
                    "album_art_300": albumArtMedium,
                    "album_art_64": albumArtLow,
                    "album_length": albumLengthList[index],
                    "album_type": "single" if albumLengthList[index] == 1 else "album",
                }
            ]
        return {"albums": artistAlbums}

    async def artistTracks(self, artistId):
        artistJson = await self.ytMusic.getArtist(artistId)
        tracks = artistJson["songs"]["results"]
        artistTracks = []
        for index, track in enumerate(tracks):
            trackArtistNames = [a["name"] for a in track["artists"]]
            albumArtLow, albumArtMedium, albumArtHigh = self.sortThumbnails(
                track["thumbnails"]
            )
            trackStuffList, trackDurationList = await asyncio.gather(
                self.AsyncTrackStuff(tracks),
                self.AsyncTrackDuration(tracks),
            )
            artistTracks += [
                {
                    "track_id": track["videoId"],
                    "track_name": track["title"],
                    "track_artists": trackArtistNames,
                    "album_art_640": albumArtHigh,
                    "album_art_300": albumArtMedium,
                    "album_art_64": albumArtLow,
                    "album_id": track["album"]["id"],
                    "album_name": track["album"]["name"],
                    "year": trackStuffList[index][1],
                    "album_artists": trackStuffList[index][2],
                    "album_length": trackStuffList[index][3],
                    "album_type": trackStuffList[index][4],
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
            albumLengthList = await self.AsyncAlbumLength(youtubeResult)
            albums = []
            for index, album in enumerate(youtubeResult):
                albumArtLow, albumArtMedium, albumArtHigh = self.sortThumbnails(
                    album["thumbnails"]
                )
                albums += [
                    {
                        "album_id": album["browseId"],
                        "album_name": album["title"],
                        "year": int(album["year"]) if album["year"].isnumeric() else 0,
                        "album_artists": album["artist"],
                        "album_art_640": albumArtHigh,
                        "album_art_300": albumArtMedium,
                        "album_art_64": albumArtLow,
                        "album_length": albumLengthList[index],
                        "album_type": "single"
                        if albumLengthList[index] == 1
                        else "album",
                    }
                ]
            return {"albums": albums}

        if mode == "track":
            youtubeResult = await self.ytMusic.searchYoutube(keyword, "songs")
            trackStuffList = await self.AsyncTrackStuff(youtubeResult)
            tracks = []
            for index, track in enumerate(youtubeResult):
                if track["album"] != None:
                    albumArtLow, albumArtMedium, albumArtHigh = self.sortThumbnails(
                        track["thumbnails"]
                    )
                    trackArtistNames = [a["name"] for a in track["artists"]]
                    tracks += [
                        {
                            "track_id": track["videoId"],
                            "track_name": track["title"],
                            "track_artists": trackArtistNames,
                            "track_duration": (
                                int(track["duration"].split(":")[0]) * 60
                                + int(track["duration"].split(":")[-1])
                            ),
                            "album_id": track["album"]["id"],
                            "album_name": track["album"]["name"],
                            "year": trackStuffList[index][1],
                            "album_artists": trackStuffList[index][2],
                            "album_art_640": albumArtHigh,
                            "album_art_300": albumArtMedium,
                            "album_art_64": albumArtLow,
                            "album_length": trackStuffList[index][3],
                            "album_type": trackStuffList[index][4],
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
                        "album_art_640": albumArtHigh,
                        "album_art_300": albumArtMedium,
                        "album_art_64": albumArtLow,
                    }
                ]
            return {"artists": artists}

    async def getLyrics(self, trackId, trackName):
        if not trackId:
            trackId = await self.searchYoutube(trackName, "songs")[0]["videoId"]
        watchPlaylist = await self.ytMusic.getWatchPlaylist(trackId)
        watchPlaylistId = watchPlaylist["lyrics"]
        return await self.ytMusic.getLyrics(watchPlaylistId)
    
