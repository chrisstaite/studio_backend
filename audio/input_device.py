import sounddevice
import sys
import numpy
from . import callback


class InputDevice(callback.Callback):
    """
    A wrapper around audio input hardware to allow it to be played into the system
    """

    def __init__(self, name, block_size):
        """
        Create a new input device
        :param name:  The name of the input device to use
        :param block_size:  The size of each sample block
        """
        super().__init__()
        device_details = sounddevice.query_devices(name)
        self._channels = device_details['max_input_channels']
        if self._channels <= 0:
            raise Exception('Not an input device')
        self._stream = sounddevice.InputStream(
            blocksize=block_size,
            channels=self._channels,
            device=name,
            callback=self._callback,
            dtype=numpy.int16
        )
        self._last_frames = None
        self._last_time = None

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

    def _callback(self, in_data, frames, time, status):
        """
        Called every time a block of samples is available from the input source
        :param in_data:  The block of samples
        :param frames:  The number of captured frames
        :param time:  The monotonic counter of this input stream
        :param status:  The current status string or None if no error
        """
        if status:
            print(status, file=sys.stderr)
        self._last_frames = frames
        self._last_time = time
        self.notify_callbacks(in_data.reshape(in_data.shape[0] * in_data.shape[1]))

    @staticmethod
    def devices():
        """
        List the available input devices
        :return:  A list of device names to pass into the constructor
        """
        devices = sounddevice.query_devices()
        return [device['name'] for device in devices if device['max_input_channels'] > 0]
