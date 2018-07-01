import os
import typing
import watchdog.observers
import watchdog.events
import threading
import audioread
import eyed3
from . import database


class DirectoryScanner(watchdog.events.FileSystemEventHandler):
    """
    A class that searches a directory for all audio files to populate the database
    and then watches it for changes.
    """

    def __init__(self, directory: str):
        """
        Start scanning for files in the directory and changes and keep the database up to date
        :param directory:  The directory to scan for audio files in
        """
        self._directory = directory
        self._scan = True
        threading.Thread(target=self._walk, daemon=True).start()
        self._directory_observer = watchdog.observers.Observer()
        self._directory_observer.schedule(self, self._directory, recursive=True)

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
        self._scan = False
        self._directory_observer.stop()
        self._directory_observer.join()

    def _walk(self):
        """
        Walk over all the files in this directory recursively to check they are in the library
        """
        for path, _, filenames in os.walk(self._directory):
            for filename in filenames:
                if not self._scan:
                    return
                self._parse_file(os.path.join(path, filename))
        self._directory_observer.start()

    def on_moved(self, event: typing.Union[watchdog.events.DirMovedEvent, watchdog.events.FileMovedEvent]):
        """
        Called when a file or a directory is moved or renamed
        :param event:  Event representing file/directory movement
        """
        session = database.Session()
        if isinstance(event, watchdog.events.FileMovedEvent):
            track = session.query(database.Track).filter_by(filename=event.src_path).one_or_none()
            if track is not None:
                track.location = event.dest_path
                session.commit()
        else:
            for track in session.query(database.Track).filter(database.Track.location.startswith(event.src_path)).all():
                track.location = event.dest_path + track.location[len(event.src_path):]
            session.commit()
        session.close()

    def on_created(self, event: typing.Union[watchdog.events.DirCreatedEvent, watchdog.events.FileCreatedEvent]):
        """
        Called when a file or directory is created
        :param event:  Event representing file/directory creation
        """
        if isinstance(event, watchdog.events.FileCreatedEvent):
            self._parse_file(event.src_path)

    def on_deleted(self, event: typing.Union[watchdog.events.DirDeletedEvent, watchdog.events.FileDeletedEvent]):
        """
        Called when a file or directory is deleted
        :param event:  Event representing file/directory deletion
        """
        session = database.Session()
        if isinstance(event, watchdog.events.FileDeletedEvent):
            session.query(database.Track).filter_by(location=event.src_path).delete()
        elif isinstance(event, watchdog.events.DirDeletedEvent):
            session.query(database.Track).filter(database.Track.location.startswith(event.src_path)).delete()
        session.commit()
        session.close()

    def on_modified(self, event: typing.Union[watchdog.events.DirModifiedEvent, watchdog.events.FileModifiedEvent]):
        """
        Called when a file or directory is modified
        :param event:  Event representing file/directory modification
        """
        if isinstance(event, watchdog.events.FileModifiedEvent):
            # If it wasn't there before, but is now playable, add it
            self._parse_file(event.src_path)

    @staticmethod
    def _parse_file(filename: str):
        """
        Add a new file to the database if it doesn't already exist and it is an audio file
        :param filename:  The path of the file to add
        """
        session = database.Session()
        file = session.query(database.Track).filter_by(location=filename).one_or_none()
        if file is not None:
            session.close()
            return
        try:
            audioread.audio_open(filename).close()
            valid = True
        except:
            valid = False
        if valid:
            try:
                file = eyed3.load(filename)
                artist = file.tag.artist
                title = file.tag.artist
            except:
                artist = ''
                title = ''
            session.add(database.Track(location=filename, artist=artist, title=title))
            session.commit()
        session.close()


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
