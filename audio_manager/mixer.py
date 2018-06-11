import audio
import settings
import collections
import uuid
from . import exception


class Channel(object):
    """
    A channel for a mixer that can have an input assigned to it
    """

    def __init__(self, mixer):
        """
        Create a channel for a given mixer
        :param audio.mixer.Mixer mixer:  The mixer to create the channel for
        """
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
    def input(self, source):
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
            self._source = None
            self._mixer.set_volume(source, self._volume)

    @property
    def volume(self):
        """
        Get the current volume for this channel
        :return:  The volume of this channel
        """
        return self._volume

    @volume.setter
    def volume(self, volume):
        """
        Set the volume for this channel
        :param volume:  The volume to set
        """
        if self._source is not None:
            self._mixer.set_volume(self._source, volume)
        self._volume = volume


class Mixer(object):
    """
    A wrapper around a mixer to handle it in channels rather than inputs
    """

    def __init__(self, channels):
        """
        Create a new mixer
        :param channels:  The number of output channels of the mixer (i.e. 2 for stereo)
        """
        self._mixer = audio.mixer.Mixer(settings.BLOCK_SIZE, channels)
        self._channels = []

    @property
    def channels(self):
        """
        Get the number of output channels for this mixer
        :return:  The number of output channels
        """
        return self._mixer.channels

    def get_channel(self, index):
        """
        Get the mixer channel
        :param index:  The channel number to get (0-indexed)
        :returns:  The Channel instance for the given channel
        :raises IndexError:  That channel doesn't exist
        """
        return self._channels[index]

    def get_channel_index(self, channel):
        """
        Get the channel index for a given channel
        :param channel:  The Channel instance to get the index of
        :return:  The index of the channel
        :raises ValueError:  That Channel instance isn't part of this Mixer
        """
        return self._channels.index(channel)

    def get_channel_count(self):
        """
        Get the number of mixer
        :return:  The number of channels
        """
        return len(self._channels)

    def add_channel(self):
        """
        Add a new channel to the mixer
        :return:  The new Channel instance
        """
        new_channel = Channel(self._mixer)
        self._channels.append(new_channel)
        return new_channel

    def remove_channel(self, index):
        """
        Remove a channel from the mixer
        :param index:  The channel to remove (0-indexed)
        """
        self._channels[index].input = None
        del self._channels[index]

    def has_callbacks(self):
        """
        Whether the mixer has any outputs sourcing from it
        :return:  True if there is anything this mixer is feeding to, False otherwise
        """
        return self._mixer.has_callbacks()

    def add_callback(self, callback):
        """
        Add a given callback to the sub-mixer
        :param callback:  The callback to add
        """
        self._mixer.add_callback(callback)

    def remove_callback(self, callback):
        """
        Remove a given callback from the sub-mixer
        :param callback:  The callback to remove
        """
        self._mixer.remove_callback(callback)


class Mixers(object):
    """
    A list of the mixers
    """

    Mixer = collections.namedtuple('Mixer', ['id', 'display_name', 'mixer'])
    _mixers = []

    @classmethod
    def get(cls):
        return cls._mixers

    @classmethod
    def add_mixer(cls, display_name, channels):
        """
        Create a new Mixer instance
        :param display_name:  The name of the new mixer
        :param channels:  The number of output channels
        :return:  The newly created Mixers.Mixer instance
        """
        mixer = Mixer(channels)
        mixer = cls.Mixer(str(uuid.uuid4()), display_name, mixer)
        cls._mixers.append(mixer)
        return mixer

    @classmethod
    def get_mixer(cls, mixer):
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
    def delete_mixer(cls, mixer):
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
