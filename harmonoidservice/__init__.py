from harmonoidservice.spotify import SpotifyHandler
from harmonoidservice.youtube import YoutubeHandler


class HarmonoidService(SpotifyHandler, YoutubeHandler):
    def __init__(self, clientId, clientSecret):
        self.clientId = clientId
        self.clientSecret = clientSecret
