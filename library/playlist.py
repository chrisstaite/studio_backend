import typing
from . import database


class Playlist(object):

    @staticmethod
    def list() -> typing.Iterable['Playlist']:
        session = database.Session()
        try:
            for playlist in session.query(database.Playlist):
                yield playlist
        finally:
            session.close()

    @classmethod
    def create(cls, name: str) -> int:
        session = database.Session()
        playlist = database.Playlist(name=name)
        session.add(playlist)
        session.commit()
        return playlist.id

    def __init__(self, id: int):
        self._session = database.Session()
        self._playlist = self._session.query(database.Playlist).get(id)

    @property
    def name(self) -> str:
        return self._playlist.name

    @name.setter
    def name(self, name: str):
        self._playlist.name = name
        self._session.commit()

    @property
    def tracks(self) -> typing.List[int]:
        query = self._session.query(database.PlaylistTrack). \
            filter(database.PlaylistTrack.playlist == self.id). \
            order_by(database.PlaylistTrack.index)
        return [track.track for track in query.all()]

    @tracks.setter
    def tracks(self, tracks: typing.List[int]):
        self._session.query(database.PlaylistTrack). \
            filter(database.PlaylistTrack.playlist == self.id).delete()
        for index, track in enumerate(tracks):
            self._session.add(database.PlaylistTrack(playlist=self.id, track=track, index=index))
        self._session.commit()

    @property
    def id(self) -> int:
        return self._playlist.id

    def delete(self):
        self._session.query(database.PlaylistTrack). \
            filter(database.PlaylistTrack.playlist == self.id).delete()
        self._session.delete(self._playlist)
        self._session.commit()
        self._session.close()

    def __iter__(self) -> typing.Iterable[database.Track]:
        """
        Iterate over the tracks on a given page
        :return:  An iterator of the results on that page
        """
        query = self._session.query(database.Track, database.PlaylistTrack). \
            filter(database.PlaylistTrack.playlist == self.id). \
            filter(database.Track.id == database.PlaylistTrack.track). \
            order_by(database.PlaylistTrack.index)
        for track, playlist_track in query.all():
            yield track
