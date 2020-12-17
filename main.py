from harmonoidservice import HarmonoidService
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import PlainTextResponse
import httpx
import json
import types

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
    import time
    
    response = await SearchYoutube("NCS", "track")
    while response != types.CoroutineType):
        response = json.dumps(response, indent=4)
        ifin =  "track_id" in response
    if (response != None and ifin==True):
        __musicsearchtest = "OK!"
    else:
        __musicsearchtest = "Fail!"
    
    try:
        response = SearchYoutube("NCS", "album")
        response = json.dumps(response, indent=4)
        ifin =  "album_id" in response
        if (response != None and ifin==True):
            __albumsearchtest = "OK!"
        else:
            __albumsearchtest = "Fail!"
    except:
        __albumsearchtest = "Fail!"
    
    try:
        response = SearchYoutube("NCS", "artist")
        response = json.dumps(response, indent=4)
        ifin =  "artist_id" in response
        if (response != None and ifin==True):
            __artistsearchtest = "OK!"
        else:
            __artistsearchtest = "Fail!"
    except:
        __artistsearchtest = "Fail!"
       
    try:
        response = harmonoidService.TrackDownload(track_id, album_id, track_name)
        status_code = response.status_code
    except:
        status_code = 500
    if status_code != 200:
        __tdtest = "Fail!"
    else:
        __tdtest = "OK!"
        
    if (__artistsearchtest=="Fail!" or __musicsearchtest=="Fail!" or __albumsearchtest=="Fail!" or __tdtest=="Fail!"):
        __testfail = True
    else:
        __testfail = False
    
    __timesec = time.time()
    __lt = time.ctime(__timesec)
    
    __json = {
        "endtime": __lt,
        "fail": __testfail,
        "tracksearch": __musicsearchtest,
        "albumsearch": __albumsearchtest,
        "artistsearch": __artistsearchtest,
        "trackdownload": __tdtest
    }
    
    return ReturnResponse(__json)
    


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
