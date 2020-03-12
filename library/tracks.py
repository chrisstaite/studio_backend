import typing
import sqlalchemy
from . import database


class Track(object):
    """
    An accessor for updating a track
    """

    def __init__(self, id):
        """
        Open a track or editing
        :param id:  The ID of the track
        """
        session = database.db.session
        self.__dict__['_session'] = session
        self.__dict__['_track'] = session.query(database.Track).get(id)

    def record_play(self):
        """
        Record a track being played
        """
        session = database.db.session
        session.add(database.TrackPlay(track=self._track.id))
        session.commit()

    def last_play(self):
        """
        Get the last time this track was played
        :return:  The last time the track was played
        """
        session = self._session
        last_play = session.query(database.TrackPlay). \
            filter(database.TrackPlay.track == self._track.id). \
            order_by(database.TrackPlay.time). \
            first()
        return None if last_play is None else last_play.time

    def __getattr__(self, item):
        """
        Get an attribute from the underlying object
        :param item:  The name of the attribute to get
        :return:  The underlying attribute
        """
        local_value = getattr(self.__dict__, item, None)
        return local_value if local_value is not None else getattr(self.__dict__['_track'], item)

    def __setattr__(self, key, value):
        """
        Set an attribute on the underlying object
        :param key:  The item to update
        :param value:  The value to set
        """
        track = self.__dict__['_track']
        setattr(track, key, value)
        self.__dict__['_session'].commit()


class Tracks(object):
    """
    An accessor for searching tracks
    """

    def __init__(self, results: int, query: str = None):
        """
        Start a query for a given track
        :param results:  The number of results per page
        :param query:  The thing to search for
        """
        self._session = database.db.session
        self._query = self._session.query(database.Track)
        if query is not None:
            self._query = self._query.filter(sqlalchemy.or_(
                database.Track.location.contains(query),
                database.Track.artist.contains(query),
                database.Track.title.contains(query)
            ))
        self._count = self._query.count()
        self._results = results

    def count(self) -> int:
        """
        Get the total number of results
        :return:  The total number of results
        """
        return self._count

    def __len__(self) -> int:
        """
        Get the total number of pages
        :return:  The total number of pages
        """
        return self._count // self._results

    def __getitem__(self, index: int) -> typing.Iterable[database.Track]:
        """
        Iterate over the tracks on a given page
        :param index:  The page to get
        :return:  An iterator of the results on that page
        """
        for track in self._query.offset(self._results * index).limit(self._results).all():
            yield track
