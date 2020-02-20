import typing
import library
import audio
import settings
import flask
import threading
from . import exception


class LivePlayer(object):

    def __init__(self, player: library.live_player.LivePlayer):
        self._player = player
        self._playlist = audio.playlist.Playlist(settings.BLOCK_SIZE)
        self._playlist.set_next_callback(self._track_finished)
        self._update_event = None
        if self._player.state == library.database.LivePlayerState.paused:
            self._playlist.pause()
        else:
            self._start_thread()
        current = self._player.current_track()
        if current is not None:
            self._playlist.set_file(library.tracks.Track(current[0]).location)

    def _start_thread(self):
        self._update_event = threading.Event()
        socketio = flask.current_app.extensions['socketio']
        socketio.start_background_task(self._update_time, socketio)

    def _stop_thread(self):
        if self._update_event is not None:
            self._update_event.set()

    def _update_time(self, socketio):
        while not self._update_event.wait(1):
            socketio.emit(
                'player_tracktime_' + str(self._player.id), self._playlist.current_time()
            )
        self._update_event = None

    def _track_finished(self):
        # TODO: Handle jingle playing
        current = self._player.current_track()
        if current[1] == library.database.LivePlayerType.loop:
            self._playlist.set_file(library.tracks.Track(current[0]).location)
        elif current[1] == library.database.LivePlayerType.play_next:
            self._player.remove_track()
            current = self._player.current_track()
            if current is not None:
                self._playlist.set_file(library.tracks.Track(current[0]).location)
        else:
            self._playlist.pause()
            self._player.state = library.database.LivePlayerState.paused

    def set_state(self, state: library.database.LivePlayerState):
        if state == library.database.LivePlayerState.playing:
            if self._update_event is None:
                self._start_thread()
            self._playlist.play()
        else:
            if self._update_event is not None:
                self._stop_thread()
            self._playlist.pause()

    def set_track(self, track_id: int):
        self._playlist.set_file(library.tracks.Track(track_id).location)

    @property
    def player(self):
        return self._player

    @property
    def playlist(self):
        return self._playlist

    @property
    def id(self):
        return str(self._player.id)

    @property
    def display_name(self):
        return self._player.name


class LivePlayers(object):
    """
    A class to handle all the current LivePlayer objects
    """

    _players = []

    @classmethod
    def add(cls, player: library.live_player.LivePlayer):
        """
        Add a player to the list of players
        :param player:  The player to add
        """
        cls._players.append(LivePlayer(player))

    @classmethod
    def remove(cls, player: library.live_player.LivePlayer):
        """
        Remove a player from the list of players
        :param player:  The player to remove
        """
        player_wrapper = next(x for x in cls._players if x.player is player)
        if player_wrapper.playlist.has_callbacks():
            raise exception.InUseException('Input has current outputs')
        cls._players.remove(player_wrapper)

    @classmethod
    def restore(cls):
        """
        Restore the live players in the persistence database
        """
        for player in library.live_player.LivePlayer.list():
            cls._players.append(LivePlayer(player))

    @classmethod
    def get_player(cls, player: typing.Union[LivePlayer, str]) -> LivePlayer:
        """
        Get the LivePlayer class for the given playlist
        :param player:  The player or player ID
        :return:  The found LivePlayer instance
        :raises ValueError:  The player is not found
        """
        try:
            return next(x for x in cls._players if x.playlist is player or str(x.id) == str(player))
        except StopIteration:
            raise ValueError('No such player found')
