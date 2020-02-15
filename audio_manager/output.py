import typing
import uuid
import audio
import settings
import json
from . import exception
from . import persist


class MultiplexedOutput(object):
    """
    A class that wraps a multiplexer to allow each split in the multiplex to be managed as an output instance
    """

    def __init__(self,
                 parent: audio.output_device.OutputDevice,
                 multiplex: audio.multiplex.Multiplex,
                 channels: int,
                 offset: int):
        """
        Create a new wrapper around a multiplexer for managing a part of the multiplex as a single output
        :param parent:  The output that the multiplexer outputs to
        :param multiplex:  The multiplexer to use
        :param channels:  The number of channels for this multiplexer output
        :param offset:  The offset into the multiplexer that this instance is to manage
        """
        self._parent = parent
        self._multiplex = multiplex
        self._channels = channels
        self._offset = offset
        self._source = None

    @property
    def channels(self) -> int:
        """
        Get the number of channels that are managed by this instance
        :return:  The number of channels
        """
        return self._channels

    @property
    def offset(self) -> int:
        """
        Get the offset into the multiplexer that this represents
        :return:  The offset into the multiplexer
        """
        return self._offset

    @property
    def parent(self) -> audio.output_device.OutputDevice:
        """
        Get the output device that the multiplexer outputs to
        :return:  The output device
        """
        return self._parent

    @property
    def multiplex(self) -> audio.multiplex.Multiplex:
        """
        Get the multiplexer that this output is using
        :return:  The multiplexer
        """
        return self._multiplex

    @property
    def input(self):
        """
        Get the current input source for this multiplex
        :return:  The current input
        """
        return self._source

    @input.setter
    def input(self, source) -> None:
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


