import audioread
import threading
import numpy
import time
from . import callback


class File(callback.Callback):
    """
    A wrapper around an audio file that allows it to be played as an input
    """

    def __init__(self, path, blocks):
        """
        Open an audio file ready to play it
        :param path:  The path to the file to play
        :param blocks:  The number of blocks to read at a time per channel
        """
        super().__init__()
        self._file = audioread.audio_open(path)
        self._blocks_sent = 0
        self._blocks = blocks * self._file.channels
        self._playing = False
        self._time = 0.0
        self._end_callback = None

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
        threading.Thread(target=self._play_thread, daemon=True).start()

    def time(self):
        """
        Get the number of seconds into the track we have played
        :return:  The number of seconds played as a float
        """
        return self._time

    def length(self):
        """
        Get the number of seconds the track is long
        :return:  The number of seconds in the track as a float
        """
        return self._file.duration

    def stop(self):
        """
        Stop the file from playing
        """
        self._playing = False

    def set_end_callback(self, end_callback):
        """
        Set a callback for when the file finishes playing
        :param end_callback:  The callback to call
        """
        self._end_callback = end_callback

    def _play_thread(self):
        """
        The loop that plays the sound from start to end, queueing raw PCM blocks
        ready to be sent to callbacks when the clock source ticks
        """
        raw_block = numpy.zeros(0, numpy.int16)
        # In order to know when to sleep until we need to know when we started
        start_time = time.time()
        # This is how many blocks we should have passed per second
        blocks_per_second = self._file.samplerate * self._file.channels
        # Calculate the starting time
        start_time -= self._blocks_sent / blocks_per_second
        for block in self._file:
            # Add the newly read blocks to the existing ones,
            # sorting out the interlacing of the channels
            raw_block = numpy.append(
                raw_block,
                numpy.fromstring(block, dtype=numpy.int16).reshape(-1, self._file.channels)
            )
            while len(raw_block) >= self._blocks and self._playing:
                # Add the number of blocks we're about to pass to find out when we should
                self._blocks_sent += self._blocks
                # Re-calculate the time we should be at
                self._time = self._blocks_sent / blocks_per_second
                # Find the difference between the time we should be at and the current time
                sleep_time = self._time - (time.time() - start_time)
                # If there is a difference and it's in the future, wait for then
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.notify_callbacks(raw_block[:self._blocks])
                raw_block = raw_block[self._blocks:]
            if not self._playing:
                break
        self._playing = False
        if self._end_callback is not None:
            self._end_callback()
