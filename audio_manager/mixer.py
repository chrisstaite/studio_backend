import typing
import audio
import settings
import uuid
import numpy
from . import exception
from . import persist


class Channel(object):
    """
    A channel for a mixer that can have an input assigned to it
    """

    def __init__(self, channel_id: str, mixer: audio.mixer.Mixer):
        """
        Create a channel for a given mixer
        :param channel_id:  The ID of this channel for persistence
        :param mixer:  The mixer to create the channel for
        """
        self._channel_id = channel_id
        self._mixer = mixer
        self._volume = 1.0
        self._source = None

    @property
    def input(self):
        """
        Get the current input source for this channel
        :return:  The current input source
        """
        return self._source

    @input.setter
    def input(self, source) -> None:
        """
        Set the input source for this channel
        :param source:  The new input source
        """
        if self._source is source:
            return
        if self._source is not None:
            self._mixer.remove_input(self._source)
            self._source = None
        if source is not None:
            self._mixer.add_input(source)
            self._source = source
            self._mixer.set_volume(source, self._volume)
        from . import input
        session = persist.Session()
        channel = session.query(persist.MixerChannel).filter_by(id=self._channel_id).one()
        channel.input = input.get_input_id(source)
        session.commit()
        session.close()

    @property
    def volume(self) -> float:
        """
        Get the current volume for this channel
        :return:  The volume of this channel
        """
        return self._volume

    @volume.setter
    def volume(self, volume: float) -> None:
        """
        Set the volume for this channel
        :param volume:  The volume to set
        """
        if not isinstance(volume, float):
            raise ValueError('Volume must be a float')
        if self._source is not None:
            self._mixer.set_volume(self._source, volume)
        self._volume = volume
        session = persist.Session()
        channel = session.query(persist.MixerChannel).filter_by(id=self._channel_id).one()
        channel.volume = volume
        session.commit()
        session.close()


class ChannelMixer(object):
    """
    A wrapper around a mixer to handle it in channels rather than inputs
    """

    def __init__(self, mixer_id: str, channels: int):
        """
        Create a new mixer
        :param mixer_id:  The ID of the mixer used for persistence of the channels
        :param channels:  The number of output channels of the mixer (i.e. 2 for stereo)
        """
        self._mixer_id = mixer_id
        self._mixer = audio.mixer.Mixer(settings.BLOCK_SIZE, channels)
        self._channels = {}

    @property
    def channels(self) -> int:
        """
        Get the number of output channels for this mixer
        :return:  The number of output channels
        """
        return self._mixer.channels

    def get_channel(self, id_: str) -> Channel:
        """
        Get the mixer channel
        :param id_:  The ID of the channel
        :returns:  The Channel instance for the given channel
        :raises IndexError:  That channel doesn't exist
        """
        return self._channels[id_]

    def get_channel_ids(self) -> typing.Iterable[str]:
        """
        Get the IDs of all the channels
        :return:  The channels IDs for the channels
        """
        return self._channels.keys()

    def get_channel_id(self, channel: Channel) -> str:
        """
        Get the ID of the given channel
        :param channel:  The Channel instance to get the ID of
        :return:  The ID of the channel
        :raises ValueError:  That Channel instance isn't part of this Mixer
        """
        try:
            return next(key for key, value in self._channels.items() if value is channel)
        except StopIteration:
            raise ValueError('Channel not found in the mixer')

    def add_channel(self) -> str:
        """
        Add a new channel to the mixer
        :return:  The new channel ID
        """
        id_ = str(uuid.uuid4())
        new_channel = Channel(id_, self._mixer)
        self._channels[id_] = new_channel
        session = persist.Session()
        session.add(persist.MixerChannel(id=id_, mixer=self._mixer_id, input='', volume=1.0))
        session.commit()
        session.close()
        return id_

    def remove_channel(self, channel_id: str) -> None:
        """
        Remove a channel from the mixer
        :param channel_id:  The ID of the channel to remove
        :raises KeyError:  The channel doesn't exist
        """
        self._channels[channel_id].input = None
        del self._channels[channel_id]
        session = persist.Session()
        session.query(persist.MixerChannel).filter_by(id=channel_id).delete()
        session.commit()
        session.close()

    def has_callbacks(self) -> bool:
        """
        Whether the mixer has any outputs sourcing from it
        :return:  True if there is anything this mixer is feeding to, False otherwise
        """
        return self._mixer.has_callbacks()

    def add_callback(self, callback: typing.Callable[[numpy.array], None]) -> None:
        """
        Add a given callback to the sub-mixer
        :param callback:  The callback to add
        """
        self._mixer.add_callback(callback)

    def remove_callback(self, callback: typing.Callable[[numpy.array], None]) -> None:
        """
        Remove a given callback from the sub-mixer
        :param callback:  The callback to remove
        """
        self._mixer.remove_callback(callback)

    def restore(self, channels: typing.Iterable[persist.MixerChannel]):
        """
        Restore mixer channels from the database
        :param channels:  The channels to set for this mixer
        """
        from . import input
        for channel in channels:
            new_channel = Channel(channel.id, self._mixer)
            self._channels[channel.id] = new_channel
            new_channel.volume = channel.volume
            new_channel.input = input.get_input(channel.input)


