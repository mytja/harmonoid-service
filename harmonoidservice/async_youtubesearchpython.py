import httpx
from youtubesearchpython import SearchVideos


class SearchVideos(SearchVideos):
    networkError = False
    validResponse = False

    def __init__(self, keyword, offset=1, mode="json", max_results=20):
        self.offset = offset
        self.mode = mode
        self.keyword = keyword
        self.max_results = max_results
        self.searchPreferences = "EgIQAQ%3D%3D"

    async def main(self):
        await self.request()

        if self.networkError:
            self.networkError = True
        else:
            if not self.validResponse:
                self.scriptResponseHandler()
            if self.validResponse:
                self.pageResponseHandler()

    async def request(self):
        try:
            url = "https://www.youtube.com/results"
            params = {
                "search_query": self.keyword,
                "page": self.offset,
                "sp": self.searchPreferences,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
            self.page = response.text

            if self.page[0:29] == '  <!DOCTYPE html><html lang="':
                self.validResponse = True

        except:
            self.networkError = True
