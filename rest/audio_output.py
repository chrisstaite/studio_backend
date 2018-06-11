import flask_restful
import flask_restful.reqparse
import audio
import settings
import audio_manager
from . import stream_sink


class OutputDevice(flask_restful.Resource):

    @staticmethod
    def get():
        return audio.output_device.OutputDevice.devices()


class CreatedOutputs(flask_restful.Resource):

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'type', type=str, choices=('device', 'icecast', 'multiplex'),
            help='The type of the output to create', required=True
        )
        self._parser.add_argument(
            'display_name', type=str, help='The name to call this output', required=True
        )
        self._device_parser = flask_restful.reqparse.RequestParser()
        self._device_parser.add_argument(
            'name', type=str, help='The name of the device to output to', required=True
        )
        self._icecast_parser = flask_restful.reqparse.RequestParser()
        self._icecast_parser.add_argument(
            'endpoint', type=str, help='The URL of the Icecast server to connect to', required=True
        )
        self._icecast_parser.add_argument(
            'password', type=str, help='The stream password', required=True
        )
        self._multiplex_parser = flask_restful.reqparse.RequestParser()
        self._multiplex_parser.add_argument(
            'parent_id', type=str, help='The output device to multiplex to', required=True
        )
        self._multiplex_parser.add_argument(
            'channels', type=int, help='The number of channels to split the output into', required=True
        )

    def get(self):
        return self._to_json(audio_manager.output.Outputs.get())

    @staticmethod
    def _to_json(outputs):
        """
        Take a list of Output objects and prepare them for jsonification
        :param outputs:  List of Output instances
        :return:  A list of dictionary objects
        """
        def to_dict(output):
            ret = {
                'id': output.id,
                'display_name': output.display_name
            }
            if isinstance(output.output, audio.output_device.OutputDevice):
                ret['type'] = 'device'
                ret['name'] = output.output.name
            elif isinstance(output.output, audio.icecast.Icecast):
                ret['type'] = 'icecast'
                ret['endpoint'] = output.output.endpoint
            elif isinstance(output.output, audio_manager.output.MultiplexedOutput):
                ret['type'] = 'multiplex'
                ret['parent_id'] = audio_manager.output.Outputs.get_output(output.output.parent).id
            elif isinstance(output.output, stream_sink.Mp3Generator):
                ret['type'] = 'browser'
            return ret
        return [to_dict(output) for output in outputs]

    @staticmethod
    def _create_device(name):
        """
        Create a new output device
        :param name:  The name of the output device to create
        :return:  The newly created output device
        """
        try:
            audio_manager.output.Outputs.get_output_device(name)
            flask_restful.abort(400, message='An output for that device already exists.')
        except ValueError:
            pass
        return audio.output_device.OutputDevice(name, settings.BLOCK_SIZE)

    @staticmethod
    def _create_icecast(endpoint, password):
        """
        Create a new Icecast output device
        :param endpoint:  The Icecast endpoint to connect to
        :param password:  The source password for the Icecast endpoint
        :return:  The newly created output
        """
        try:
            audio_manager.output.Outputs.get_icecast_output(endpoint)
            flask_restful.abort(400, message='An output to that Icecast endpoint already exists.')
        except ValueError:
            pass
        icecast = audio.icecast.Icecast()
        if not icecast.connect(endpoint, password):
            flask_restful.abort(400, message='Unable to connect to Icecast endpoint')
        return icecast

    @staticmethod
    def _create_multiplex(parent_id, channels):
        """
        Create a new multiplex output device
        :param parent_id:     The parent device to output to
        :param channels:      The number of channels for each of the multiplex splits
        :returns:  The newly created outputs
        """
        try:
            parent = audio_manager.output.Outputs.get_output(parent_id)
        except ValueError:
            flask_restful.abort(400, message='Parent output does not exist.')
            raise  # No-op
        if not isinstance(parent.output, audio.output_device.OutputDevice):
            flask_restful.abort(400, message='Parent must be an output device')
        parent_channels = parent.output.channels
        if parent_channels < (channels * 2):
            flask_restful.abort(400, message='Parent device only has {} channels'.format(parent_channels))
        multiplex = audio.multiplex.Multiplex(parent_channels, settings.BLOCK_SIZE)
        parent.output.input = multiplex
        return [
            audio_manager.output.MultiplexedOutput(parent.output, multiplex, channels, i * channels)
            for i in range(parent_channels // channels)
        ]

    def post(self):
        """
        Create a new output device
        :return:  Newly created Output objects
        """
        args = self._parser.parse_args(strict=False)
        type_function = getattr(self, '_create_' + args['type'])
        type_args = getattr(self, '_' + args['type'] + '_parser').parse_args(strict=False)
        output_device = type_function(**type_args)
        outputs = []
        if isinstance(output_device, list):
            i = 1
            for device in output_device:
                output = audio_manager.output.Outputs.add_output(args['display_name'] + ' - ' + str(i), device)
                i += 1
                outputs.append(output)
        else:
            output = audio_manager.output.Outputs.add_output(args['display_name'], output_device)
            outputs.append(output)
        return self._to_json(outputs)


class Output(flask_restful.Resource):

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'display_name', type=str, help='The name to call this output'
        )

    def put(self, output_id):
        try:
            output = audio_manager.output.Outputs.get_output(output_id)
        except ValueError:
            flask_restful.abort(404, message='No such output exists')
            raise  # No-op
        args = self._parser.parse_args(strict=True)
        if 'display_name' in args:
            output.display_name = args['display_name']

    @staticmethod
    def delete(output_id):
        try:
            output = audio_manager.output.Outputs.get_output(output_id)
            audio_manager.output.Outputs.delete_output(output)
        except ValueError:
            flask_restful.abort(404, message='No such output exists')
        except audio_manager.exception.InUseException:
            flask_restful.abort(400, message='Output is in use')
        return True


def setup_api(api):
    """
    Configure the REST endpoints for this namespace
    :param flask_restful.Api api:  The API to add the endpoints to
    """
    api.add_resource(CreatedOutputs, '/audio/output')
    api.add_resource(Output, '/audio/output/<string:output_id>')
    api.add_resource(OutputDevice, '/audio/output/devices')