class Output(object):
    """
    A wrapper around an output for the ID and display name
    """

    __slots__ = ('_id', '_display_name', '_output')

    def __init__(self, id_, display_name, output):
        self._id = id_
        self._display_name = display_name
        self._output = output

    @property
    def id(self):
        """
        Get the UUID for this output
        :return:  The UUID of this output
        """
        return self._id

    @property
    def output(self):
        """
        Get the underlying output, should not be used to set the input
        :return:  The underlying output
        """
        return self._output

    @property
    def display_name(self):
        """
        Get the display name for this output
        :return:  The display name of this output
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """
        Set the display name for this output
        :param display_name:  The display name to set
        """
        self._display_name = display_name
        session = persist.Session()
        entity = session.query(persist.Output).get(self._id)
        entity.display_name = display_name
        session.commit()
        session.close()

    @property
    def input(self):
        """
        Get the ID of the input
        :return:  The ID of the input for this output
        """
        from . import input
        return input.get_input_id(self._output.input)

    @input.setter
    def input(self, input_id):
        """
        Set the input to the given ID
        :param input_id:  The ID of the input to use
        :raises ValueError:  If the input_id is not valid
        :raises InUseException:  If the output is multiplexed
        """
        if isinstance(self._output.input, MultiplexedOutput):
            raise exception.InUseException()
        if input_id is None:
            input_id = ''
        from . import input
        self._output.input = input.get_input(input_id)
        session = persist.Session()
        entity = session.query(persist.Output).get(self._id)
        entity.input = input_id
        session.commit()
        session.close()


class Outputs(object):
    """
    A static manager for the created outputs for this process
    """

    _outputs = []

    @classmethod
    def get(cls) -> typing.List[Output]:
        """
        Get the list of outputs
        :return:  The list of registered outputs
        """
        return cls._outputs

    @classmethod
    def add_output(cls, display_name: str, output) -> Output:
        """
        Add an output
        :param display_name:  The name of the output to add
        :param output:  The output instance to add
        :return:  The newly wrapped output object
        """
        from . import input
        output = Output(str(uuid.uuid4()), display_name, output)
        cls._outputs.append(output)
        type_ = None
        parameters = None
        if isinstance(output.output, audio.output_device.OutputDevice):
            type_ = persist.OutputTypes.device
            parameters = output.output.name
        elif isinstance(output.output, audio.icecast.Icecast):
            type_ = persist.OutputTypes.icecast
            parameters = json.dumps({
                'endpoint': output.output.endpoint,
                'password': output.output.password
            })
        elif isinstance(output.output, MultiplexedOutput):
            type_ = persist.OutputTypes.multiplex
            parameters = json.dumps({
                'parent': cls.get_output_device(output.output.parent.name).id,
                'channels': output.output.channels,
                'offset': output.output.offset
            })
        elif isinstance(output.output, audio.output_file.RollingFile):
            type_ = persist.OutputTypes.file
            parameters = output.output.base_path
        if type_ is not None:
            session = persist.Session()
            session.add(persist.Output(
                id=output.id,
                display_name=display_name,
                type=type_,
                input=input.get_input_id(output.output.input),
                parameters=parameters
            ))
            session.commit()
            session.close()
        return output

    @classmethod
    def get_output(cls, output: typing.Union[str,
                                             audio.output_device.OutputDevice,
                                             audio.icecast.Icecast,
                                             audio.mp3.Mp3]) -> Output:
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
    def get_output_device(cls, name: str) -> Output:
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
    def get_output_file(cls, path: str) -> Output:
        """
        Get the Output class for the given output file
        :param path:  The base path for the output file
        :return:  The found Output instance
        :raises ValueError:  The device is not found
        """
        try:
            return next(x for x in cls._outputs
                        if isinstance(x.output, audio.output_file.RollingFile) and
                        x.output.base_path == path)
        except StopIteration:
            raise ValueError('No such device found')

    @classmethod
    def get_icecast_output(cls, endpoint: str) -> Output:
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
    def delete_output(cls, output: Output) -> None:
        """
        Delete an output
        :param output:  The output to delete
        :raises InUseException:  The output is in use
        :raises ValueError:  The output doesn't exist
        """
        if output.output.input is not None:
            raise exception.InUseException('Output in use')
        cls._outputs.remove(output)
        session = persist.Session()
        session.query(persist.Output).filter_by(id=output.id).delete()
        session.commit()
        session.close()
        # If all the multiplexers are removed, then remove the multiplex device
        if isinstance(output.output, MultiplexedOutput):
            if not any(x.output.parent == output.output.parent
                       for x in cls._outputs if isinstance(x.output, MultiplexedOutput)):
                output.output.parent.input = None

    @classmethod
    def restore(cls):
        """
        Restore the outputs from the database
        """
        session = persist.Session()
        for sql_input in session.query(persist.Output).filter_by(type=persist.OutputTypes.device).all():
            output_object = audio.output_device.OutputDevice(sql_input.parameters, settings.BLOCK_SIZE)
            output = Output(sql_input.id, sql_input.display_name, output_object)
            cls._outputs.append(output)
        for sql_input in session.query(persist.Output).filter_by(type=persist.OutputTypes.icecast).all():
            output_object = audio.icecast.Icecast()
            parameters = json.loads(sql_input.parameters)
            output_object.connect(parameters['endpoint'], parameters['password'])
            output = Output(sql_input.id, sql_input.display_name, output_object)
            cls._outputs.append(output)
        for sql_input in session.query(persist.Output).filter_by(type=persist.OutputTypes.multiplex).all():
            parameters = json.loads(sql_input.parameters)
            parent = cls.get_output(parameters['parent']).output
            multiplex = None
            for other_output in cls._outputs:
                if isinstance(other_output.output, MultiplexedOutput) and other_output.output.parent is parent:
                    multiplex = other_output.output.multiplex
            if multiplex is None:
                multiplex = audio.multiplex.Multiplex(parent.channels, settings.BLOCK_SIZE)
                parent.input = multiplex
            output_object = MultiplexedOutput(parent, multiplex, parameters['channels'], parameters['offset'])
            output = Output(sql_input.id, sql_input.display_name, output_object)
            cls._outputs.append(output)
        for sql_input in session.query(persist.Output).filter_by(type=persist.OutputTypes.file).all():
            output_object = audio.output_file.RollingFile(sql_input.parameters)
            output = Output(sql_input.id, sql_input.display_name, output_object)
            cls._outputs.append(output)
        session.close()

    @classmethod
    def restore_inputs(cls):
        """
        Restore the inputs to the outputs from the database.
        For some reason, this has to be done in two stages because if this is imported after Mixer then we
        get an assertion in the PyAudio core.
        """
        session = persist.Session()
        for output in cls._outputs:
            output.input = session.query(persist.Output).get(output.id).input
        session.close()
