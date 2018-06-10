import collections
import uuid
import audio
from . import exception


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


class Outputs(object):

    Output = collections.namedtuple('Output', ['id', 'display_name', 'output'])
    _outputs = []

    @classmethod
    def get(cls):
        return cls._outputs

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
        :raises ValueError:  The device is not found
        """
        try:
            return next(x for x in cls._outputs if x.output is output or x.id == output)
        except StopIteration:
            raise ValueError('No such device found')

    @classmethod
    def get_output_device(cls, name):
        """
        Get the Output class for the given output device
        :param name:  The device name of the output device
        :return:  The found Output instance
        :raises ValueError:  The device is not found
        """
        try:
            return next(x for x in cls._outputs
                        if isinstance(x.output, audio.output_device.OutputDevice) and
                        x.output.name == name)
        except StopIteration:
            raise ValueError('No such device found')

    @classmethod
    def get_icecast_output(cls, endpoint):
        """
        Get the Output class for the given Icecast endpoint
        :param endpoint:  The endpoint of the Icecast output
        :return:  The found Output instance
        :raises ValueError:  The device is not found
        """
        try:
            return next(x for x in cls._outputs
                        if isinstance(x.output, audio.icecast.Icecast) and
                        x.output.endpoint == endpoint)
        except StopIteration:
            raise ValueError('No such device found')

    @classmethod
    def delete_output(cls, output):
        """
        Delete an output
        :param output:  The output to delete
        :raises InUseException:  The output is in use
        :raises ValueError:  The output doesn't exist
        """
        if output.output.input is not None:
            raise exception.InUseException('Output in use')
        cls._outputs.remove(output)
        # If all the multiplexers are removed, then remove the multiplex device
        if isinstance(output.output, MultiplexedOutput):
            if not any(x.output.parent == output.output.parent
                       for x in cls._outputs if isinstance(x.output, MultiplexedOutput)):
                output.output.parent.input = None
