import werkzeug.exceptions
import flask_restful
import flask_restful.reqparse
import audio
import uuid
import collections
import settings


class OutputDevice(flask_restful.Resource):

    def get(self):
        return audio.output_device.OutputDevice.devices()


class MultiplexedOutput(object):

    def __init__(self, parent, multiplex, channels, offset):
        self._parent = parent
        self._multiplex = multiplex
        self._channels = channels
        self._offset = offset
        self._source = None

    @property
    def channels(self):
        return self._channels

    @property
    def parent(self):
        return self._parent

    @property
    def input(self):
        return self._source

    @input.setter
    def input(self, source):
        """
        Set the input for this output
        :param source:  The source to set as the input
        """
        if source is self._source:
            return
        if self._source is not None:
            self._multiplex.remove_input(self._source)
            self._source = None
        self._multiplex.add_input(source, self._offset)
        self._source = source


class CreatedOutputs(flask_restful.Resource):

    Output = collections.namedtuple('Output', ['id', 'display_name', 'output'])
    _outputs = []

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
        return self._to_json(self._outputs)

    def _to_json(self, outputs):
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
            elif isinstance(output.output, MultiplexedOutput):
                ret['type'] = 'multiplex'
                ret['parent_id'] = next(x.id for x in self._outputs if x.output is output.output.parent)
            else:
                ret['type'] = 'browser'
            return ret
        return [to_dict(output) for output in outputs]

    def _create_device(self, name):
        """
        Create a new output device
        :param name:  The name of the output device to create
        :return:  The newly created output device
        """
        if any(isinstance(output.output, audio.output_device.OutputDevice) and output.output.name == name
                for output in self._outputs):
            raise werkzeug.exceptions.BadRequest('An output of that name already exists.')
        return audio.output_device.OutputDevice(name, settings.BLOCK_SIZE)

    def _create_icecast(self, endpoint, password):
        """
        Create a new Icecast output device
        :param endpoint:  The Icecast endpoint to connect to
        :param password:  The source password for the Icecast endpoint
        :return:  The newly created output
        """
        if any(isinstance(output.output, audio.icecast.Icecast) and output.output.endpoint == endpoint
                for output in self._outputs):
            raise werkzeug.exceptions.BadRequest('An output to that Icecast endpoint already exists.')
        icecast = audio.icecast.Icecast()
        if not icecast.connect(endpoint, password):
            raise werkzeug.exceptions.BadRequest('Unable to connect to Icecast endpoint')
        return icecast

    def _create_multiplex(self, parent_id, channels):
        """
        Create a new multiplex output device
        :param parent_id:     The parent device to output to
        :param channels:      The number of channels for each of the multiplex splits
        :returns:  The newly created outputs
        """
        try:
            parent = self.get_output(parent_id)
        except werkzeug.exceptions.NotFound:
            raise werkzeug.exceptions.BadRequest('Parent output does not exist.')
        if not isinstance(parent.output, audio.output_device.OutputDevice):
            raise werkzeug.exceptions.BadRequest('Parent must be an output device')
        parent_channels = parent.output.channels
        if parent_channels < (channels * 2):
            raise werkzeug.exceptions.BadRequest('Parent device only has {} channels'.format(parent_channels))
        multiplex = audio.multiplex.Multiplex(parent_channels, settings.BLOCK_SIZE)
        parent.output.input = multiplex
        return [
            MultiplexedOutput(parent.output, multiplex, channels, i * channels)
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
                output = self.add_output(args['display_name'] + ' - ' + str(i), device)
                i += 1
                outputs.append(output)
        else:
            output = self.add_output(args['display_name'], output_device)
            outputs.append(output)
        return self._to_json(outputs)

    @classmethod
    def add_output(cls, display_name, output):
        output = cls.Output(str(uuid.uuid4()), display_name, output)
        cls._outputs.append(output)
        return output

    @classmethod
    def get_output(cls, output):
        """
        Get the Output class for the given output
        :param output:  The output or output ID
        :return:  The found Output instance
        :raises werkzeug.exceptions.NotFound:  The device is not found
        """
        try:
            return next(x for x in cls._outputs if x.output is output or x.id == output)
        except StopIteration:
            raise werkzeug.exceptions.NotFound('No such device found')

    @classmethod
    def delete_output(cls, output):
        """
        Delete an output
        :param output:  The output to delete
        :raises werkzeug.exceptions.BadRequest:  The output is in use
        :raises werkzeug.exceptions.NotFound:  The output doesn't exist
        """
        if output.output.input is not None:
            raise werkzeug.exceptions.BadRequest('Output in use')
        try:
            cls._outputs.remove(output)
        except ValueError:
            raise werkzeug.exceptions.NotFound('No such device found')
        # If all the multiplexers are removed, then remove the multiplex device
        if isinstance(output.output, MultiplexedOutput):
            if not any(x.output.parent == output.output.parent
                       for x in cls._outputs if isinstance(x.output, MultiplexedOutput)):
                output.output.parent.input = None


class Output(flask_restful.Resource):

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'display_name', type=str, help='The name to call this output'
        )

    def put(self, output_id):
        output = CreatedOutputs.get_output(output_id)
        args = self._parser.parse_args(strict=True)
        if 'display_name' in args:
            output.display_name = args['display_name']

    def delete(self, output_id):
        output = CreatedOutputs.get_output(output_id)
        CreatedOutputs.delete_output(output)
        return True
