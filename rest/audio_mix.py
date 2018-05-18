import flask_restful
import flask_restful.reqparse
import uuid
import audio
import settings
import os.path
from . import audio_input


class LiveInput(object):
    """
    A wrapper around a live input for a mixer
    """

    def __init__(self, name):
        self._input = audio_input.InputDevice.start_input(name)
        self._name = name

    def name(self):
        return self._name

    def remove(self):
        audio_input.InputDevice.stop_input(self._name)

    def device(self):
        return self._input


class FileInput(object):
    """
    A wrapper around a recorded input for a mixer
    """

    def __init__(self, filename):
        self._input = audio.file.File(filename, settings.BLOCK_SIZE)
        self._name = os.path.basename(filename)
        self._input.play()

    def name(self):
        return self._name

    def remove(self):
        self._input.stop()

    def device(self):
        return self._input


class Mixer(object):
    """
    A wrapper around the audio mixer to track objects against their UUIDs
    """

    def __init__(self, *args, **kwargs):
        self._mixer = audio.mixer.Mixer(*args, **kwargs)
        self._inputs = {}
        self._output = None

    def inputs(self):
        """
        Get a list of the current inputs
        :return:  A dictionary of the input ID to the input name
        """
        return {
            input_id: input_device.name() for input_id, input_device in self._inputs
        }

    def output(self):
        """
        Get the current output
        :return:  The name of the output
        """
        return "" if self._output is None else self._output[0]

    def set_output(self, name):
        """
        Set the output for this mixer
        :param name:  The output to set
        """
        if self._output is not None:
            self._output[1].set_input(None)
            self._output[1].stop()
            self._output = None
        if name is not None:
            output = audio.output_device.OutputDevice(name, settings.BLOCK_SIZE)
            self._output[1].start()
            output.set_input(self._mixer)
            self._output = (name, output)

    def add_live_input(self, name):
        """
        Add a live device input to the mixer
        :param name:  The name of the live device to add
        :returns:  The ID for the input on the mixer
        """
        return self._add_input(LiveInput(name))

    def add_file_input(self, filename):
        """
        Add a live device input to the mixer
        :param filename:  The path to the file to open and play
        :returns:  The ID for the input on the mixer
        """
        return self._add_input(FileInput(filename))

    def _add_input(self, input_device):
        """
        Add an input device to the mixer
        :param input_device:  The input device to add
        :return:  The ID for the input on the mixer
        """
        input_id = uuid.uuid4()
        self._mixer.add_input(input_device.device())
        self._inputs[input_id] = input_device
        return input_id

    def remove_input(self, input_id):
        """
        Remove a given input from the mixer
        :param input_id:  The ID returned by add_input when added
        """
        if input_id not in self._inputs:
            flask_restful.abort(404, message='Input with ID {} does not exist for mixer'.format(input_id))
        input_device = self._inputs[input_id]
        self._mixer.remove_input(input_device)
        del self._inputs[input_id]
        input_device.remove()


class Mixers(flask_restful.Resource):

    _mixers = {}

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'channels', type=int, default=2, help='The number of output channels for the mixer'
        )

    @classmethod
    def get_mixer(cls, mixer_id):
        if mixer_id not in cls._mixers:
            flask_restful.abort(404, message='Mixer with ID {} does not exist'.format(mixer_id))
        return cls._mixers[mixer_id]

    def get(self):
        return list(Mixers._mixers.keys())

    def post(self):
        args = self._parser.parse_args()
        mixer_id = uuid.uuid4()
        Mixers._mixers[mixer_id] = Mixer(
            settings.BLOCK_SIZE, args['channels']
        )
        return mixer_id


class MixerInputs(flask_restful.Resource):

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'name', type=str, help='Name of the input to add to the mixer'
        )

    def get(self, mixer_id):
        mixer = Mixers.get_mixer(mixer_id)
        return mixer.inputs()

    def post(self, mixer_id):
        mixer = Mixers.get_mixer(mixer_id)
        args = self._parser.parse_args()
        return mixer.add_live_input(args['name'])


class MixerOutput(flask_restful.Resource):

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'name', type=str, help='Name of the output to add to the mixer'
        )

    def get(self, mixer_id):
        mixer = Mixers.get_mixer(mixer_id)
        return mixer.output()

    def post(self, mixer_id):
        mixer = Mixers.get_mixer(mixer_id)
        args = self._parser.parse_args()
        mixer.set_output(args['name'])
