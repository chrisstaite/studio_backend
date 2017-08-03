import sounddevice
import sys
from . import input


class InputDevice(input.Input):

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
        self._stream = sounddevice.RawInputStream(
            blocksize=block_size,
            channels=self._channels,
            device=name,
            callback=self._callback
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
        self.notify_callbacks(in_data)

    @staticmethod
    def devices():
        """
        List the available input devices
        :return:  A list of device names to pass into the constructor
        """
        device_list = []
        for device in sounddevice.query_devices():
            if device['max_input_channels'] > 0:
                device_list.append(device['name'])
        return device_list
