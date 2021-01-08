from harmonoidservice import HarmonoidService
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import PlainTextResponse
from fastapi.encoders import jsonable_encoder
import json
import time

harmonoidService = HarmonoidService()

app = FastAPI()


@app.on_event("startup")
async def startupEvent():
    """
    Prefetching player JavaScript
    """
    await harmonoidService.ytMusic.youtube.getJS()


def returnResponse(response):
    if type(response) is dict:
        return Response(json.dumps(response, indent=4), media_type="application/json")
    if type(response) is str:
        return PlainTextResponse(response)
    return response


@app.get("/")
async def hello():
    return returnResponse("service is running")


@app.get("/search")
async def searchYoutube(keyword, mode="album"):
    result = await harmonoidService.SearchYoutube(keyword, mode)
    return returnResponse(result)


@app.get("/albuminfo")
async def albumInfo(album_id):
    result = await harmonoidService.AlbumInfo(album_id)
    return returnResponse(result)


@app.get("/trackinfo")
async def trackInfo(track_id, album_id=None):
    result = await harmonoidService.TrackInfo(track_id, album_id)
    return returnResponse(result)


@app.get("/artistinfo")
async def artistInfo(artist_id):
    result = await harmonoidService.ArtistInfo(artist_id)
    return returnResponse(result)


@app.get("/artisttracks")
async def artistTracks(artist_id):
    result = await harmonoidService.ArtistTracks(artist_id)
    return returnResponse(result)


@app.get("/trackdownload")
async def trackDownload(track_id=None, album_id=None, track_name=None):
    if not any((track_id, track_name)):
        raise HTTPException(422, "Neither trackId nor trackName is specified")
    if track_id and track_name:
        raise HTTPException(422, "Both trackId and trackName is specified")
    return await harmonoidService.trackDownload(track_id, album_id, track_name)


@app.get("/test")
async def test(trackName="NoCopyrightedSounds", albumName="NoCopyrightedSounds", artistName="NoCopyrightedSounds", trackDownloadName="NoCopyrightedSounds", lyricsTrackId="Kx7B-XvmFtE"):
    startTime = time.time()
    startLt = time.ctime(startTime)
    print("[test] Testing /search&mode=track")
    try:
        response = await searchYoutube(trackName, "track")
        response = jsonable_encoder(response)
        responseCode = response["status_code"]
        print(f"[test] Status code: {responseCode}")
        tracks = json.loads(response["body"])["tracks"]
        if len(tracks) != 0 and tracks[0]["track_id"]:
            trackSearchTest = True
        else:
            trackSearchTest = False
    except Exception as e:
        trackSearchTest = False
        print(f"[test] Exception: {e}")

    print("[test] Testing /trackInfo")
    try:
        response = await trackInfo(tracks[0]["track_id"])
        response = jsonable_encoder(response)
        responseCode = response["status_code"]
        print(f"[test] Status code: {responseCode}")
        tracks = json.loads(response["body"])
        if len(tracks) != 0 and tracks["track_id"]:
            trackInfoTest = True
        else:
            trackInfoTest = False
    except Exception as e:
        trackInfoTest = False
        print(f"[test] Exception: {e}")

    print("[test] Testing /search&mode=album")
    try:
        response = await searchYoutube(albumName, "album")
        response = jsonable_encoder(response)
        responseCode = response["status_code"]
        print(f"[test] Status code: {responseCode}")
        albums = json.loads(response["body"])["albums"]
        if len(albums) != 0 and albums[0]["album_id"]:
            albumSearchTest = True
        else:
            albumSearchTest = False
    except Exception as e:
        albumSearchTest = False
        print(f"[test] Exception: {e}")

    print("[test] Testing /albumInfo")
    try:
        response = await albumInfo(albums[0]["album_id"])
        response = jsonable_encoder(response)
        responseCode = response["status_code"]
        print(f"[test] Status code: {responseCode}")
        albums = json.loads(response["body"])
        if len(albums) != 0 and (albums["tracks"][0]["track_id"]):
            albumInfoTest = True
        else:
            albumInfoTest = False
    except Exception as e:
        albumInfoTest = False
        print(f"[test] Exception: {e}")
    
    print("[test] Testing /search&mode=artist")
    try:
        response = await searchYoutube(artistName, "artist")
        response = jsonable_encoder(response)
        responseCode = response["status_code"]
        print(f"[test] Status code: {responseCode}")
        artists = json.loads(response["body"])["artists"]
        if len(artists) != 0 and artists[0]["artist_id"]:
            artistSearchTest = True
        else:
            artistSearchTest = False
    except Exception as e:
        artistSearchTest = False
        print(f"[test] Exception: {e}")

    print("[test] Testing /artistInfo")
    try:
        response = await artistInfo(artists[0]["artist_id"])
        response = jsonable_encoder(response)
        responseCode = response["status_code"]
        print(f"[test] Status code: {responseCode}")
        artists = json.loads(response["body"])
        if len(artists) != 0 and artists["description"]:
            artistInfoTest = True
        else:
            artistInfoTest = False
    except Exception as e:
        trackInfoTest = False
        print(f"[test] Exception: {e}")
    
    print("[test] Testing /trackDownload")
    try:
        response = await harmonoidService.trackDownload(None, None, trackDownloadName)
        statusCode = response.status_code
    except Exception as e:
        statusCode = 500
        print(f"[test] Exception: {e}")
    print(f"[test] Status code: {statusCode}")
    if statusCode != 200:
        trackDownloadTest = False
    else:
        trackDownloadTest = True
    
    if all([trackSearchTest, trackInfoTest, albumSearchTest, albumInfoTest, artistSearchTest, artistInfoTest, trackDownloadTest]):
        testSuccess = True
    else:
        testSuccess = False
    
    endTime = time.time()
    endLt = time.ctime(endTime)
    totalTime = endTime - startTime
    response = {
        "endTime": endLt,
        "startTime": startLt,
        "time": totalTime,
        "success": testSuccess,
        "trackSearch": trackSearchTest,
        "trackInfo": trackInfoTest,
        "albumSearch": albumSearchTest,
        "alubmInfo": albumInfoTest,
        "artistSearch": artistSearchTest,
        "artistInfo": artistInfoTest,
        "trackDownload": trackDownloadTest,
    }
    return returnResponse(response)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app")

    
"""
- Class methods names are lower camel case.
- Class names are upper camel case.
- Constants are upper snake case.
- Class attributes are lower camel case.
- Other identifiers & object names are lower camel case.
- Only private methods have two underscores in their name.
"""
