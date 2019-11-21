import typing
import library
import audio
import settings
from . import exception


class LivePlayer(object):

    def __init__(self, player: library.live_player.LivePlayer):
        self._player = player
        self._playlist = audio.playlist.Playlist(settings.BLOCK_SIZE)
        self._playlist.set_next_callback(self._track_finished)
        if self._player.state == library.database.LivePlayerState.playing:
            current = self._player.tracks[self._player.index]
            self._playlist.set_file(library.tracks.Track(current[0]).location)

    def _track_finished(self):
        # TODO: Handle jingle playing
        index = self._player.index
        current = self._player.tracks[index]
        if current[1] == library.database.LivePlayerType.loop:
            self._playlist.set_file(library.tracks.Track(current[0]).location)
        elif current[1] == library.database.LivePlayerType.play_next:
            index += 1
            current = self._player.tracks[index]
            self._playlist.set_file(library.tracks.Track(current[0]).location)
            self._player.index = index
        else:
            self._player.state = library.database.LivePlayerState.paused

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
            return next(x for x in cls._players if x.playlist is player or x.id == player)
        except StopIteration:
            raise ValueError('No such player found')
