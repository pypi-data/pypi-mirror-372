from datetime import datetime
from plexflow.core.torrents.results.torrent import Torrent
from plexflow.utils.imdb.imdb_codes import IMDbCode
from plexflow.utils.torrent.hash import extract_torrent_hash

class ExtraTorrentSearchResult(Torrent):
    def __init__(self, **kwargs):
        super().__init__()
        self._magnet = kwargs.get('magnet_link')
        self._name = kwargs.get('name')
        self._date = kwargs.get('date')
        self._type = kwargs.get('type')
        self._size = kwargs.get('size_bytes')
        self._seeds = kwargs.get('seeds')
        self._peers = kwargs.get('peers')
        self._link = kwargs.get('link')
        self._uploader = kwargs.get('uploader')
        self.src = 'extratorrent'

    @property
    def source(self) -> str:
        return self.src

    @property
    def magnet(self) -> str:
        return self._magnet

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def seeds(self) -> int:
        return self._seeds

    @property
    def peers(self) -> int:
        return self._peers

    @property
    def size_bytes(self) -> int:
        return self._size

    @property
    def imdb_code(self) -> IMDbCode:
        return None

    @property
    def release_name(self) -> str:
        return self._name

    @property
    def hash(self) -> str:
        return extract_torrent_hash(self._magnet)

    @property
    def uploader(self) -> str:
        return self._uploader

    @property
    def url(self) -> str:
        return self._link

    @property
    def category(self) -> str:
        return self._type
