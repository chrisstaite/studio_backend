import lameenc
import numpy
from . import callback


class Mp3(callback.Callback):
    """
    An endpoint for an audio stream that encodes to MP3
    """

    def __init__(self, quality: int = 7, bit_rate: int = 128):
        """
        Create an MP3 encoder for an audio stream
        :param quality:   The quality to produce, 2 - best, 7 - fastest
        :param bit_rate:  The output bit rate (constant bit rate encoding)
        """
        super().__init__()
        self._encoder = None
        self._input = None
        self._quality = quality
        self._bit_rate = bit_rate
        self._channels = None

    def close(self):
        """
        Flush any output
        """
        encoder = self._encoder
        self._channels = None
        self._encoder = None
        if encoder is not None:
            self.notify_callbacks(encoder.flush())

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, source) -> None:
        """
        Set the input for this output
        :param source:  The input to set or None to clear
        """
        if self._input is source:
            return
        if self._input is not None:
            self._input.remove_callback(self._input_callback)
        if self._encoder is not None:
            if source is not None and source.channels != self._channels:
                try:
                    self.notify_callbacks(self._encoder.flush())
                except RuntimeError:
                    # If the encoder hasn't encoded anything, it's fine
                    pass
                self._encoder = None
        self._input = None
        if source is not None:
            if self._encoder is None:
                try:
                    self._encoder = lameenc.Encoder()
                    self._encoder.set_channels(source.channels)
                    self._encoder.set_quality(self._quality)
                    self._encoder.set_bit_rate(self._bit_rate)
                    self._channels = source.channels
                except:
                    self._encoder = None
                    raise
            self._input = source
            self._input.add_callback(self._input_callback)

    def _input_callback(self, _, blocks: numpy.array) -> None:
        """
        Called when a block of samples is available from the input source
        :param blocks:  The input block to write to the output
        """
        encoder = self._encoder
        if encoder is None:
            return
        output = encoder.encode(blocks)
        if len(output) > 0:
            self.notify_callbacks(output)
