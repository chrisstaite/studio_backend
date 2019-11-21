import flask_restful.reqparse
import typing
import library


class LivePlayers(flask_restful.Resource):
    """
    Handler listing live players
    """

    def __init__(self):
        """
        Create the parser for adding and removing directories
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'name', type=str, help='The name of the player', required=True
        )

    @staticmethod
    def get() -> typing.List[typing.Dict]:
        """
        Get a list of all the live players
        :return:  A list of all the live players
        """
        return list({'id': player.id, 'name': player.name} for player in library.LivePlayer.list())

    def post(self) -> int:
        """
        Create a new live player
        :return:  The ID of the new live player
        """
        args = self._parser.parse_args(strict=True)
        return library.LivePlayer.create(args['name'])


class LivePlayer(flask_restful.Resource):
    """
    Handler for getting and setting the name of and removing live players
    """

    def __init__(self):
        """
        Create the parser for adding and removing directories
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'name', type=str, help='The name of the player', required=True
        )

    @staticmethod
    def get(id: int) -> str:
        """
        Get the name of the player
        :param id:  The ID of the player
        :return:  A list of all the live players
        """
        return library.LivePlayer(id).name

    def put(self, id: int) -> int:
        """
        Set the name of the player
        :param id:  The ID of the player
        :return:  Always true
        """
        args = self._parser.parse_args(strict=True)
        library.LivePlayer(id).name = args['name']
        return True

    @staticmethod
    def delete(id: int) -> bool:
        """
        Delete the player
        :param id:  The ID of the player
        :return:  Always true
        """
        library.LivePlayer(id).delete()
        return True


class LivePlayerTracks(flask_restful.Resource):
    """
    Handler adding and removing tracks for live players
    """

    def __init__(self):
        """
        Create the parser for adding and removing live players
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'tracks', type=int, action='append', help='The tracks for the playlist', required=True
        )

    def get(self, id) -> typing.List[typing.Dict]:
        """
        Get the tracks for a player
        :param id:  The ID of the player
        :return:  A list of the tracks in the player
        """
        player = library.LivePlayer(id)
        return [
            {
                'id': track,
                'type': type_.name
            } for track, type_ in player.tracks
        ]

    def put(self, id) -> bool:
        """
        Change the name of the player
        :param id:  The ID of the player
        :return:  Always true
        """
        args = self._parser.parse_args(strict=True)
        player = library.LivePlayer(id)
        # TODO
        return True


class LivePlayerState(flask_restful.Resource):
    """
    Handler for the state of a live player
    """

    def __init__(self):
        """
        Create the parser for setting the player state
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'state', type=str, help='The new state of the player', required=True
        )

    def get(self, id) -> str:
        """
        Get the state of the player
        :param id:  The ID of the player to get the state of
        :return:  The current state of the player
        """
        player = library.LivePlayer(id)
        return player.state.name

    def put(self, id) -> bool:
        """
        Set the state of the player
        :param id:  The ID of the player to set the state of
        :return:  Always true
        """
        args = self._parser.parse_args(strict=True)
        player = library.LivePlayer(id)
        player.state = library.database.LivePlayerState[args['state']]
        return True


class LivePlayerIndex(flask_restful.Resource):
    """
    Handler for the current track being played of a live player
    """

    def __init__(self):
        """
        Create the parser for setting the current index
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'index', type=int, help='The new index of the player', required=True
        )

    def get(self, id) -> int:
        """
        Get the index of the player playlist
        :param id:  The ID of the player to get the playlist index of
        :return:  The current index of the player
        """
        player = library.LivePlayer(id)
        return player.index

    def put(self, id) -> bool:
        """
        Set the current playlist index of the player
        :param id:  The ID of the player to set the index of
        :return:  Always true
        """
        args = self._parser.parse_args(strict=True)
        player = library.LivePlayer(id)
        player.index = args['index']
        return True


class LivePlayerJinglePlaylist(flask_restful.Resource):
    """
    Handler for getting and setting the playlist containing the jingles for a live player
    """

    def __init__(self):
        """
        Create the parser for setting the jingle playlist
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'id', type=int, help='The ID of the playlist that has the jingles in'
        )

    def get(self, id) -> str:
        """
        Get the ID of the current jingle playlist
        :param id:  The ID of the player to get the state of
        :return:  The ID of the current jingle playlist
        """
        player = library.LivePlayer(id)
        playlist = player.jingle_playlist
        return '' if playlist is None else str(playlist.id)

    def put(self, id) -> bool:
        """
        Set the playlist containing the jingles
        :param id:  The ID of the play to set the state of
        :return:  Always true
        """
        args = self._parser.parse_args(strict=True)
        player = library.LivePlayer(id)
        player.jingle_playlist = args['id']
        return True


class LivePlayerJingleCount(flask_restful.Resource):
    """
    Handler for getting and setting the number of songs to play before a jingle for a live player
    """

    def __init__(self):
        """
        Create the parser for setting the number of songs between the jingles in a player
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'count', type=int, help='The number of songs to play between jingles'
        )

    def get(self, id) -> int:
        """
        Get the number of songs between jingles for a player
        :param id:  The ID of the player to get the count for
        :return:  The number of songs between jingles
        """
        player = library.LivePlayer(id)
        return player.jingle_count

    def put(self, id) -> bool:
        """
        Get the number of songs between jingles for a player
        :param id:  he ID of the player to set the count for
        :return:  Always true
        """
        args = self._parser.parse_args(strict=True)
        player = library.LivePlayer(id)
        player.jingle_count = args['count']
        return True


class LivePlayerJinglePlays(flask_restful.Resource):
    """
    Handler for getting the number of songs played since the last jingle for a live player
    """

    def get(self, id) -> int:
        """
        Get the number of songs played since the last jingle for a player
        :param id:  The ID of the player to get the count for
        :return:  The number of songs played since the last jingle
        """
        player = library.LivePlayer(id)
        return player.jingle_plays


def setup_api(api):
    """
    Configure the REST endpoints for this namespace
    :param flask_restful.Api api:  The API to add the endpoints to
    """
    api.add_resource(LivePlayers, '/player')
    api.add_resource(LivePlayer, '/player/<int:id>')
    api.add_resource(LivePlayerTracks, '/player/<int:id>/tracks')
    api.add_resource(LivePlayerState, '/player/<int:id>/state')
    api.add_resource(LivePlayerIndex, '/player/<int:id>/state')
    api.add_resource(LivePlayerJinglePlaylist, '/player/<int:id>/jingle_playlist')
    api.add_resource(LivePlayerJingleCount, '/player/<int:id>/jingle_count')
    api.add_resource(LivePlayerJinglePlays, '/player/<int:id>/jingle_plays')
