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
        session = database.db.session
        try:
            for playlist in session.query(database.LivePlayer):
                yield LivePlayer(playlist.id)
        finally:
            session.close()

    @classmethod
    def create(cls, name: str) -> int:
        session = database.db.session
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
        self._playlist_id = id

    @property
    def name(self) -> str:
        return database.db.session.query(database.LivePlayer).get(self._playlist_id).name

    @name.setter
    def name(self, name: str):
        session = database.db.session
        session.query(database.LivePlayer). \
            filter(database.LivePlayer.id == self._playlist_id). \
            update({database.LivePlayer.name: name})
        session.commit()

    @property
    def id(self) -> int:
        return self._playlist_id

    def delete(self):
        import audio_manager
        audio_manager.live_player.LivePlayers.remove(self)
        session = database.db.session
        session.query(database.LivePlayer). \
            filter(database.LivePlayer.id == self._playlist_id). \
            delete()
        session.commit()

    def _get_player(self):
        import audio_manager
        return audio_manager.live_player.LivePlayers.get_player(str(self._playlist_id))

    @property
    def state(self) -> database.LivePlayerState:
        return database.db.session.query(database.LivePlayer).get(self._playlist_id).state

    @state.setter
    def state(self, state: database.LivePlayerState):
        session = database.db.session
        session.query(database.LivePlayer). \
            filter(database.LivePlayer.id == self._playlist_id). \
            update({database.LivePlayer.state: state})
        session.commit()
        self._get_player().set_state(state)
        self._emit('player_state_' + str(self.id), state.name)

    @property
    def jingle_playlist(self) -> typing.Optional[playlist.Playlist]:
        playlist_id = database.db.session.query(database.LivePlayer).get(self._playlist_id).jingle_playlist
        return None if not playlist_id else playlist.Playlist(playlist_id)

    @jingle_playlist.setter
    def jingle_playlist(self, playlist: playlist.Playlist):
        session = database.db.session
        session.query(database.LivePlayer). \
            filter(database.LivePlayer.id == self._playlist_id). \
            update({database.LivePlayer.jingle_playlist: None if playlist is None else playlist.id})
        session.commit()
        self._emit('player_jingles_' + str(self.id), '' if playlist is None else playlist.id)

    @property
    def jingle_count(self) -> int:
        return database.db.session.query(database.LivePlayer).get(self._playlist_id).jingle_count

    @jingle_count.setter
    def jingle_count(self, jingle_count: typing.Optional[int]):
        session = database.db.session
        update = {
            database.LivePlayer.jingle_count: jingle_count
        }
        if jingle_count is None:
            update[database.LivePlayer.jingle_plays] = 0
        session.query(database.LivePlayer). \
            filter(database.LivePlayer.id == self._playlist_id). \
            update(update)
        session.commit()

    @property
    def jingle_plays(self) -> int:
        return database.db.session.query(database.LivePlayer).get(self._playlist_id).jingle_plays

    @jingle_plays.setter
    def jingle_plays(self, jingle_plays: int):
        session = database.db.session
        session.query(database.LivePlayer). \
            filter(database.LivePlayer.id == self._playlist_id). \
            update({database.LivePlayer.jingle_plays: jingle_plays})
        session.commit()

    def current_track(self) -> typing.Optional[typing.Tuple[int, database.LivePlayerType]]:
        query = database.db.session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index)
        track = query.first()
        if track is None:
            return None
        return track.track, track.type

    def remove_track(self):
        session = database.db.session
        query = session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index)
        session.delete(query.first())
        session.query(database.LivePlayerTrack). \
            update({'index': (database.LivePlayerTrack.index - 1)})
        session.commit()
        self._send_tracks(session)

    def _send_tracks(self, session):
        query = session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index)
        self._emit(
            'player_tracks_' + str(self.id),
            [{'id': track.track, 'type': track.type.name} for track in query.all()]
        )

    @property
    def tracks(self) -> typing.List[typing.Tuple[int, database.LivePlayerType]]:
        query = database.db.session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index)
        return [(track.track, track.type) for track in query.all()]

    @tracks.setter
    def tracks(self, tracks: typing.List[typing.Tuple[int, database.LivePlayerType]]):
        session = database.db.session
        current_track = session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id). \
            order_by(database.LivePlayerTrack.index). \
            first()
        query = session.query(database.LivePlayerTrack). \
            filter(database.LivePlayerTrack.playlist == self.id)
        query.delete()
        for index, (track, type_) in enumerate(tracks):
            session.add(database.LivePlayerTrack(playlist=self.id, track=track, index=index, type=type_))
        session.commit()
        if len(tracks) > 0 and (current_track is None or tracks[0][0] != current_track.track):
            self._get_player().set_track(tracks[0][0])
            self._emit('player_tracktime_' + str(self.id), 0)
        elif len(tracks) == 0:
            self._emit('player_tracktime_' + str(self.id), 0)
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
        query = database.db.session.query(database.Track, database.PlaylistTrack). \
            filter(database.PlaylistTrack.playlist == self.id). \
            filter(database.Track.id == database.PlaylistTrack.track). \
            order_by(database.PlaylistTrack.index)
        for track, playlist_track in query.all():
            yield track
