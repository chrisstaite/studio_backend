from . import callback
from . import file


class Playlist(callback.Callback):
    """
    A class that encapsulates a number of file names, the topmost of which is wrapped by a audio.file.File.
    """

    def __init__(self, blocks):
        """
        Create a new empty playlist
        :param blocks:  The block size to use
        """
        super().__init__()
        self._files = []
        self._file = None
        self._blocks = blocks

    def add_file(self, filename):
        """
        Add a file to the end of the playlist
        :param filename:  The file to add to the end of the playlist
        """
        self._files.append(filename)
        if len(self._files) == 0:
            self._load_file()

    def _load_file(self):
        """
        Load the next file in the playlist
        """
        self._file = file.File(self._files[0], self._blocks)
        self._file.add_callback(self._forward)

    def _next_file(self):
        """
        Used as callback when file is finished to play the next one
        """
        self._files.pop()
        if len(self._files) > 0:
            self._load_file()
            self.play()
        else:
            self._file = None

    def _forward(self, source, blocks):
        """
        A forwarder for file blocks to the receiver
        :param source:  The origin of the blocks
        :param blocks:  The blocks of audio
        """
        self.notify_callbacks(blocks)

    def play(self):
        """
        Play the playlist
        """
        self._file.set_end_callback(self._next_file)
        self._file.play()

    def stop(self):
        """
        Stop playing
        """
        if self._file is not None:
            self._file.set_end_callback(None)
            self._file.stop()
