import audioread
import threading
import numpy
import queue
from . import callback


class File(callback.Callback):
    """
    A wrapper around an audio file that allows it to be played as an input
    """

    def __init__(self, path, blocks, clock_source):
        """
        Open an audio file ready to play it
        :param path:  The path to the file to play
        :param blocks:  The number of blocks to read at a time per channel
        :param clock_source:  The source of timing callbacks, usually an output device
        """
        super().__init__()
        self._file = audioread.audio_open(path)
        self._blocks = blocks * self._file.channels
        self._playing = False
        self._clock_source = clock_source
        self._queue = queue.Queue(maxsize=4)

    def channels(self):
        """
        Get the number of channels in this file
        :return:  The number of audio channels in this file
        """
        return self._file.channels

    def play(self):
        """
        Start the audio file playing to callbacks
        """
        if self._playing:
            return
        self._playing = True
        self._clock_source.add_callback(self._callback)
        threading.Thread(target=self._play_thread, daemon=True).start()

    def stop(self):
        """
        Stop the file from playing
        """
        if self._playing:
            self._clock_source.remove_callback(self._callback)
        self._playing = False
        # Empty the queue to allow the thread to quit
        try:
            while not self._queue.empty():
                self._queue.get_nowait()
        except queue.Empty:
            # Don't mind if it's empty, we were just trying stop the thread
            pass

    def _callback(self, source):
        """
        A callback for each tick of the clock source
        :param source:  The source of the callback, unused
        """
        try:
            self.notify_callbacks(self._queue.get_nowait())
        except queue.Empty:
            # Nothing to play
            pass

    def _play_thread(self):
        """
        The loop that plays the sound from start to end, queueing raw PCM blocks
        ready to be sent to callbacks when the clock source ticks
        """
        raw_block = numpy.zeros(0, numpy.int16)
        for block in self._file:
            if not self._playing:
                return
            raw_block = numpy.append(
                raw_block,
                numpy.fromstring(block, dtype=numpy.int16).reshape(-1, self._file.channels)
            )
            while len(raw_block) >= self._blocks and self._playing:
                self._queue.put(raw_block[:self._blocks])
                raw_block = raw_block[self._blocks:]
