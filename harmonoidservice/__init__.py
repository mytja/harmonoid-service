from .browsing import BrowsingHandler
from .downloading import DownloadHandler
import ytmusicapi

class HarmonoidService(BrowsingHandler, DownloadHandler):
    ytmusic = ytmusicapi.YTMusic()
