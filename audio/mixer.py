import numpy
import threading
from . import callback


class Input(object):
    __slots__ = ('channels', 'has_input', 'volume')

    def __init__(self, channels, has_input, volume):
        self.channels = channels
        self.has_input = has_input
        self.volume = volume


class Mixer(callback.Callback):
    """
    A basic mixer that takes inputs and adds them into a single output track
    """

    def __init__(self, block_size, output_channels):
        """
        Create a new mixer that mixes lots of input streams into a single output stream
        :param block_size:  The number of blocks used per sample
        :param output_channels:  The output channels that it is mixed down to (i.e. 1 for mono, 2 for stereo)
        """
        super().__init__()
        self._block_size = block_size * output_channels
        self._channels = output_channels
        self._current_sample = None
        self._inputs = {}
        self._input_lock = threading.Lock()
        # Initialise the current block
        self._tick()

    def add_input(self, source):
        """
        Add an input to the mixer
        :param source:  The input to add to the mix
        """
        self._input_lock.acquire()
        if source in self._inputs:
            self._input_lock.release()
            raise Exception("Unable to add inputs multiple times")
        self._inputs[source] = Input(source.channels(), False, 0.5)
        self._input_lock.release()
        source.add_callback(self._input_callback)

    def remove_input(self, source):
        """
        Remove an input from the mixer
        :param source:  The input to remove from the mix
        """
        source.remove_callback(self._input_callback)
        self._input_lock.acquire()
        del self._inputs[source]
        self._input_lock.release()

    def set_volume(self, source, volume):
        """
        Set the volume of the given source
        :param source:  The source to set the volume of
        :param volume:  A volume to set it to between 0.0 and 2.0
        :raises ValueError:  If volume is not between 0 and 2
        :raises KeyError:  If the source is not in this mixer
        """
        volume = float(volume)
        if volume < 0.0 or volume > 2.0:
            raise ValueError("Volume must be between 0 and 2")
        self._input_lock.acquire()
        self._inputs[source].volume = volume
        self._input_lock.release()

    def _map_channels(self, blocks, channels):
        """
        Map the channels in a block to the number of output channels of this mixer
        :param blocks:  The blocks with the number of channels in `channels`
        :param channels:  The number of channels in the block
        :return:  The blocks mapped to the number of channels in this mixer
        """
        separate_channels = blocks.reshape(channels, len(blocks) // channels)
        if self._channels > channels:
            # Mix-up to more channels
            separate_channels = [
                separate_channels[i % len(separate_channels)] for i in range(self._channels)
            ]
            return numpy.ravel(numpy.vstack(separate_channels))
        else:
            # Mix-down to fewer channels
            scale = self._channels / channels
            output = scale * separate_channels[0]
            for channel in separate_channels[1:]:
                output += scale * channel
            return output.astype(numpy.int16)

    def _tick(self):
        """
        Create a new sample and return the old one
        :return:  The completed input block
        """
        completed_sample = self._current_sample
        self._current_sample = numpy.zeros(self._block_size, numpy.int16)
        return completed_sample

    def _input_callback(self, source, blocks):
        """
        Take an input block
        :param source:  The input that the block came from
        :param blocks:  The input data from the input
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

        if this_input.channels != self._channels:
            # Need to re-sample the channels
            blocks = self._map_channels(blocks, this_input.channels)

        # Set the volume
        blocks = (blocks * this_input.volume).astype(numpy.int16)

        self._input_lock.acquire()
        try:
            self._current_sample += blocks
        finally:
            self._input_lock.release()
