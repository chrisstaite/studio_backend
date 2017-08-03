import numpy
import threading
from . import input


class Mixer(input.Input):

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
        self._input_lock.aquire()
        if source in self._inputs:
            self._input_lock.release()
            raise Exception("Unable to add inputs multiple times")
        self._inputs[source] = (source.channels(), False)
        self._input_lock.release()
        source.add_callback(self._input_callback)

    def remove_input(self, source):
        """
        Remove an input from the mixer
        :param source:  The input to remove from the mix
        """
        source.remove_callback(self._input_callback)

    def _map_channels(self, blocks, channels):
        """
        Map the channels in a block to the number of output channels of this mixer
        :param blocks:  The blocks with the number of channels in `channels`
        :param channels:  The number of channels in the block
        :return:  The blocks mapped to the number of channels in this mixer
        """
        separate_channels = blocks.reshape(channels, len(blocks)/channels, order='FORTRAN')
        if self._channels > channels:
            # Mix-up to more channels
            separate_channels = [
                separate_channels[i % len(separate_channels)] for i in range(self._channels)
            ]
            return numpy.ravel(numpy.vstack(separate_channels), order='F')
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
        self._current_sample = numpy.zeros(self._block_size, numpy.float)
        return completed_sample

    def _input_callback(self, source, blocks):
        """
        Take an input block
        :param source:  The input that the block came from
        :param blocks:  The input data from the input
        """
        self._input_lock.aquire()
        try:
            channels, has_input = self._inputs[source]
        except:
            self._input_lock.release()
            raise

        if has_input:
            # A new block for an input, tick the clock
            try:
                completed_sample = self._tick()
                self._inputs = {
                    current_input: (info[0], current_input == source) for current_input, info in self._inputs.items()
                }
            finally:
                self._input_lock.release()
            # Call the callbacks
            self.notify_callbacks(completed_sample)
        else:
            self._input_lock.release()

        if channels != self._channels:
            # Need to re-sample the channels
            blocks = self._map_channels(blocks, channels)

        self._input_lock.aquire()
        try:
            self._current_sample += blocks
        finally:
            self._input_lock.release()
