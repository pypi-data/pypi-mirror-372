from plexflow.utils.api.rest.plexful import Plexful
from plexflow.core.torrents.providers.tpb.utils import TPBSearchResult

class TPB(Plexful):
    def __init__(self, base_url: str = 'https://apibay.org'):
        super().__init__(base_url=base_url)
    
    def search(self, query: str, headless: bool = True, **kwargs) -> list[TPBSearchResult]:
        response = self.get('/q.php', query_params={
            'q': query,
        }, headless=headless, **kwargs)
        
        if headless:
            response.raise_for_status()
            data = response.json()
        else:
            data = response.json
 
        return list(map(lambda x: TPBSearchResult(**x), data))
