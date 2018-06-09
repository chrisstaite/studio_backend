import numpy
import threading
from . import callback


class Input(object):
    __slots__ = ('start_channel', 'channels', 'has_input')

    def __init__(self, start_channel, channels, has_input):
        self.start_channel = start_channel
        self.channels = channels
        self.has_input = has_input


class Multiplex(callback.Callback):
    """
    A multiplexer that takes in multiple inputs and maps them to a multi-channel output
    """

    def __init__(self, channels, block_size):
        """
        Construct a new multiplexer
        :param channels:  The number of output channels
        :param block_size:  The number of blocks used per sample
        """
        super().__init__()
        self._block_size = block_size
        self._channels = channels
        self._current_sample = None
        self._input_lock = threading.Lock()
        self._inputs = {}
        # Initialise the current block
        self._tick()

    @property
    def channels(self):
        """
        Get the number of output channels for this multiplexer
        :return:  The number of output channels
        """
        return self._channels

    def add_input(self, source, start_channel):
        """
        Add an input to the multiplexer
        :param source:  The device to input from
        :param start_channel:  The channel to play the input to on the output
        """
        channels = source.channels
        if start_channel < 0 or start_channel + channels >= self._channels:
            raise Exception("Start channel out of the range for the output device")
        for input_device in self._inputs.values():
            in_start = input_device.start_channel
            in_end = input_device.start_channel + input_device.channels
            if in_start <= start_channel < in_end or \
                    in_start < start_channel + channels <= in_end:
                raise Exception("Input already mapped to those channels")
        self._input_lock.acquire()
        if source in self._inputs:
            self._input_lock.release()
            raise Exception("Unable to add inputs multiple times")
        self._inputs[source] = Input(start_channel, channels, False)
        self._input_lock.release()
        source.add_callback(self._input_callback)

    def remove_input(self, source):
        """
        Remove an input from the multiplexer
        :param source:  The input to remove
        """
        source.remove_callback(self._input_callback)
        self._input_lock.acquire()
        del self._inputs[source]
        self._input_lock.release()

    def _tick(self):
        """
        Create a new sample and return the old one
        :return:  The completed input block
        """
        completed_sample = self._current_sample
        self._current_sample = numpy.zeros(self._block_size * self._channels, numpy.int16)
        return completed_sample

    def _get_input(self, source):
        """
        Get the Input instance for the given source, calling _tick if we've seen it before
        :param source:  The source to get the input for
        :return:  The Input instance
        :raises KeyError:  If the source is not mapped for this multiplexer
        """
        self._input_lock.acquire()
        try:
            this_input = self._inputs[source]
        except KeyError:
            self._input_lock.release()
            raise

        if this_input.has_input:
            # A new block for an input, tick the clock
            try:
                completed_sample = self._tick()
                for current_input, info in self._inputs.items():
                    info.has_input = current_input is source
            finally:
                self._input_lock.release()
            # Call the callbacks
            self.notify_callbacks(completed_sample)
        else:
            this_input.has_input = True
            self._input_lock.release()

        return this_input

    def _input_callback(self, source, blocks):
        """
        Take an input block
        :param source:  The input that the block came from
        :param blocks:  The input data from the input
        """
        this_input = self._get_input(source)

        self._input_lock.acquire()
        try:
            for i in range(this_input.channels):
                self._current_sample[this_input.start_channel+i::self._channels] = blocks[i::this_input.channels]
        finally:
            self._input_lock.release()
