import typing
import uuid
import audio
import settings
from . import exception
from . import persist


class Input(object):

    __slots__ = ('_id', '_display_name', '_input')

    def __init__(self, id_, display_name, input_):
        self._id = id_
        self._display_name = display_name
        self._input = input_

    @property
    def id(self):
        return self._id

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        self._display_name = display_name
        session = persist.Session()
        entity = session.query(persist.Input).get(self.id)
        entity.display_name = display_name
        session.commit()
        session.close()

    @property
    def input(self):
        return self._input


class Inputs(object):
    """
    A list of the created inputs in this process
    """

    _inputs = []

    @classmethod
    def get(cls) -> typing.List[Input]:
        """
        Get the current inputs
        :return:  The list of inputs
        """
        return cls._inputs

    @classmethod
    def add_input(cls, display_name: str, input_) -> Input:
        """
        Add a new input
        :param display_name:  The name for the input
        :param input_:  The input to add
        :return:  The newly created input instance
        """
        input_ = Input(str(uuid.uuid4()), display_name, input_)
        cls._inputs.append(input_)
        session = persist.Session()
        session.add(persist.Input(
            id=input_.id,
            display_name=display_name,
            type=persist.InputTypes.device,
            parameters=input_.input.name
        ))
        session.commit()
        session.close()
        return input_

    @classmethod
    def get_input(cls, input_: typing.Union[typing.Any, str]) -> Input:
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
    def get_input_device(cls, name: str) -> Input:
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
    def delete_input(cls, input_: Input) -> None:
        """
        Delete an input
        :param input_:  The Input instance to delete
        :raises InUseException:  The output is in use
        :raises ValueError:  The output doesn't exist
        """
        if input_.input.has_callbacks():
            raise exception.InUseException('Input has current outputs')
        cls._inputs.remove(input_)
        session = persist.Session()
        session.query(persist.Input).filter_by(id=input_.id).delete()
        session.commit()
        session.close()

    @classmethod
    def restore(cls):
        """
        Restore the inputs from the database
        """
        session = persist.Session()
        for sql_input in session.query(persist.Input).all():
            input_object = None
            if sql_input.type == persist.InputTypes.device:
                input_object = audio.input_device.InputDevice(sql_input.parameters, settings.BLOCK_SIZE)
            input_ = Input(sql_input.id, sql_input.display_name, input_object)
            cls._inputs.append(input_)
        session.close()


def get_input(input_id: str):
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
    from . import mixer
    # Look for another mixer next
    return mixer.Mixers.get_mixer(input_id).mixer
    # TODO: Add a playlist source lookup


def get_input_id(input_) -> str:
    """
    Get an input ID for a given input
    :param input_:  The input to find the ID for
    :return:  The ID for the given input or '' if the input was None
    :raises ValueError:  No such input found
    """
    # An empty ID means set it to nothing
    if input_ is None:
        return ''
    # Look for a device input first
    try:
        return Inputs.get_input(input_).id
    except ValueError:
        pass
    from . import mixer
    # Look for another mixer next
    return mixer.Mixers.get_mixer(input_).id
    # TODO: Add a playlist source lookup
