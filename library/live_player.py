import typing
from . import database
from . import playlist


class LivePlayer(object):
    """
    A special kind of playlist that supports pauses, jingles and bed
    """

    @staticmethod
    def list() -> typing.Iterable['LivePlayer']:
        session = database.Session()
        try:
            for playlist in session.query(database.LivePlayer):
                yield playlist
        finally:
            session.close()

    @classmethod
    def create(cls, name: str) -> int:
        session = database.Session()
        playlist = database.LivePlayer(name=name, index=0, state=database.LivePlayerState.paused, jingle_plays=0)
        session.add(playlist)
        session.commit()
        import audio_manager
        audio_manager.live_player.LivePlayers.add(LivePlayer(playlist.id))
        return playlist.id

    def __init__(self, id: int):
        """
        Create an instance of the live player represented by the given ID
        :param id:  The ID of this player
        """
        self._session = database.Session()
        self._playlist = self._session.query(database.LivePlayer).get(id)

    @property
    def name(self) -> str:
        return self._playlist.name

    @name.setter
    def name(self, name: str):
        self._playlist.name = name
        self._session.commit()

    @property
    def id(self) -> int:
        return self._playlist.id

    def delete(self):
        import audio_manager
        audio_manager.live_player.LivePlayers.remove(self)
        self._session.delete(self._playlist)
        self._session.commit()
        self._session.close()

    @property
    def state(self) -> database.LivePlayerState:
        return self._playlist.state

    @state.setter
    def state(self, state: database.LivePlayerState):
        self._playlist.state = state
        self._session.commit()

    @property
    def index(self) -> int:
        return self._playlist.index

    @index.setter
    def index(self, index: int):
        self._playlist.index = index
        self._session.commit()

    @property
    def jingle_playlist(self) -> typing.Optional[playlist.Playlist]:
        playlist_id = self._playlist.jingle_playlist
        return None if not playlist_id else playlist.Playlist(playlist_id)

    @jingle_playlist.setter
    def jingle_playlist(self, playlist: playlist.Playlist):
        if playlist is None:
            self._playlist.jingle_playlist = None
        else:
            self._playlist.jingle_playlist = playlist.id
        self._session.commit()

    @property
    def jingle_count(self) -> int:
        return self._playlist.jingle_count

    @jingle_count.setter
    def jingle_count(self, jingle_count: typing.Optional[int]):
        self._playlist.jingle_count = jingle_count
        if jingle_count is None:
            self._playlist.jingle_plays = 0
        self._session.commit()

    @property
    def jingle_plays(self) -> int:
        return self._playlist.jingle_plays

    @jingle_plays.setter
    def jingle_plays(self, jingle_plays: int):
        self._playlist.jingle_plays = jingle_plays
        self._session.commit()

    @property
    def tracks(self) -> typing.List[typing.Tuple[int, database.LivePlayerType]]:
        query = self._session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index)
        return [(track.track, track.type) for track in query.all()]

    @tracks.setter
    def tracks(self, tracks: typing.List[typing.Tuple[int, database.LivePlayerType]]):
        query = self._session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id)
        query.delete()
        for index, (track, type_) in enumerate(tracks):
            self._session.add(database.LivePlayerTrack(playlist=self.id, track=track, index=index, type=type_))
        self._session.commit()

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
