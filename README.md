# harmonoid-service

#### An asynchronous FastAPI app for searching & downloading music from [YouTube Music](https://music.youtube.com).

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

##### This is used in the 🎵 [Harmonoid](https://github.com/alexmercerind/harmonoid) music app.

This repository has everything ready to be deployed on [Heroku](https://heroku.com) or on a Linux VM.

## ❔ What does this app do?

This app is a simple backend that can be used to browse & download music from [YouTube Music](https://music.youtube.com) using [youtube-dl](https://github.com/ytdl-org/youtube-dl) & [ytmusicapi](https://github.com/sigma67/ytmusicapi). The tracks you get in download, are MP3 in format with exact metadata.

This uses [mutagen](https://github.com/quodlibet/mutagen) for adding metadata & album art to the tracks.

You can use this in your music app if you want.

**This project is strictly intended for personal & non-commercial usage only. The project does not support piracy. Buy artists' music to support them.**

###### 🎶 A track downloaded using this app

![A track downloaded](/downloaded_track.PNG)

## 🔧 Setting Up

### Heroku

**1) Create a new personal app at Heroku**

Let's assume that, you created an app with name 'yourapp' for the rest of process.

**2) Clone this repository and enter it**

```bash
git clone https://github.com/raitonoberu/harmonoid-service --depth=1

cd harmonoid-service
```

**3) Add remote to Heroku**

```bash
git remote add heroku https://git.heroku.com/yourapp.git
```

**4) Add buildpacks to the app**

```bash
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

heroku buildpacks:add heroku/python
```

You can add buildpacks directly from the settings page of your app if you don't want to install & use the heroku CLI.

**5) Push changes to heroku**

```bash
git push heroku master
```

**6) Verify that you did everything correct**

- Now, if you visit your app at https://yourapp.herokuapp.com/ in a browser, you will see 'service is running' on your screen, with a status code of 200.
- Visit test suite at https://yourapp.herokuapp.com/test in a browser! If you see something like this:
```
{
    "endtime": "Fri Dec 18 07:31:29 2020",
    "fail": true,
    "tracksearch": true,
    "albumsearch": true,
    "artistsearch": true,
    "trackdownload": false
}
```
If ```fail``` is true, then a component failed to do its job correctly, in this case ```trackdownload``` 

### On Linux VM / Cloud Service

**1) Clone this repository**

In terminal / bash in your home directory (```cd ~```), type in ```git clone https://github.com/raitonoberu/harmonoid-service```

**2) Open folder**

Open your newly created foler with ```cd harmonoid-service```

**3) Run a script included with this repository**

Run ```sudo source setupvm``` on Ubuntu, on Debian ```sudo ./setupvm```

You can also try command without ```sudo```

## 📐 Usage

**This is a generic web app, so you can use something like [urllib](https://docs.python.org/3/library/urllib.html) or [requests](https://github.com/psf/requests) to access it.**

I'll be using requests for the examples below.

##### Searching For Music

```python
import requests

response = requests.get(
    'https://yourapp.herokuapp.com/search', {
        'keyword': 'Tobu Sunburst',                    #Keyword for searching
        'mode': 'album',                               #Your mode for searching. Valid modes are 'album', 'track', & 'artist'
        'offset': '0',                                 #Search offset
        'limit': '50',                                 #Limiting the amount of results
    }
)

print(response.json())
```

##### Get Tracks Of An Album

```python
import requests

response = requests.get(
    'https://yourapp.herokuapp.com/albuminfo', {
        'album_id': 'MPREb_PvefrisSxRq',                #Album ID of the track
    }
)

print(response.json())
```

##### Get Information About A Track

```python
import requests

response = requests.get(
    'https://yourapp.herokuapp.com/trackinfo', {
        'track_id': '9j81j90jkKU',                      #Track ID of the track
        'album_id': 'MPREb_PvefrisSxRq',                #Album ID of the track
    }
)

print(response.json())
```

##### Get Albums Of An Artist

```python
import requests

response = requests.get(
    'https://yourapp.herokuapp.com/artistalbums', {
        'artist_id': 'UCh6GMTlXgeHnwDHaIQ_ThAA',        #Artist ID of the artist
    }
)

print(response.json())
```

##### Get Tracks Of An Artist

```python
import requests

response = requests.get(
    'https://yourapp.herokuapp.com/artisttracks', {
        'artist_id': 'UCh6GMTlXgeHnwDHaIQ_ThAA',        #Artist ID of the artist
    }
)

print(response.json())
```

##### Download A Track

```python
import requests

audioResponse = requests.get(
    'https://yourapp.herokuapp.com/trackdownload', {
        'track_id': '9j81j90jkKU',                     #Track ID of the track
    }
)
if (audioResponse.status_code == 200):
    audioTrackBinary = audioResponse.content
    audioTrackFile = open('download.m4a', 'wb')
    audioTrackFile.write(audioTrackBinary)
    audioTrackFile.close()
    print('Download Successful!')
else:
    print('Download Failed!')
```

**NOTE**: If something goes wrong during the runtime of the app, like [youtube-dl](https://github.com/ytdl-org/youtube-dl) stops working or your server's IP gets blocked with 429 status codes from Google, you'll recieve status code 500 from this app.
In that case you can simply re-push the code to the Heroku by making an empty commit. It will automatically update the dependencies at heroku and everything should be fixed.

## 💌 Big Thanks To These People And Organizations

- **Heroku**

  - Thanks for providing a free place to deploy this web app.

- [sigmatics](https://github.com/sigma67) for [ytmusicapi](https://github.com/sigma67/ytmusicapi)
- [Sebastián Ramírez](https://github.com/tiangolo) for [fastapi](https://github.com/tiangolo/fastapi)
- [youtube-dl](https://github.com/ytdl-org) for [youtube-dl](https://github.com/ytdl-org/youtube-dl)
- [Quod Libet](https://github.com/quodlibet) for [mutagen](https://github.com/quodlibet/mutagen)
- [Encode](https://github.com/encode) for [httpx](https://github.com/encode/httpx)
- [Tin Tvrtković](https://github.com/Tinche) for [aiofiles](https://github.com/Tinche/aiofiles)
