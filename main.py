from harmonoidservice import HarmonoidService
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import PlainTextResponse
import json

import logging


logging.basicConfig(level=logging.INFO)

harmonoidService = HarmonoidService()

app = FastAPI()


def dict_to_response(dict):
    return Response(json.dumps(dict, indent=4), media_type="application/json")


@app.get("/")
async def hello():
    return PlainTextResponse("service is running")


@app.get("/search")
async def SearchYoutube(keyword, mode="album"):
    result = await harmonoidService.SearchYoutube(keyword, mode)
    return dict_to_response(result)


@app.get("/albuminfo")
async def AlbumInfo(album_id):
    result = await harmonoidService.AlbumInfo(album_id)
    return dict_to_response(result)


@app.get("/trackinfo")
async def TrackInfo(track_id, album_id):
    result = await harmonoidService.TrackInfo(track_id, album_id)
    return dict_to_response(result)


@app.get("/artistalbums")
async def ArtistAlbums(artist_id):
    result = await harmonoidService.ArtistAlbums(artist_id)
    return dict_to_response(result)


@app.get("/artisttracks")
async def ArtistTracks(artist_id):
    result = await harmonoidService.ArtistTracks(artist_id)
    return dict_to_response(result)


@app.get("/trackdownload")
async def TrackDownload(track_id=None, album_id=None, track_name=None):
    if not any((track_id, track_name)):
        raise HTTPException(422, "Neither track_id nor track_name is specified")
    if not any((track_id, album_id)):
        raise HTTPException(422, "track_id nor album_id both should be specified")
    if track_id and track_name:
        raise HTTPException(422, "Both track_id and track_name is specified")
    return await harmonoidService.TrackDownload(track_id, album_id, track_name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
