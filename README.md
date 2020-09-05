# spotiyt-server


#### An asynchronous FastAPI app for searching music in Spotify & downloading music from YouTube.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

##### This is used in the 🎵 [Harmonoid](https://github.com/alexmercerind/harmonoid) music app.


This repository has everything ready to be deployed on [Heroku](https://heroku.com).

## ❔ What does this app do?

This app is a wrapper around the already publicly available Spotify Web API, to search for various tracks, albums & artists on Spotify & download music from YouTube using [youtube-dl](https://github.com/ytdl-org/youtube-dl) & [youtube-search-python](https://github.com/alexmercerind/youtube-search-python). The tracks you get in download, are M4A in format with exact metadata fetched from Spotify.

This uses [mutagen](https://github.com/quodlibet/mutagen) for adding metadata & album art to the tracks.

You can use this in your music app if you want.

**This project is strictly intended for personal & non-commercial usage only. The project does not support piracy. Buy artists' music to support them.**

###### 🎶 A track downloaded using this app

![A track downloaded](/downloaded_track.PNG)


## 🛠 Setting Up


**1) Create a new personal app at Heroku**

Let's assume that, you created an app with name 'yourapp' for the rest of process.


**2) Setup environment variables at your Heroku app**

You need to set the two following environment variables in your Heroku app:

- **SPOTIFY_CLIENT_ID**
  - Your client ID from Spotify.
- **SPOTIFY_CLIENT_SECRET**
  - Your client secret from Spotify.

And, if you're new into this... You can get them [here](https://developer.spotify.com/documentation/general/guides/app-settings/) from Spotify.

**3) Clone this repository and enter it**

```bash
git clone https://github.com/raitonoberu/spotiyt-server --depth=1

cd harmonoid-service
```

**4) Push changes to Heroku**

```bash
git remote add heroku https://git.heroku.com/yourapp.git

git push heroku master
```

**5) Verify that you did everything correct**

Now, if you visit your app at https://yourapp.herokuapp.com/ in a browser, you will see 'service is running' on your screen, with a status code of 200.


## 📐 Usage


**This is a generic web app, so you can use something like [urllib](https://docs.python.org/3/library/urllib.html) or [requests](https://github.com/psf/requests) to access it.**

I'll be using requests for the examples below.

##### Searching For Music

```python
import requests

response = requests.get(
    'https://yourapp.herokuapp.com/search', {
        'keyword': 'fade alan walker',        #Keyword for searching
        'mode': 'album',                      #Your mode for searching. Valid modes are 'album', 'track', & 'artist'
        'offset': '0',                        #Search offset
        'limit': '50',                        #Limiting the amount of results
    }
)

print(response.json())
```

##### Get Tracks Of An Album

```python
import requests

response = requests.get(
    'https://yourapp.herokuapp.com/albuminfo', {
        'album_id': '5HMjpBO0v78ayq5lreAyDd',        #Spotify Album ID of the track
    }
)

print(response.json())
```

##### Get Information About A Track

```python
import requests

response = requests.get(
    'https://yourapp.herokuapp.com/trackinfo', {
        'track_id': '0HmONWWIU1FXkwWLDpqrjl',        #Spotify Track ID of the track
    }
)

print(response.json())
```

##### Get Albums Of An Artist

```python
import requests

response = requests.get(
    'https://yourapp.herokuapp.com/artistalbums', {
        'artist_id': '7vk5e3vY1uw9plTHJAMwjN',        #Spotify Artist ID of the artist
    }
)

print(response.json())
```

##### Get Tracks Of An Artist

```python
import requests

response = requests.get(
    'https://yourapp.herokuapp.com/artisttracks', {
        'artist_id': '7vk5e3vY1uw9plTHJAMwjN',        #Spotify Artist ID of the artist
    }
)

print(response.json())
```

##### Download A Track

```python
import requests

audioResponse = requests.get(
    'https://yourapp.herokuapp.com/trackdownload', {
        'track_id': '0HmONWWIU1FXkwWLDpqrjl',        #Spotify Track ID of the track
    }
)
if (audioResponse.status_code == 200):
    audioTrackBinary = audioResponse.content
    audioTrackFile = open('download.m4a', 'wb')
    audioTrackFile.write(audioTrackBinary)
    audioTrackFile.close()
    print('Download Successful!')
else:
    print('Download Unsuccessful!')
```

**NOTE**: If something goes wrong during the runtime of the app, like [youtube-dl](https://github.com/ytdl-org/youtube-dl) or [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) stop working or your server's IP gets blocked with 429 status codes from Google, you'll recieve status code 500 from this app.
In that case you can simply re-push the code to the Heroku by making an empty commit. It will automatically update the dependencies at heroku and everything should be fixed.


## ❤ Big Thanks To These People And Organizations

- **Spotify**
  - Thanks a lot for publicly giving your API to developers. It is really helpful for everyone who wants to develop something music related.

- **Heroku**
  - Thanks for providing a free place to deploy this web app.


- [Sebastián Ramírez](https://github.com/tiangolo) for [fastapi](https://github.com/tiangolo/fastapi)
- [youtube-dl](https://github.com/ytdl-org) for [youtube-dl](https://github.com/ytdl-org/youtube-dl)
- [Hitesh Kumar Saini](https://github.com/alexmercerind) for [youtube-search-python](https://github.com/alexmercerind/youtube-search-python)
- [Quod Libet](https://github.com/quodlibet) for [mutagen](https://github.com/quodlibet/mutagen)
- [Encode](https://github.com/encode) for [httpx](https://github.com/encode/httpx)
- [Tin Tvrtković](https://github.com/Tinche) for [aiofiles](https://github.com/Tinche/aiofiles)
