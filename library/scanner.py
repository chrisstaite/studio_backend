import audioread
import eyed3
import watchdog.observers
import watchdog.events
import os
import sys
import typing
import database


class DirectoryScanner(watchdog.events.FileSystemEventHandler):
    """
    A class that searches a directory for all audio files to populate the database
    and then watches it for changes.
    """

    def __init__(self, directory: str):
        """
        Setup for scanning
        :param directory:  The directory to scan for audio files in
        """
        self._directory = directory

    def start(self):
        """
        Walk over all the files in this directory recursively to check they are in the library
        """
        for path, _, filenames in os.walk(self._directory):
            for filename in filenames:
                self._parse_file(os.path.join(path, filename))
        directory_observer = watchdog.observers.Observer()
        directory_observer.schedule(self, self._directory, recursive=True)
        directory_observer.start()

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


if __name__ == "__main__":
    DirectoryScanner(sys.argv[1]).start()
