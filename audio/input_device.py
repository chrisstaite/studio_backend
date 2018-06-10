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
        self._name = name
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
        self._started = False

    def add_callback(self, cb):
        """
        Add a callback to this input device
        :param cb:  The callback to add
        """
        super().add_callback(cb)
        self._check_state()

    def remove_callback(self, cb):
        """
        Remove a callback from this input device
        :param cb:  The callback to remove
        """
        super().add_callback(cb)
        self._check_state()

    def _check_state(self):
        """
        Check that we are started or stopped if we need to
        """
        required_state = self.has_callbacks()
        if required_state != self._started:
            if required_state:
                self._stream.start()
            else:
                self._stream.stop()
            self._started = required_state

    @property
    def name(self):
        """
        Get the name of the input device
        :return:  The input device name
        """
        return self._name

    @property
    def channels(self):
        """
        Get the number of channels
        :return:  The number of channels for this input
        """
        return self._channels

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
        self.notify_callbacks(numpy.ravel(in_data))

    @staticmethod
    def devices():
        """
        List the available input devices
        :return:  A list of device names to pass into the constructor
        """
        devices = sounddevice.query_devices()
        return [device['name'] for device in devices if device['max_input_channels'] > 0]
