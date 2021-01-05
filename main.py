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
    return returnResponse("harmonoid")


@app.get("/search")
async def searchYoutube(keyword, mode="album"):
    result = await harmonoidService.searchYoutube(keyword, mode)
    return returnResponse(result)


@app.get("/albumInfo")
async def albumInfo(albumId):
    result = await harmonoidService.albumInfo(albumId)
    return returnResponse(result)


@app.get("/trackInfo")
async def trackInfo(trackId, albumId=None):
    result = await harmonoidService.trackInfo(trackId, albumId)
    return returnResponse(result)


@app.get("/artistInfo")
async def artistInfo(artistId):
    result = await harmonoidService.artistInfo(artistId)
    return returnResponse(result)


@app.get("/artistTracks")
async def artistTracks(artistId):
    result = await harmonoidService.artistTracks(artistId)
    return returnResponse(result)


@app.get("/artistinfo")
async def artistInfo(artistId):
    result = await harmonoidService.artistInfo(artistId)
    return returnResponse(result)


@app.get("/lyrics")
async def getLyrics(trackId, trackName=None):
    if not any((trackId, trackName)):
        raise HTTPException(422, "Neither trackId nor trackName is specified")
    if trackId and trackName:
        raise HTTPException(422, "Both trackId and trackName is specified")
    result = await harmonoidService.getLyrics(trackId, trackName)
    return result


@app.get("/trackDownload")
async def trackDownload(trackId=None, albumId=None, trackName=None):
    if not any((trackId, trackName)):
        raise HTTPException(422, "Neither trackId nor trackName is specified")
    if trackId and trackName:
        raise HTTPException(422, "Both trackId and trackName is specified")
    return await harmonoidService.trackDownload(trackId, albumId, trackName)


@app.get("/test")
async def test():
    startTime = time.time()
    startLt = time.ctime(startTime)
    print("[test] Testing /search&mode=track")
    try:
        response = await searchYoutube("NoCopyrightSounds", "track")
        response = jsonable_encoder(response)
        responseCode = response["status_code"]
        print(f"[test] Status code: {responseCode}")
        tracks = json.loads(response["body"])["tracks"]
        if len(tracks) != 0 and tracks[0]["albumId"]:
            trackSearchTest = True
        else:
            trackSearchTest = False
    except Exception as e:
        trackSearchTest = False
        print(f"[test] Exception: {e}")

    print("[test] Testing /search&mode=album")
    try:
        response = await searchYoutube("NoCopyrightSounds", "album")
        response = jsonable_encoder(response)
        responseCode = response["status_code"]
        print(f"[test] Status code: {responseCode}")
        albums = json.loads(response["body"])["albums"]
        if len(albums) != 0 and albums[0]["albumId"]:
            albumSearchTest = True
        else:
            albumSearchTest = False
    except Exception as e:
        albumSearchTest = False
        print(f"[test] Exception: {e}")
    print("[test] Testing /search&mode=artist")
    try:
        response = await searchYoutube("NoCopyrightSounds", "artist")
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
    print("[test] Testing /trackDownload")
    try:
        response = await harmonoidService.trackDownload("JTjmZZ1W2ew", None, None)
        statusCode = response.status_code
    except Exception as e:
        statusCode = 500
        print(f"[test] Exception: {e}")
    print(f"[test] Status code: {statusCode}")
    if statusCode != 200:
        trackDownloadTest = False
    else:
        trackDownloadTest = True
    if all([trackSearchTest, albumSearchTest, artistSearchTest, trackDownloadTest]):
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
        "albumSearch": albumSearchTest,
        "artistSearch": artistSearchTest,
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
