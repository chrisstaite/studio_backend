import collections
import uuid
import audio
from . import exception


class Inputs(object):

    Input = collections.namedtuple('Input', ['id', 'display_name', 'input'])
    _inputs = []

    @classmethod
    def get(cls):
        return cls._inputs

    @classmethod
    def add_input(cls, display_name, input):
        output = cls.Input(str(uuid.uuid4()), display_name, input)
        cls._inputs.append(output)
        return output

    @classmethod
    def get_input(cls, input):
        """
        Get the Input class for the given input
        :param input:  The input or input ID
        :return:  The found Input instance
        :raises ValueError:  The device is not found
        """
        try:
            return next(x for x in cls._inputs if x.input is input or x.id == input)
        except StopIteration:
            raise ValueError('No such device found')

    @classmethod
    def get_input_device(cls, name):
        """
        Get the Input class for the given output device
        :param name:  The device name of the input device
        :return:  The found Input instance
        :raises ValueError:  The device is not found
        """
        try:
            return next(x for x in cls._inputs
                        if isinstance(x.input, audio.input_device.InputDevice) and
                        x.input.name == name)
        except StopIteration:
            raise ValueError('No such device found')

    @classmethod
    def delete_input(cls, input_):
        """
        Delete an input
        :param input_:  The Input instance to delete
        :raises InUseException:  The output is in use
        :raises ValueError:  The output doesn't exist
        """
        if input_.input.has_callbacks():
            raise exception.InUseException('Input has current outputs')
        cls._inputs.remove(input_)
