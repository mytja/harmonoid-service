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
        if len(tracks) != 0 and tracks[0]["trackId"]:
            trackSearchTest = True
        else:
            trackSearchTest = False
    except Exception as e:
        trackSearchTest = False
        print(f"[test] Exception: {e}")

    print("[test] Testing /trackInfo")
    try:
        response = await trackInfo(tracks[0]["trackId"])
        response = jsonable_encoder(response)
        responseCode = response["status_code"]
        print(f"[test] Status code: {responseCode}")
        tracks = json.loads(response["body"])
        if len(tracks) != 0 and tracks["trackId"]:
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
        if len(albums) != 0 and albums[0]["albumId"]:
            albumSearchTest = True
        else:
            albumSearchTest = False
    except Exception as e:
        albumSearchTest = False
        print(f"[test] Exception: {e}")

    print("[test] Testing /albumInfo")
    try:
        response = await albumInfo(albums[0]["albumId"])
        response = jsonable_encoder(response)
        responseCode = response["status_code"]
        print(f"[test] Status code: {responseCode}")
        albums = json.loads(response["body"])
        if len(albums) != 0 and (albums["tracks"][0]["trackId"]):
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
        
    print("[test] Testing /lyrics")
    try:
        response = await getLyrics(lyricsTrackId, None)
        response = jsonable_encoder(response)
        try:
            responseCode = response["status_code"]
            print(f"[test] Status code: {responseCode}")
        except Exception as e:
            print("[test] Exception: No status code!")
            print(f"[test] Exception: Details: {e}")
        lyrics = json.loads(response["body"])
        if len(lyrics) != 0 and lyrics["lyrics"]:
            lyricsSearchTest = True
        else:
            lyricsSearchTest = False
    except Exception as e:
        lyricsSearchTest = False
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
    
    if all([trackSearchTest, trackInfoTest, albumSearchTest, albumInfoTest, artistSearchTest, artistInfoTest, lyricsSearchTest, trackDownloadTest]):
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
        "lyricsSearch": lyricsSearchTest,
        "trackDownload": trackDownloadTest,
    }
    return returnResponse(response)


if __name__ == "__main__":
    import bjoern

    bjoern.run(app, "0.0.0.0", 8000)

    
"""
- Class methods names are lower camel case.
- Class names are upper camel case.
- Constants are upper snake case.
- Class attributes are lower camel case.
- Other identifiers & object names are lower camel case.
- Only private methods have two underscores in their name.
"""
