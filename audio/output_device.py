import typing
import sounddevice
import sys
import numpy
import queue
from . import callback


class OutputDevice(callback.Callback):
    """
    A wrapper around an output device which plays samples to external audio hardware
    """

    def __init__(self, name: str, block_size: int):
        """
        Create a new output device
        :param name:  The name of the output device to use
        :param block_size:  The number of blocks to use for each channel
        """
        super().__init__()
        device_details = sounddevice.query_devices(name)
        self._channels = device_details['max_output_channels']
        if self._channels <= 0:
            raise Exception('Not an output device')
        self._stream = sounddevice.OutputStream(
            blocksize=block_size,
            channels=self._channels,
            device=name,
            callback=self._output_callback,
            dtype=numpy.int16,
            latency=device_details['default_low_output_latency']
        )
        self._block_size = self._channels * block_size
        self._input = None
        # We'll drop frames if we're processing slower than this
        self._output_queue = queue.Queue(maxsize=16)
        self._name = name
        self._started = False

    @property
    def name(self) -> str:
        """
        Get the name of the output device
        :return:  The name of the output device
        """
        return self._name

    @property
    def input(self):
        """
        Get the current input source for this output
        :return:  The input source
        """
        return self._input

    @input.setter
    def input(self, source):
        """
        Set the input for this output
        :param source:  The input to set or None to clear
        """
        if self._input is source:
            return
        if self._input is not None:
            self._input.remove_callback(self._input_callback)
        self._input = source
        if self._input is not None:
            if not self._started:
                self._started = True
                self._stream.start()
            self._input.add_callback(self._input_callback)
        elif self._started:
            self._started = False
            self._stream.stop()

    @property
    def channels(self) -> int:
        """
        Get the number of channels
        :return:  The number of channels for this input
        """
        return self._channels

    def _input_callback(self, _, blocks: numpy.array) -> None:
        """
        Called when a block of samples is available from the input source
        :param blocks:  The input block to write to the output
        """
        try:
            self._output_queue.put_nowait(blocks)
        except queue.Full:
            self._output_queue.get_nowait()
            self._output_queue.put_nowait(blocks)

    def _output_callback(self, out_data: numpy.array, frames: int, time: int, status: str) -> None:
        """
        Called every time a block of samples is wanted for the output
        :param out_data:  The list to put the output data into
        :param frames:  The number of blocks to output
        :param time:  The monotonic counter of this output stream
        :param status:  The current status string or None if no error
        """
        if status:
            print(status, file=sys.stderr)
        frames *= self._channels
        data = numpy.zeros(0, numpy.int16)
        try:
            while len(data) < frames:
                data = numpy.append(data, self._output_queue.get_nowait())
        except queue.Empty:
            data = numpy.append(data, numpy.zeros(frames - len(data), numpy.int16))
        out_data[:] = numpy.reshape(data, (-1, self._channels))
        # Notify listeners that a tick has tuck
        self.notify_callbacks()

    @staticmethod
    def devices() -> typing.List[str]:
        """
        List the available output devices
        :return:  A list of device names to pass into the constructor
        """
        devices = sounddevice.query_devices()
        return [device['name'] for device in devices if device['max_output_channels'] > 0]
