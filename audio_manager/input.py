import collections
import uuid
import audio
from . import exception
from . import mixer


class Inputs(object):

    Input = collections.namedtuple('Input', ['id', 'display_name', 'input'])
    _inputs = []

    @classmethod
    def get(cls):
        return cls._inputs

    @classmethod
    def add_input(cls, display_name, input_):
        input_ = cls.Input(str(uuid.uuid4()), display_name, input_)
        cls._inputs.append(input_)
        return input_

    @classmethod
    def get_input(cls, input_):
        """
        Get the Input class for the given input
        :param input_:  The input or input ID
        :return:  The found Input instance
        :raises ValueError:  The device is not found
        """
        try:
            return next(x for x in cls._inputs if x.input is input_ or x.id == input_)
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


def get_input(input_id):
    """
    Get an input for a given input ID
    :param input_id:  The ID of the input to find
    :return:  The input for the given ID or None if the input_id was empty
    :raises ValueError:  No such input found
    """
    # An empty ID means set it to nothing
    if input_id == '':
        return None
    # Look for a device input first
    try:
        return Inputs.get_input(input_id).input
    except ValueError:
        pass
    # Look for another mixer next
    return mixer.Mixers.get_mixer(input_id).mixer
    # TODO: Add a playlist source lookup
