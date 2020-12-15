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
    
    response = SearchYoutube("NCS", "track")
    if (response != None):
        __musicsearchtest = "OK!"
    else:
        __musicsearchtest = "Fail!"
    
    response = SearchYoutube("NCS", "album")
    if (response != None):
        __albumsearchtest = "OK!"
    else:
        __albumsearchtest = "Fail!"
    
    response = SearchYoutube("NCS", "artist")
    if (response != None):
        __artistsearchtest = "OK!"
    else:
        __artistsearchtest = "Fail!"
        
    response = await TrackDownload(track_name="NCS")
    if (response != None or response.find("500") == -1):
        __tdtest = "OK!"
    else:
        __tdtest = "Fail!"
        
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
