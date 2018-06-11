import flask_restful
import flask_restful.reqparse
import audio
import settings
import audio_manager


class InputDevice(flask_restful.Resource):

    @staticmethod
    def get():
        return audio.input_device.InputDevice.devices()


class CreatedInputs(flask_restful.Resource):

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'type', type=str, choices=('device', ),
            help='The type of the input to create', required=True
        )
        self._parser.add_argument(
            'display_name', type=str, help='The name to call this input', required=True
        )
        self._device_parser = flask_restful.reqparse.RequestParser()
        self._device_parser.add_argument(
            'name', type=str, help='The name of the device to input from', required=True
        )

    def get(self):
        return self._to_json(audio_manager.input.Inputs.get())

    @staticmethod
    def _to_json(inputs):
        """
        Take a list of Input objects and prepare them for jsonification
        :param inputs:  List of Input instances
        :return:  A list of dictionary objects
        """
        def to_dict(input_):
            ret = {
                'id': input_.id,
                'display_name': input_.display_name
            }
            if isinstance(input_.input, audio.input_device.InputDevice):
                ret['type'] = 'device'
                ret['name'] = input_.input.name
            return ret
        return [to_dict(input_) for input_ in inputs]

    @staticmethod
    def _create_device(name):
        """
        Create a new output device
        :param name:  The name of the output device to create
        :return:  The newly created output device
        """
        try:
            audio_manager.input.Inputs.get_input_device(name)
            flask_restful.abort(400, message='An input for that device already exists.')
        except ValueError:
            pass
        return audio.input_device.InputDevice(name, settings.BLOCK_SIZE)

    def post(self):
        """
        Create a new input device
        :return:  Newly created Input objects
        """
        args = self._parser.parse_args(strict=False)
        type_function = getattr(self, '_create_' + args['type'])
        type_args = getattr(self, '_' + args['type'] + '_parser').parse_args(strict=False)
        input_device = type_function(**type_args)
        inputs = [audio_manager.input.Inputs.add_input(args['display_name'], input_device)]
        return self._to_json(inputs)


class Input(flask_restful.Resource):

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'display_name', type=str, help='The name to call this output'
        )

    def put(self, input_id):
        try:
            input_ = audio_manager.input.Inputs.get_input(input_id)
        except ValueError:
            flask_restful.abort(404, message='No such input exists')
            raise  # No-op
        args = self._parser.parse_args(strict=True)
        if 'display_name' in args:
            input_.display_name = args['display_name']

    @staticmethod
    def delete(input_id):
        try:
            input_ = audio_manager.input.Inputs.get_input(input_id)
            audio_manager.input.Inputs.delete_input(input_)
        except ValueError:
            flask_restful.abort(404, message='No such input exists')
        except audio_manager.exception.InUseException:
            flask_restful.abort(400, message='Input is in use')
        return True


def setup_api(api):
    """
    Configure the REST endpoints for this namespace
    :param flask_restful.Api api:  The API to add the endpoints to
    """
    api.add_resource(CreatedInputs, '/audio/input')
    api.add_resource(Input, '/audio/input/<string:input_id>')
    api.add_resource(InputDevice, '/audio/input/devices')
