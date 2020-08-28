from harmonoidservice import HarmonoidService
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import PlainTextResponse
from os import getenv
import json

import logging


logging.basicConfig(level=logging.INFO)

harmonoidService = HarmonoidService(
    getenv("SPOTIFY_CLIENT_ID"), getenv("SPOTIFY_CLIENT_SECRET")
)

app = FastAPI()


def dict_to_response(dict):
    return Response(json.dumps(dict, indent=4), media_type="application/json")


@app.get("/")
async def hello():
    return PlainTextResponse("service is running")


@app.get("/accesstoken")
async def accesstoken():
    token = await harmonoidService.AccessToken()
    return PlainTextResponse(token)


@app.get("/search")
async def SearchSpotify(keyword, mode="album", offset: int = 0, limit: int = 50):
    result = await harmonoidService.SearchSpotify(keyword, mode, offset, limit)
    return dict_to_response(result)


@app.get("/searchyoutube")
async def SearchYoutube(keyword, offset: int = 1, max_results: int = 10):
    result = await harmonoidService.SearchYoutube(keyword, offset, max_results)
    return dict_to_response(result)


@app.get("/albuminfo")
async def AlbumInfo(album_id):
    result = await harmonoidService.AlbumInfo(album_id)
    return dict_to_response(result)


@app.get("/trackinfo")
async def TrackInfo(track_id):
    result = await harmonoidService.TrackInfo(track_id)
    return dict_to_response(result)


@app.get("/artistrelated")
async def ArtistRelated(artist_id):
    result = await harmonoidService.ArtistRelated(artist_id)
    return dict_to_response(result)


@app.get("/artistalbums")
async def ArtistAlbums(artist_id):
    result = await harmonoidService.ArtistAlbums(artist_id)
    return dict_to_response(result)


@app.get("/artisttracks")
async def ArtistTracks(artist_id, country="us"):
    result = await harmonoidService.ArtistTracks(artist_id, country)
    return dict_to_response(result)


@app.get("/trackdownload")
async def TrackDownload(track_id=None, track_name=None):
    if not any((track_id, track_name)):
        raise HTTPException(422, "Neither track_id nor track_name is specified")
    if track_id and track_name:
        raise HTTPException(422, "Both track_id and track_name is specified")
    return await harmonoidService.TrackDownload(track_id, track_name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
