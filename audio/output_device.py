import sounddevice
import sys
import numpy
import queue


class OutputDevice(object):

    def __init__(self, name, block_size):
        """
        Create a new output device
        :param name:  The name of the output device to use
        :param block_size:  The number of blocks to use for each channel
        """
        device_details = sounddevice.query_devices(name)
        self._channels = device_details['max_output_channels']
        if self._channels <= 0:
            raise Exception('Not an output device')
        self._stream = sounddevice.RawOutputStream(
            blocksize=block_size,
            channels=self._channels,
            device=name,
            callback=self._output_callback
        )
        self._input = None
        self._block_size = self._channels * block_size
        # We'll drop frames if we're processing slower than this
        self._output_queue = queue.Queue(maxsize=16)

    def set_input(self, source):
        """
        Set the input for this output
        :param source:  The input to set or None to clear
        """
        if self._input == source:
            return
        if self._input is not None:
            self._input.remove_callback(self._input_callback)
        self._input = source
        if self._input is not None:
            self._input.add_callback(self._input_callback)

    def channels(self):
        """
        Get the number of channels
        :return:  The number of channels for this input
        """
        return self._channels

    def __enter__(self):
        self._stream.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stream.stop()

    def _input_callback(self, source, blocks):
        """
        Called when a block of samples is available from the input source
        :param source:  The source that the input came from
        :param blocks:  The input block to write to the output
        """
        try:
            self._output_queue.put_nowait(blocks)
        except queue.Full:
            print("Dropping output buffer as it is full", file=sys.stderr)
            self._output_queue.get_nowait()
            self._output_queue.put_nowait(blocks)

    def _output_callback(self, out_data, frames, time, status):
        """
        Called every time a block of samples is wanted for the output
        :param out_data:  The list to put the output data into
        :param frames:  The number of blocks to output
        :param time:  The monotonic counter of this output stream
        :param status:  The current status string or None if no error
        """
        if status:
            print(status, file=sys.stderr)
        try:
            data = self._output_queue.get_nowait()
        except queue.Empty:
            print("Buffer underflow, padding with empty", file=sys.stderr)
            data = numpy.zeros(self._block_size, numpy.float)
        if len(out_data) > len(data):
            out_data[:len(data)] = data
            out_data[len(data):] = b'\x00' * (len(out_data) - len(data))
        else:
            out_data[:] = data

    @staticmethod
    def devices():
        """
        List the available output devices
        :return:  A list of device names to pass into the constructor
        """
        device_list = []
        for device in sounddevice.query_devices():
            if device['max_output_channels'] > 0:
                device_list.append(device['name'])
        return device_list
