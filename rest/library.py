import os
import typing
import flask
import mimetypes
import flask_restful.reqparse
import library


class Library(flask_restful.Resource):
    """
    Handler adding and removing root directories from the library
    """

    def __init__(self):
        """
        Create the parser for adding and removing directories
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'directory', type=str, help='The location to add as a library root', required=True
        )

    @staticmethod
    def get() -> typing.List[str]:
        """
        Get a list of all the root directories in the library
        :return:  A list of all the root directories for the library
        """
        return list(library.Library.list())

    def delete(self) -> bool:
        """
        Remove a directory from the list of roots
        :return:  Always true
        """
        args = self._parser.parse_args(strict=True)
        library.Library.remove_directory(args['directory'])
        return True

    def post(self) -> bool:
        """
        Add a directory to the list of roots
        :return:  Always true
        """
        args = self._parser.parse_args(strict=True)
        library.Library.add_directory(args['directory'])
        return True


class TrackSearch(flask_restful.Resource):
    """
    Handler searching for tracks within the library
    """

    def __init__(self):
        """
        Create the parser for querying
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'query', type=str, help='The query to search for'
        )
        self._parser.add_argument(
            'results', type=int, help='The number of results per page', default=20
        )
        self._parser.add_argument(
            'page', type=int, help='The page to get the results for (0-indexed)', default=0
        )

    def get(self) -> typing.Dict:
        """
        Get a list of all the tracks matching the query
        :return:  A list of all tracks matching
        """
        args = self._parser.parse_args(strict=True)
        tracks = library.Tracks(args['results'], args['query'])
        return {
            'count': tracks.count(),
            'tracks': [
                {
                    'id': track.id,
                    'location': track.location,
                    'title': track.title,
                    'artist': track.artist,
                    'length': track.length
                } for track in tracks[args['page']]
            ]
        }


class Track(flask_restful.Resource):
    """
    Handler for playing tracks and updating their details
    """

    def __init__(self):
        """
        Create the parser for querying
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'artist', type=str, help='The artist name'
        )
        self._parser.add_argument(
            'title', type=str, help='The title name'
        )

    def get(self, id: int) -> typing.Dict:
        """
        Get a list of all the tracks matching the query
        :param id:  The ID of the track
        :return:  A list of all tracks matching
        """
        def generate(track_):
            with open(track_.location, 'rb') as file_:
                data = file_.read(1024)
                while data:
                    yield data
                    data = file_.read(1024)
        track = library.Track(id)
        mimetype, encoding = mimetypes.guess_type(track.location)
        if mimetype is None:
            mimetype = 'audio/mpeg'
        return flask.Response(generate(track), mimetype=mimetype)

    def put(self, id: int) -> bool:
        """
        Change the track details
        :param id:  The ID of the track
        :return:  Always true
        """
        args = self._parser.parse_args(strict=True)
        track = library.Track(id)
        if args['title'] is not None:
            track.title = args['title']
        if args['artist'] is not None:
            track.artist = args['artist']
        return True


class Filesystem(flask_restful.Resource):

    @staticmethod
    def _windows_roots() -> typing.List[str]:
        """
        Get the root drives on Windows
        :return:  The root drives on Windows
        """
        import ctypes.windll
        import string
        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in string.lowercase:
            if bitmask & 1:
                drives.append(letter)
            bitmask >>= 1
        return drives

    @staticmethod
    def _list_dirs(location: str) -> typing.Iterable[str]:
        """
        Get a list of directories in a given location
        :param location:  The location to list from
        :return:  An iterable of the directories available
        """
        try:
            if hasattr(os, 'scandir'):
                # Optimised implementation for 3.5+
                with os.scandir(location) as it:
                    for entry in it:
                        if entry.is_dir() and not entry.name.startswith('.'):
                            yield entry.name
            else:
                # Stupid implementation that has to do a lot of work
                for path in os.listdir(location):
                    if not path.startswith('.') and os.path.isdir(os.path.join(location, path)):
                        yield path
        except (FileNotFoundError, NotADirectoryError):
            flask_restful.abort(404, message='Directory does not exist')
        except PermissionError:
            flask_restful.abort(403, message='Inaccessible directory')

    def get(self, location: str = None) -> typing.List[str]:
        """
        Get a list of the directories in a given directory
        :param location:  The location to search from (None means the root)
        :return:  A list of the directories in the given directory
        """
        if os.name == 'nt':
            if location is None:
                # On Windows, the root is the drive letters
                return self._windows_roots()
            else:
                # Need to add the colon back in for the search to work
                location = location[0] + ":" + location[1:]
        else:
            # Every other system is sane
            if location is None:
                location = '/'
            else:
                location = '/' + location
        return list(self._list_dirs(location))


class Playlists(flask_restful.Resource):
    """
    Handler listing playlists
    """

    def __init__(self):
        """
        Create the parser for adding and removing directories
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'name', type=str, help='The name of the playlist', required=True
        )

    @staticmethod
    def get() -> typing.List[typing.Dict]:
        """
        Get a list of all the playlists
        :return:  A list of all the playlists
        """
        return list({'id': playlist.id, 'name': playlist.name} for playlist in library.Playlist.list())

    def post(self) -> int:
        """
        Create a new playlist
        :return:  The ID of the new playlist
        """
        args = self._parser.parse_args(strict=True)
        return library.Playlist.create(args['name'])


class Playlist(flask_restful.Resource):
    """
    Handler adding and removing playlists
    """

    def __init__(self):
        """
        Create the parser for adding and removing directories
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'name', type=str, help='The name of the playlist'
        )
        self._parser.add_argument(
            'tracks', type=int, action='append', help='The tracks for the playlist'
        )

    def get(self, id) -> typing.List[typing.Dict]:
        """
        Get the tracks for a playlist
        :param id:  The ID of the playlist
        :return:  A list of the tracks in the playlist
        """
        playlist = library.Playlist(id)
        return [
            {
                'id': track.id,
                'location': track.location,
                'title': track.title,
                'artist': track.artist,
                'length': track.length
            } for track in playlist
        ]

    def put(self, id) -> bool:
        """
        Change the name of the playlist
        :param id:  The ID of the playlist
        :return:  Always true
        """
        args = self._parser.parse_args(strict=True)
        playlist = library.Playlist(id)
        if args['name'] is not None:
            playlist.name = args['name']
        if args['tracks'] is not None:
            playlist.tracks = args['tracks']
        return True

    @staticmethod
    def delete(id) -> bool:
        """
        Delete the
        :param id:  The ID of the playlist
        :return:  Always true
        """
        library.Playlist(id).delete()
        return True


def setup_api(api):
    """
    Configure the REST endpoints for this namespace
    :param flask_restful.Api api:  The API to add the endpoints to
    """
    api.add_resource(Filesystem, '/browse', '/browse/<path:location>')
    api.add_resource(Library, '/library')
    api.add_resource(TrackSearch, '/library/track')
    api.add_resource(Track, '/library/track/<int:id>')
    api.add_resource(Playlists, '/playlist')
    api.add_resource(Playlist, '/playlist/<int:id>')


mimetypes.init()
