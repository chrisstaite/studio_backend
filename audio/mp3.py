import lameenc
from . import callback


class Mp3(callback.Callback):
    """
    An endpoint for an audio stream that encodes to MP3
    """

    def __init__(self, quality=7, bit_rate=128):
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

    def set_input(self, source):
        """
        Set the input for this output
        :param source:  The input to set or None to clear
        """
        if self._input is source:
            return
        if self._input is not None:
            self._input.remove_callback(self._input_callback)
        if self._encoder is not None:
            self.notify_callbacks(self._encoder.flush())
            self._encoder = None
        self._input = None
        if source is not None:
            try:
                self._encoder = lameenc.Encoder()
                self._encoder.set_channels(source.channels())
                self._encoder.set_quality(self._quality)
                self._encoder.set_bit_rate(self._bit_rate)
            except:
                self._encoder = None
                raise
            self._input = source
            self._input.add_callback(self._input_callback)

    def _input_callback(self, source, blocks):
        """
        Called when a block of samples is available from the input source
        :param source:  The source that the input came from
        :param blocks:  The input block to write to the output
        """
        output = self._encoder.encode(blocks)
        if len(output) > 0:
            self.notify_callbacks(output)