class Mixer(object):

    __slots__ = ('id', 'display_name', 'mixer')

    def __init__(self, id_, display_name, mixer):
        self.id = id_
        self.display_name = display_name
        self.mixer = mixer


class Mixers(object):
    """
    A list of the created mixers
    """

    _mixers = []

    @classmethod
    def get(cls) -> typing.List[Mixer]:
        return cls._mixers

    @classmethod
    def add_mixer(cls, display_name: str, channels: int) -> Mixer:
        """
        Create a new Mixer instance
        :param display_name:  The name of the new mixer
        :param channels:  The number of output channels
        :return:  The newly created Mixers.Mixer instance
        """
        id_ = str(uuid.uuid4())
        mixer = ChannelMixer(id_, channels)
        mixer = Mixer(id_, display_name, mixer)
        cls._mixers.append(mixer)
        session = persist.Session()
        sql_mixer = persist.Mixer(id=mixer.id, display_name=display_name, output_channels=channels)
        session.add(sql_mixer)
        session.commit()
        session.close()
        return mixer

    @classmethod
    def get_mixer(cls, mixer: typing.Union[ChannelMixer, str]) -> Mixer:
        """
        Get the Mixers.Mixer class for the given mixer
        :param mixer:  The mixer or mixer ID
        :return:  The found Mixers.Mixer instance
        :raises ValueError:  The mixer is not found
        """
        try:
            return next(x for x in cls._mixers if x.mixer is mixer or x.id == mixer)
        except StopIteration:
            raise ValueError('No such mixer found')

    @classmethod
    def delete_mixer(cls, mixer: Mixer) -> None:
        """
        Delete a mixer
        :param mixer:  The Mixers.Mixer instance to delete
        :raises InUseException:  The mixer output is in use
        :raises ValueError:  The output doesn't exist
        """
        if mixer.mixer.has_callbacks():
            raise exception.InUseException('Input has current outputs')
        for i in range(mixer.mixer.get_channel_count()):
            mixer.mixer.get_channel(i).input = None
        cls._mixers.remove(mixer)
        session = persist.Session()
        session.query(persist.Mixer).filter_by(id=mixer.id).delete()
        session.query(persist.MixerChannel).filter_by(mixer=mixer.id).delete()
        session.commit()
        session.close()

    @classmethod
    def restore(cls):
        """
        Restore the mixers in the persistence database
        """
        session = persist.Session()
        for sql_mixer in session.query(persist.Mixer).all():
            mixer = ChannelMixer(sql_mixer.id, sql_mixer.output_channels)
            mixer = Mixer(sql_mixer.id, sql_mixer.display_name, mixer)
            cls._mixers.append(mixer)
        for mixer in cls._mixers:
            mixer.mixer.restore(session.query(persist.MixerChannel).filter_by(mixer=mixer.id))
        session.close()


Mixers.restore()
