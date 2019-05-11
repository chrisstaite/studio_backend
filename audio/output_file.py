import os.path
import datetime
from . import mp3


class RollingFile(object):
    """
    A class that can sink to an audio file which rolls every hour of recording
    """

    ROLL_TIME_SECONDS = 60 * 60

    def __init__(self, base_path: str, quality: int = 7, bitrate: int = 64):
        """
        Create a new rolling file output
        :param base_path:  The path to add the time to which is recorded to
        """
        self._base = base_path
        self._current_file = None
        self._start_time = None
        self._source = None
        self._output = mp3.Mp3(quality, bitrate)
        self._output.add_callback(self._write_file)

    @property
    def base_path(self) -> str:
        """
        Get the base path of the file that is recorded to, the actual file has the time added
        :return:  The base path of the file to record
        """
        return self._base

    @property
    def channels(self) -> int:
        """
        Get the number of channels recorded from the source
        :return:  The number of channels
        """
        if self._source is None:
            return 0
        return self._source.channels

    @property
    def input(self):
        """
        Get the current input
        :return:  The current input
        """
        return self._source

    @input.setter
    def input(self, source) -> None:
        """
        Set the audio source to write to the file
        :param source:  The source
        """
        if source is self._source:
            return
        self._source = source
        self._output.input = source
        # Roll the file if we have a new source
        if self._current_file is not None:
            tmp = self._current_file
            self._current_file = None
            tmp.close()

    def close(self) -> None:
        """
        Stop generating MP3 output because the stream has stopped
        """
        self._output.remove_callback(self._write_file)
        if self._source is not None:
            self._output.input = None
        if self._current_file is not None:
            self._current_file.close()

    def _open_file(self) -> None:
        """
        Create a filename for the file and open it ready to write to
        """
        now = datetime.datetime.now()
        timestamp = now.strftime('_%Y%m%d-%H%M%S')
        filename, ext = os.path.splitext(os.path.basename(self.base_path))
        if ext.lower() != '.mp3':
            ext += '.mp3'
        filename = filename + timestamp + ext
        path = os.path.join(os.path.dirname(self.base_path), filename)
        self._current_file = open(path, 'wb')
        self._start_time = now

    def _write_file(self, _, blocks: bytes) -> None:
        """
        The handler for MP3 blocks to write to the file
        :param blocks:  The data produced (the MP3)
        """
        if self._current_file is None:
            self._open_file()
        elif datetime.datetime.now() - self._start_time > datetime.timedelta(seconds=self.ROLL_TIME_SECONDS):
            self._current_file.close()
            self._open_file()
        self._current_file.write(blocks)
