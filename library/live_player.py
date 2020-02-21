import typing
import flask
from . import database
from . import playlist


class LivePlayer(object):
    """
    A special kind of playlist that supports pauses, jingles and bed
    """

    # Cached socketio instance
    _socketio = None

    @staticmethod
    def list() -> typing.Iterable['LivePlayer']:
        session = database.Session()
        try:
            for playlist in session.query(database.LivePlayer):
                yield LivePlayer(playlist.id)
        finally:
            session.close()

    @classmethod
    def create(cls, name: str) -> int:
        session = database.Session()
        playlist = database.LivePlayer(name=name, state=database.LivePlayerState.paused, jingle_plays=0)
        session.add(playlist)
        session.commit()
        import audio_manager
        audio_manager.live_player.LivePlayers.add(LivePlayer(playlist.id))
        return playlist.id

    @staticmethod
    def _emit(name, value):
        try:
            socketio = flask.current_app.extensions['socketio']
            LivePlayer._socketio = socketio
        except RuntimeError:
            # Running in background thread, use cache
            socketio = LivePlayer._socketio
        if socketio is not None:
            socketio.emit(name, value)

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

    def _get_player(self):
        import audio_manager
        return audio_manager.live_player.LivePlayers.get_player(self._playlist.id)

    @property
    def state(self) -> database.LivePlayerState:
        return self._playlist.state

    @state.setter
    def state(self, state: database.LivePlayerState):
        self._playlist.state = state
        self._session.commit()
        self._get_player().set_state(state)
        self._emit('player_state_' + str(self.id), state.name)

    @property
    def jingle_playlist(self) -> typing.Optional[playlist.Playlist]:
        playlist_id = self._playlist.jingle_playlist
        return None if not playlist_id else playlist.Playlist(playlist_id)

    @jingle_playlist.setter
    def jingle_playlist(self, playlist: playlist.Playlist):
        if playlist is None:
            self._playlist.jingle_playlist = None
            self._emit('player_jingles_' + str(self.id), '')
        else:
            self._playlist.jingle_playlist = playlist.id
            self._emit('player_jingles_' + str(self.id), playlist.id)
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

    def current_track(self) -> typing.Optional[typing.Tuple[int, database.LivePlayerType]]:
        query = self._session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index)
        track = query.first()
        if track is None:
            return None
        return track.track, track.type

    def remove_track(self):
        query = self._session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index)
        self._session.delete(query.first())
        self._session.query(database.LivePlayerTrack). \
            update({'index': (database.LivePlayerTrack.index - 1)})
        self._session.commit()
        self._send_tracks()

    def _send_tracks(self):
        query = self._session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index)
        self._emit(
            'player_tracks_' + str(self.id),
            [{'id': track.track, 'type': track.type.name} for track in query.all()]
        )

    @property
    def tracks(self) -> typing.List[typing.Tuple[int, database.LivePlayerType]]:
        query = self._session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index)
        return [(track.track, track.type) for track in query.all()]

    @tracks.setter
    def tracks(self, tracks: typing.List[typing.Tuple[int, database.LivePlayerType]]):
        current_track = self._session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index). \
            first()
        query = self._session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id)
        query.delete()
        for index, (track, type_) in enumerate(tracks):
            self._session.add(database.LivePlayerTrack(playlist=self.id, track=track, index=index, type=type_))
        self._session.commit()
        if len(tracks) > 0 and (current_track is None or tracks[0][0] != current_track.track):
            self._get_player().set_track(tracks[0][0])
        elif len(tracks) == 0:
            self._get_player().playlist.set_file(None)
        self._emit(
            'player_tracks_' + str(self.id),
            [{'id': track, 'type': type_.name} for track, type_ in tracks]
        )

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
