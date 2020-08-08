import urllib.request
import urllib.parse
import base64
import json
from flask import Response
from urllib.request import Request


class SpotifyHandler:

    def AccessToken(self):
        encoded = base64.b64encode(bytes(self.clientId + ':' + self.clientSecret, encoding='utf_8')).decode('utf_8')
        parameters = urllib.parse.urlencode({'grant_type': 'client_credentials'}).encode()
        headers = {'Authorization': f'Basic {encoded}'}

        request = Request(
            url = 'https://accounts.spotify.com/api/token',
            data = parameters,
            headers = headers 
        )
        response = urllib.request.urlopen(request)
        return json.loads(response.read())['access_token']

    def TrackInfo(self, trackId):
        if trackId!=None:
            token = self.AccessToken()
            request = Request(
                url = f'https://api.spotify.com/v1/tracks/{trackId}',
                data = None,
                headers = {'Authorization': f'Bearer {token}'}
            )
            response = urllib.request.urlopen(request)
            track = json.loads(response.read())
            album_art_640 = ''
            album_art_300 = ''
            album_art_64 = ''
            for image in track['album']['images']:
                if image['height'] == 640:
                    album_art_640 = image['url']
                elif image['height'] == 300:
                    album_art_300 = image['url']
                elif image['height'] == 64:
                    album_art_64 = image['url']
            a_artists = track['album']['artists']
            album_artists = []
            for artist in a_artists:
                album_artists+=[artist['name']]
            t_artists = track['artists']
            track_artists = []
            for artist in t_artists:
                track_artists+=[artist['name']] 
            return Response(json.dumps({   
                'track_id': track['id'],
                'track_name': track['name'],
                'track_artists': track_artists,
                'track_number': track['track_number'],
                'track_duration': track['duration_ms'],
                'album_art_640': album_art_640,
                'album_art_300': album_art_300,
                'album_art_64': album_art_64,
                'album_id': track['album']['id'],
                'album_name': track['album']['name'],
                'year': track['album']['release_date'].split('-')[0],
                'album_artists': album_artists,
                'album_length': track['album']['total_tracks'],
                'album_type': track['album']['album_type']
            }, indent = 4), headers= {'Content-Type' : 'application/json'}, status=200)
        else:
            return Response('bad request', status=400)

    def AlbumInfo(self, albumId):
        if albumId!=None:
            token = self.AccessToken()
            query = urllib.parse.urlencode({'limit': 50, 'offset': 0})
            request = Request(
                url = f'https://api.spotify.com/v1/albums/{albumId}/tracks' + '?' + query,
                data = None,
                headers = {'Authorization': f'Bearer {token}'}
            )
            response = urllib.request.urlopen(request)
            tracks = json.loads(response.read())['items']
            result = []
            for track in tracks:
                t_artists = track['artists']
                track_artists = []
                for artist in t_artists:
                    track_artists+=[artist['name']]
                result+=[
                    {
                        'track_id': track['id'],
                        'track_name': track['name'],
                        'track_artists': track_artists,
                        'track_number': track['track_number'],
                        'track_duration': track['duration_ms'],
                    }
                ]
            return Response(json.dumps({'tracks': result}, indent=4), headers= {'Content-Type' : 'application/json'}, status=200)
        else:
            return Response('bad request', status=400)
        
    def ArtistRelated(self, artistId):
        if artistId != None:
            token = self.AccessToken()
            relatedArtists = []
            albums = []
            relatedArtistsRequest = Request(
                url = f'https://api.spotify.com/v1/artists/{artistId}/related-artists',
                data = None,
                headers = {'Authorization': f'Bearer {token}'}
            )
            relatedArtistsResponse = urllib.request.urlopen(relatedArtistsRequest)
            relatedArtistsJson = json.loads(relatedArtistsResponse.read())
            for artist in relatedArtistsJson['artists']:
                artist_art_640 = ''
                artist_art_300 = ''
                artist_art_64 = ''
                for image in artist['images']:
                    if image['height'] == 640:
                        artist_art_640 = image['url']
                    elif image['height'] == 300:
                        artist_art_300 = image['url']
                    elif image['height'] == 64:
                        artist_art_64 = image['url']
                relatedArtists+=[
                    {   
                        'artist_id': artist['id'],
                        'artist_name': artist['name'],
                        'artist_popularity': artist['popularity'],
                        'artist_art_640': artist_art_640,
                        'artist_art_300': artist_art_300,
                        'artist_art_64': artist_art_64,
                        }
                    ]
            return Response(json.dumps({'artists' : relatedArtists}, indent = 4), headers= {'Content-Type' : 'application/json'}, status=200)
        else:
            return Response('bad request', status=400)

    def ArtistAlbums(self, artistId):
        if artistId != None:
            token = self.AccessToken()
            artistAlbums = []
            albums = []
            relatedArtistsRequest = Request(
                url = f'https://api.spotify.com/v1/artists/{artistId}/albums',
                data = None,
                headers = {'Authorization': f'Bearer {token}'}
            )
            artistAlbumsResponse = urllib.request.urlopen(relatedArtistsRequest)
            artistAlbumsJson = json.loads(artistAlbumsResponse.read())
            for album in artistAlbumsJson['items']:
                album_art_640 = ''
                album_art_300 = ''
                album_art_64 = ''
                album_artists = []
                a_artists = album['artists']
                for artist in a_artists:
                    album_artists+=[artist['name']]
                for image in album['images']:
                    if image['height'] == 640:
                        album_art_640 = image['url']
                    elif image['height'] == 300:
                        album_art_300 = image['url']
                    elif image['height'] == 64:
                        album_art_64 = image['url']
                artistAlbums+=[
                    {   
                        'album_id': album['id'],
                        'album_name': album['name'],
                        'year': album['release_date'].split('-')[0],
                        'album_artists': album_artists,
                        'album_art_640': album_art_640,
                        'album_art_300': album_art_300,
                        'album_art_64': album_art_64,
                        'album_length': album['total_tracks'],
                        'album_type': album['album_type']
                        }
                    ]
            return Response(json.dumps({'albums' : artistAlbums}, indent = 4), headers= {'Content-Type' : 'application/json'}, status=200)
        else:
            return Response('bad request', status=400)

    def ArtistTracks(self, artistId):
        if artistId != None:
            token = self.AccessToken()
            artistTracks = []
            albums = []
            artistTracksRequest = Request(
                url = f'https://api.spotify.com/v1/artists/{artistId}/top-tracks?country=us',
                data = None,
                headers = {'Authorization': f'Bearer {token}'}
            )
            artistTracksResponse = urllib.request.urlopen(artistTracksRequest)
            artistTracksJson = json.loads(artistTracksResponse.read())
            for track in artistTracksJson['tracks']:
                album_art_640 = ''
                album_art_300 = ''
                album_art_64 = ''
                album_artists = []
                a_artists = track['artists']
                for artist in a_artists:
                    album_artists+=[artist['name']]
                t_artists = track['artists']
                track_artists = []
                for artist in t_artists:
                    track_artists+=[artist['name']]
                for image in track['album']['images']:
                    if image['height'] == 640:
                        album_art_640 = image['url']
                    elif image['height'] == 300:
                        album_art_300 = image['url']
                    elif image['height'] == 64:
                        album_art_64 = image['url']
                artistTracks+=[
                    {   
                        'track_id': track['id'],
                        'track_name': track['name'],
                        'track_artists': track_artists,
                        'track_number': track['track_number'],
                        'track_duration': track['duration_ms'],
                        'album_art_640': track['album']['images'][0]['url'],
                        'album_art_300': track['album']['images'][1]['url'],
                        'album_art_64': track['album']['images'][2]['url'],
                        'album_id': track['album']['id'],
                        'album_name': track['album']['name'],
                        'year': track['album']['release_date'].split('-')[0],
                        'album_artists': album_artists,
                        'album_length': track['album']['total_tracks'],
                        'album_type': track['album']['album_type']
                        }
                    ]
            return Response(json.dumps({'albums' : artistTracks}, indent = 4), headers= {'Content-Type' : 'application/json'}, status=200)
        else:
            return Response('bad request', status=400)

    def SearchSpotify(self, keyword, mode, offset, limit):
        if keyword!=None:
            token = self.AccessToken()
            query = urllib.parse.urlencode({'q': keyword, 'type': mode, 'limit': limit, 'offset': offset})
            request = Request(
                url = 'https://api.spotify.com/v1/search' + '?' + query,
                data = None,
                headers = {'Authorization': f'Bearer {token}'}
            )
            response = json.loads(urllib.request.urlopen(request).read())
            
            if mode == 'album':
                albums = []
                for album in response['albums']['items']:
                    album_art_640 = ''
                    album_art_300 = ''
                    album_art_64 = ''
                    for image in album['images']:
                        if image['height'] == 640:
                            album_art_640 = image['url']
                        elif image['height'] == 300:
                            album_art_300 = image['url']
                        elif image['height'] == 64:
                            album_art_64 = image['url']
                    a_artists = album['artists']
                    album_artists = []
                    for artist in a_artists:
                        album_artists+=[artist['name']]
                    albums+=[
                        {   
                            'album_id': album['id'],
                            'album_name': album['name'],
                            'year': album['release_date'].split('-')[0],
                            'album_artists': album_artists,
                            'album_art_640': album_art_640,
                            'album_art_300': album_art_300,
                            'album_art_64': album_art_64,
                            'album_length': album['total_tracks'],
                            'album_type': album['album_type']
                        }
                    ]
                return Response(json.dumps({'albums': albums}, indent = 4), headers= {'Content-Type' : 'application/json'}, status=200) 
            elif mode == 'track':
                tracks = []
                for track in response['tracks']['items']:
                    album_art_640 = ''
                    album_art_300 = ''
                    album_art_64 = ''
                    for image in track['album']['images']:
                        if image['height'] == 640:
                            album_art_640 = image['url']
                        elif image['height'] == 300:
                            album_art_300 = image['url']
                        elif image['height'] == 64:
                            album_art_64 = image['url']
                    a_artists = track['album']['artists']
                    album_artists = []
                    for artist in a_artists:
                        album_artists+=[artist['name']]
                    t_artists = track['artists']
                    track_artists = []
                    for artist in t_artists:
                        track_artists+=[artist['name']]
                    tracks+=[
                        {   
                            'track_id': track['id'],
                            'track_name': track['name'],
                            'track_artists': album_artists,
                            'track_number': track['track_number'],
                            'track_duration': track['duration_ms'],
                            'album_id': track['album']['id'],
                            'album_name': track['album']['name'],
                            'year': track['album']['release_date'].split('-')[0],
                            'album_artists': album_artists,
                            'album_art_640': album_art_640,
                            'album_art_300': album_art_300,
                            'album_art_64': album_art_64,
                            'album_length': track['album']['total_tracks'],
                            'album_type': track['album']['album_type']
                        }
                    ]
                return Response(json.dumps({'tracks': tracks}, indent = 4), headers= {'Content-Type' : 'application/json'}, status=200) 
            elif mode == 'artist':
                artists = []
                for artist in response['artists']['items']:
                    artist_art_640 = ''
                    artist_art_300 = ''
                    artist_art_64 = ''
                    for image in artist['images']:
                        if image['height'] == 640:
                            artist_art_640 = image['url']
                        elif image['height'] == 300:
                            artist_art_300 = image['url']
                        elif image['height'] == 64:
                            artist_art_64 = image['url']
                    artists+=[
                        {   
                            'artist_id': artist['id'],
                            'artist_name': artist['name'],
                            'artist_popularity': artist['popularity'],
                            'artist_art_640': artist_art_640,
                            'artist_art_300': artist_art_300,
                            'artist_art_64': artist_art_64,
                        }
                    ]
                return Response(json.dumps({'artists': artists}, indent = 4), headers= {'Content-Type' : 'application/json'}, status=200)
        else:
            return Response('bad request', status=400)