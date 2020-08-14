from youtubesearchpython import SearchVideos
import youtube_dl
import json
from urllib.request import urlopen
from urllib.request import Request
import os
from flask import make_response, Response


class YoutubeHandler:

    def AudioUrl(self, videoId):
        import youtube_dl
        ydl_opts = {
            'format': 'bestaudio/best',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f'https://www.youtube.com/watch?v={videoId}', download=False)
            return info['formats'][0]['url']

    def SearchYoutube(self, keyword, offset, mode, maxResults):
        if keyword != None:
            search = SearchVideos(keyword, offset, mode, maxResults)
            return Response(search.result(), headers = {'Content-Type' : 'application/json'}, status = 200)
        else:
            return make_response('bad request', 400)

    def TrackDownload(self, trackId, trackName):

        if trackId != None:
            try:
                trackInfo = self.TrackInfo(trackId).json        
                artists = ''
                for artist in trackInfo['album_artists']:
                    artists+=artist.split('(')[0].strip().split('-')[0].strip()+' '

                videoId = self.SearchYoutube('lyrics ' + trackInfo['track_name'].split('(')[0].strip().split('-')[0].strip() + ' ' + artists, 1, 'json', 1).json['search_result'][0]['id']
                audioUrl = self.AudioUrl(videoId)

                audioRequest = Request(
                    url = audioUrl,
                    data = None
                )
                audioResponse = urlopen(audioRequest)
                audioBytes = audioResponse.read()
                response = make_response(audioBytes, 200)
                response.headers.set('Content-Type', 'audio/mp4')
                response.headers.set('Content-Length', audioResponse.headers['Content-Length'])

                return response
            except:
                return make_response('error', 500)
        
        elif trackName != None:
            try:
                videoId = self.SearchYoutube(trackName, 1, 'json', 1).json['search_result'][0]['id']
                audioUrl = self.AudioUrl(videoId)

                audioRequest = Request(
                    url = audioUrl,
                    data = None
                )
                audioResponse = urlopen(audioRequest)
                audioBytes = audioResponse.read()
                response = make_response(audioBytes, 200)
                response.headers.set('Content-Type', 'audio/mp4')

                return response
            except:
                return make_response('error', 500)
        else:
            return make_response('bad request', 400)