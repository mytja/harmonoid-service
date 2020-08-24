from harmonoidservice import HarmonoidService
from flask import Flask, request, Response
from os import getenv

harmonoidService = HarmonoidService(getenv('SPOTIFY_CLIENT_ID'), getenv('SPOTIFY_CLIENT_SECRET'))
main = Flask(__name__)

@main.route('/')
def Hello():
    return Response('service is running', status=200, headers={'Content-Type' : 'text/html'})

@main.route('/accesstoken')
def AccessToken():
    return harmonoidService.AccessToken()

@main.route('/search')
def SearchSpotify():
    return harmonoidService.SearchSpotify(request.args.get('keyword', None), request.args.get('mode', 'album'), int(request.args.get('offset', 0)), int(request.args.get('limit', 50)))

@main.route('/searchyoutube')
def SearchYoutube():
    return harmonoidService.SearchYoutube(request.args.get('keyword', None), int(request.args.get('offset', 1)), request.args.get('mode', 'json'), int(request.args.get('max_results', 10)))

@main.route('/albuminfo')
def AlbumInfo():
    return harmonoidService.AlbumInfo(request.args.get('album_id', None))

@main.route('/trackinfo')
def TrackInfo():
    return harmonoidService.TrackInfo(request.args.get('track_id', None))

@main.route('/artistrelated')
def ArtistRelated():
    return harmonoidService.ArtistRelated(request.args.get('artist_id', None))

@main.route('/artistalbums')
def ArtistAlbums():
    return harmonoidService.ArtistAlbums(request.args.get('artist_id', None))

@main.route('/artisttracks')
def ArtistTracks():
    return harmonoidService.ArtistTracks(request.args.get('artist_id', None))

@main.route('/trackdownload')
def TrackDownload():
    return harmonoidService.TrackDownload(request.args.get('track_id', None), request.args.get('track_name', None))

if __name__ == '__main__':
    main.run()