from harmonoidservice import HarmonoidService
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import PlainTextResponse
import json

harmonoidService = HarmonoidService()

app = FastAPI()


def ReturnResponse(response):
    if type(response) == dict:
        return Response(json.dumps(response, indent=4), media_type="application/json")
    if type(response) == str:
        return PlainTextResponse(response)


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


@app.get("/trackdownload")
async def TrackDownload(track_id=None, album_id=None, track_name=None):
    if not any((track_id, track_name)):
        raise HTTPException(422, "Neither track_id nor track_name is specified")
    if track_id and track_name:
        raise HTTPException(422, "Both track_id and track_name is specified")
    return await harmonoidService.TrackDownload(track_id, album_id, track_name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app")
