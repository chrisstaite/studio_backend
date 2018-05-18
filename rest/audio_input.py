import flask_restful
import audio
import settings


class Device(object):
    __slots__ = ('_ref_count', '_device')

    def __init__(self, name):
        self._ref_count = 1
        self._device = audio.input_device.InputDevice(name, settings.BLOCK_SIZE)
        self._device.start()

    def reference(self):
        self._ref_count += 1
        return self._device

    def dereference(self):
        self._ref_count -= 1
        if self._ref_count == 0:
            self._device.start()


class InputDevice(flask_restful.Resource):

    _inputs = {}

    def get(self):
        return audio.input_device.InputDevice.devices()

    @staticmethod
    def start_input(name):
        if name in InputDevice._inputs:
            return InputDevice._inputs[name].reference()
        device = Device(name)
        InputDevice._inputs[name] = device
        return device

    @staticmethod
    def stop_input(name):
        if name in InputDevice._inputs:
            InputDevice._inputs[name].dereference()
