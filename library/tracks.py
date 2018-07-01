import typing
import sqlalchemy
from . import database


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
        self._session = database.Session()
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
