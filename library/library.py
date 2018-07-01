import typing
import subprocess
import sys
import os.path
import atexit
from . import database


class DirectoryScanner(object):
    """
    A class that manages the external directory scanner process
    """

    def __init__(self, directory: str):
        """
        Start scanning for files in the directory and changes and keep the database up to date
        :param directory:  The directory to scan for audio files in
        """
        self._directory = directory
        self._process = subprocess.Popen([
            sys.executable, os.path.join(os.path.dirname(__file__), 'scanner.py'), directory
        ])
        atexit.register(self.close)

    @property
    def directory(self) -> str:
        """
        Get the directory location that this scanner is working for
        :return:  The location that is being scanned by this scanner
        """
        return self._directory

    def close(self):
        """
        Stop scanning for files in this directory
        """
        atexit.unregister(self.close)
        self._process.terminate()


class Library(object):
    """
    The maintainer of the library root directories
    """

    _directory_handlers = []

    @classmethod
    def add_directory(cls, directory: str):
        """
        Add a directory to the library
        :param directory:  The location of the directory to add
        """
        session = database.Session()
        if session.query(database.Library.id).filter(database.Library.location.startswith(directory)).count() == 0:
            cls._directory_handlers.append(DirectoryScanner(directory))
            session.add(database.Library(location=directory))
            session.commit()
        session.close()

    @classmethod
    def remove_directory(cls, directory: str):
        """
        Remove a directory from the library
        :param directory:  The location of the directory to remove
        """
        try:
            handler = next(x for x in cls._directory_handlers if x.directory == directory)
        except StopIteration:
            return
        handler.close()
        cls._directory_handlers.remove(handler)
        session = database.Session()
        session.query(database.Library).filter_by(location=directory).delete()
        session.query(database.Track).filter(database.Track.location.startswith(directory)).delete()
        session.commit()
        session.close()

    @classmethod
    def list(cls) -> typing.Iterable[str]:
        """
        Get an iterator over the directories for the root of the library
        :return:  An iterator of the directories
        """
        for handler in cls._directory_handlers:
            yield handler.directory

    @classmethod
    def restore(cls):
        """
        Load the library from the database
        """
        session = database.Session()
        for directory in session.query(database.Library).all():
            cls._directory_handlers.append(DirectoryScanner(directory.location))
        session.close()


Library.restore()
