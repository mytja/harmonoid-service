from harmonoidservice import HarmonoidService
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import PlainTextResponse
from fastapi.encoders import jsonable_encoder
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
    
    __start_time = time.time()
    __start_lt = time.ctime(__start_time)
    
    response = await SearchYoutube("NCS", "track")
    response = jsonable_encoder(response)
    rcode = response["status_code"]
    print("[test-troubleshooting] Status code: "+str(rcode))
    response = response["body"]
    
    try:
        ifin =  "track_id" in response
        if (response != None and ifin==True and int(rcode) == 200):
            __musicsearchtest = True
        else:
            __musicsearchtest = False
    except:
        print("[test-troubleshooting] Type is not dict")
    
    response = await SearchYoutube("NCS", "album")
    response = jsonable_encoder(response)
    rcode = response["status_code"]
    print("[test-troubleshooting] Status code: "+str(rcode))
    response = response["body"]
    
    try:
        ifin =  "album_id" in response
        if (response != None and ifin==True and int(rcode) == 200):
            __albumsearchtest = True
        else:
            __albumsearchtest = False
    except:
        print("[test-troubleshooting] Type is not dict")
    
    response = await SearchYoutube("NCS", "artist")
    response = jsonable_encoder(response)
    rcode = response["status_code"]
    print("[test-troubleshooting] Status code: "+str(rcode))
    response = response["body"]
    
    try:
        ifin =  "artist_id" in response
        if (response != None and ifin==True and int(rcode) == 200):
            __artistsearchtest = True
        else:
            __artistsearchtest = False
    except:
        print("[test-troubleshooting] Type is not dict")
       
    try:
        response = await harmonoidService.TrackDownload(track_id, album_id, track_name)
        #print("[test-troubleshooting]: "+str(response)) File can't convert to string!
        
    except:
        status_code = 500
    try:
        status_code = response.status_code
        print(status_code)
    except:
        status_code = 200
    if status_code != 200:
        __tdtest = False
    else:
        __tdtest = True
        
    if (__artistsearchtest==False or __musicsearchtest==False or __albumsearchtest==False or __tdtest==False):
        __testfail = True
    else:
        __testfail = False
    
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
        "trackdownload": __tdtest
    }
    
    return ReturnResponse(__json)
    


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
