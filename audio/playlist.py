import numpy
import typing
from . import callback
from . import file


class Playlist(callback.Callback):
    """
    A class that requests the next file when the last has finished, when provided, wraps in a audio.file.File.
    """

    def __init__(self, blocks: int):
        """
        Create a new empty playlist
        :param blocks:  The block size to use
        """
        super().__init__()
        self._callback = None
        self._file = None
        self._paused = False
        self._blocks = blocks

    @property
    def channels(self) -> int:
        """
        Get the number of output channels for this playlist
        :return:  The number of output channels
        """
        return 2 if self._file is None else self._file.channels

    def set_next_callback(self, callback: typing.Optional[typing.Callable]) -> None:
        """
        Set the callback that is called when the current file has finished playing
        :param callback:  The callback to call
        """
        self._callback = callback

    def set_file(self, filename: str) -> None:
        """
        Set the current playback file, replacing the current one and start it playing
        :param filename:  The file to set as playing
        """
        if self._file is not None:
            self.stop()
        self._file = file.File(filename, self._blocks)
        self._file.add_callback(self._forward)
        self._file.set_end_callback(self._next_file)
        if not self._paused:
            self._file.play()

    def current_time(self) -> float:
        """
        Get the number of seconds into the current file
        :return:  The number of seconds into the current file
        """
        return 0.0 if self._file is None else self._file.time()

    def _next_file(self) -> None:
        """
        Used as callback when file is finished to play the next one
        """
        self._file = None
        if self._callback is not None:
            self._callback()

    def _forward(self, _, blocks: numpy.array) -> None:
        """
        A forwarder for file blocks to the receiver
        :param blocks:  The blocks of audio
        """
        self.notify_callbacks(blocks)

    def play(self) -> None:
        """
        Play the playlist
        """
        self._paused = False
        if self._file is not None:
            self._file.set_end_callback(self._next_file)
            self._file.play()

    def pause(self) -> None:
        """
        Pause the playlist
        """
        self._paused = True
        if self._file is not None:
            self._file.set_end_callback(None)
            self._file.pause()

    def stop(self) -> None:
        """
        Stop playing
        """
        if self._file is not None:
            self._file.set_end_callback(None)
            self._file.stop()
