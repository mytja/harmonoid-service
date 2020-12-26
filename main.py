from harmonoidservice import HarmonoidService
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import PlainTextResponse
from fastapi.encoders import jsonable_encoder
import json
import time

harmonoidService = HarmonoidService()

app = FastAPI()


def ReturnResponse(response):
    if type(response) == dict:
        return Response(json.dumps(response, indent=4), media_type="application/json")
    if type(response) == str:
        return PlainTextResponse(response)
    return response


@app.get("/")
async def hello():
    return ReturnResponse("service is running")


@app.get("/search")
async def SearchYoutube(keyword, mode="album"):
    result = await harmonoidService.SearchYoutube(keyword, mode)
    return ReturnResponse(result)


@app.get("/albuminfo")
async def AlbumInfo(album_id):
    result = await harmonoidService.AlbumInfo(album_id)
    return ReturnResponse(result)


@app.get("/trackinfo")
async def TrackInfo(track_id, album_id=None):
    result = await harmonoidService.TrackInfo(track_id, album_id)
    return ReturnResponse(result)


@app.get("/artistalbums")
async def ArtistAlbums(artist_id):
    result = await harmonoidService.ArtistAlbums(artist_id)
    return ReturnResponse(result)


@app.get("/artisttracks")
async def ArtistTracks(artist_id):
    result = await harmonoidService.ArtistTracks(artist_id)
    return ReturnResponse(result)


@app.get("/artistinfo")
async def ArtistAlbums(artist_id):
    result = await harmonoidService.ArtistInfo(artist_id)
    return ReturnResponse(result)


@app.get("/trackdownload")
async def TrackDownload(track_id=None, album_id=None, track_name=None):
    if not any((track_id, track_name)):
        raise HTTPException(422, "Neither track_id nor track_name is specified")
    if track_id and track_name:
        raise HTTPException(422, "Both track_id and track_name is specified")
    return await harmonoidService.TrackDownload(track_id, album_id, track_name)


@app.get("/test")
async def Test():
    __start_time = time.time()
    __start_lt = time.ctime(__start_time)

    print("[test-troubleshooting] Testing searching (track)")
    try:
        response = await SearchYoutube("NCS", "track")
        response = jsonable_encoder(response)
        rcode = response["status_code"]
        print("[test-troubleshooting] Status code: " + str(rcode))

        tracks = json.loads(response["body"])["tracks"]
        if len(tracks) != 0 and tracks[0]["album_id"]:
            __musicsearchtest = True
        else:
            __musicsearchtest = False
    except Exception as e:
        __musicsearchtest = False
        print("[test-troubleshooting] Exception: " + str(e))

    print("[test-troubleshooting] Testing searching (album)")
    try:
        response = await SearchYoutube("NCS", "album")
        response = jsonable_encoder(response)
        rcode = response["status_code"]
        print("[test-troubleshooting] Status code: " + str(rcode))

        albums = json.loads(response["body"])["albums"]
        if len(albums) != 0 and albums[0]["album_id"]:
            __albumsearchtest = True
        else:
            __albumsearchtest = False
    except Exception as e:
        __albumsearchtest = False
        print("[test-troubleshooting] Exception: " + str(e))

    print("[test-troubleshooting] Testing searching (artist)")
    try:
        response = await SearchYoutube("NCS", "artist")
        response = jsonable_encoder(response)
        rcode = response["status_code"]
        print("[test-troubleshooting] Status code: " + str(rcode))

        artists = json.loads(response["body"])["artists"]
        if len(artists) != 0 and artists[0]["artist_id"]:
            __artistsearchtest = True
        else:
            __artistsearchtest = False
    except Exception as e:
        __artistsearchtest = False
        print("[test-troubleshooting] Exception: " + str(e))

    print("[test-troubleshooting] Testing downloading")
    try:
        response = await harmonoidService.TrackDownload(
            "JTjmZZ1W2ew", None, None
        )  # NCS
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        print("[test-troubleshooting] Exception: " + str(e))

    print("[test-troubleshooting] Status code: " + str(status_code))
    if status_code != 200:
        __tdtest = False
    else:
        __tdtest = True

    if all([__artistsearchtest, __musicsearchtest, __albumsearchtest, __tdtest]):
        __testfail = False
    else:
        __testfail = True

    __timesec = time.time()
    __lt = time.ctime(__timesec)

    __time = __timesec - __start_time

    __json = {
        "endtime": __lt,
        "starttime": __start_lt,
        "time": __time,
        "fail": __testfail,
        "tracksearch": __musicsearchtest,
        "albumsearch": __albumsearchtest,
        "artistsearch": __artistsearchtest,
        "trackdownload": __tdtest,
    }

    return ReturnResponse(__json)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
