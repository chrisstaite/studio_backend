import typing
import flask_restful
import flask_restful.reqparse
import audio_manager


class CreatedMixers(flask_restful.Resource):
    """
    Handler for creating mixers and getting a list of current mixers
    """

    def __init__(self):
        """
        Create the argument parser for creating new mixers
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'display_name', type=str, required=True, help='The name of the new mixer'
        )
        self._parser.add_argument(
            'channels', type=int, default=2, help='The number of output channels for the mixer'
        )

    @staticmethod
    def _to_json(mixers: typing.Iterable[audio_manager.mixer.Mixers.Mixer]) -> typing.List[typing.Dict]:
        """
        Take a list of Mixer objects and prepare them for jsonification
        :param mixers:  List of Mixer instances
        :return:  A list of dictionary objects
        """
        def to_dict(mixer):
            ret = {
                'id': mixer.id,
                'display_name': mixer.display_name,
                'output_channels': mixer.mixer.channels,
                'channel_count': mixer.mixer.get_channel_count()
            }
            return ret
        return [to_dict(mixer) for mixer in mixers]

    def get(self) -> typing.List[typing.Dict]:
        """
        Get a list of the Mixers
        :return:  A list of the current Mixer instances
        """
        return self._to_json(audio_manager.mixer.Mixers.get())

    def post(self) -> typing.List[typing.Dict]:
        """
        Create a new mixer
        :return:  The new mixer object
        """
        args = self._parser.parse_args(strict=True)
        mixers = [audio_manager.mixer.Mixers.add_mixer(args['display_name'], args['channels'])]
        return self._to_json(mixers)


class Mixer(flask_restful.Resource):
    """
    Handler for updating a mixers' attributes and deleting it
    """

    def __init__(self):
        """
        Create the parser for updating the mixer
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'display_name', type=str, help='The name to call this mixer'
        )

    @staticmethod
    def _get_mixer(mixer_id: str) -> audio_manager.mixer.Mixers.Mixer:
        try:
            return audio_manager.mixer.Mixers.get_mixer(mixer_id)
        except ValueError:
            flask_restful.abort(404, message='No such mixer exists')
            raise  # No-op

    @staticmethod
    def _dict_channel(channel: audio_manager.mixer.Channel):
        return {
            'volume': channel.volume,
            'input': audio_manager.input.get_input_id(channel.input)
        }

    def get(self, mixer_id: str) -> typing.Dict:
        mixer = self._get_mixer(mixer_id)
        return {
            'id': mixer.id,
            'display_name': mixer.display_name,
            'output_channels': mixer.mixer.channels,
            'channels': [
                self._dict_channel(mixer.mixer.get_channel(i)) for i in range(mixer.mixer.get_channel_count())
            ]
        }

    def put(self, mixer_id: str) -> bool:
        """
        Update a mixers' attributes
        :param mixer_id:  The mixer ID to update
        :return:  Always True, aborts if there is an error
        """
        mixer = self._get_mixer(mixer_id)
        args = self._parser.parse_args(strict=True)
        if args['display_name'] is not None:
            mixer.display_name = args['display_name']
        return True

    def delete(self, mixer_id: str) -> bool:
        """
        Delete the mixer
        :param mixer_id:  The ID of the mixer to delete
        :return:  Always True, aborts on error
        """
        mixer = self._get_mixer(mixer_id)
        try:
            audio_manager.mixer.Mixers.delete_mixer(mixer)
        except ValueError:
            flask_restful.abort(404, message='Mixer was already deleted')
        except audio_manager.exception.InUseException:
            flask_restful.abort(400, message='Mixer is in use')
        return True


class NewMixerChannel(flask_restful.Resource):
    """
    A handler for creating a channel for a mixer
    """

    @staticmethod
    def post(mixer_id: str) -> int:
        """
        Create a new channel for a mixer
        :param mixer_id:  The ID of the mixer to add the channel to
        :return:  The channel number of the new channel
        """
        try:
            mixer = audio_manager.mixer.Mixers.get_mixer(mixer_id)
            channel = mixer.mixer.add_channel()
            return mixer.mixer.get_channel_index(channel)
        except ValueError:
            flask_restful.abort(404, message='No such mixer exists')
        except audio_manager.exception.InUseException:
            flask_restful.abort(400, message='Mixer is in use')


class MixerChannel(flask_restful.Resource):
    """
    A handle to update and remove a given channel for a mixer
    """

    def __init__(self):
        """
        Create the parser for a channel update
        """
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'input', type=str, help='The ID of the input to set to the channel'
        )
        self._parser.add_argument(
            'volume', type=float, help='The volume to set the channel to'
        )

    @staticmethod
    def _get_mixer(mixer_id: str) -> audio_manager.mixer.Mixers.Mixer:
        """
        Get the mixer by its ID
        :param mixer_id:  The ID of the mixer
        :return:  The mixer
        """
        try:
            return audio_manager.mixer.Mixers.get_mixer(mixer_id)
        except ValueError:
            flask_restful.abort(404, message='No such mixer exists')

    def put(self, mixer_id: str, index: int) -> bool:
        """
        Update the mixer channels' attributes
        :param mixer_id:  The ID of the mixer
        :param index:  The index of the channel in the mixer
        :return:  Always True, aborts on error
        """
        mixer = self._get_mixer(mixer_id)
        try:
            channel = mixer.mixer.get_channel(index)
        except IndexError:
            flask_restful.abort(404, message='Channel does not exist on the mixer')
            raise  # No-op
        args = self._parser.parse_args(strict=True)
        if args['volume'] is not None:
            channel.volume = args['volume']
        if args['input'] is not None:
            try:
                new_input = audio_manager.input.get_input(args['input'])
            except ValueError:
                flask_restful.abort(400, message='Input with the given ID does not exist')
                raise  # No-op
            for i in range(mixer.mixer.get_channel_count()):
                if index != i and mixer.mixer.get_channel(i).input is new_input:
                    flask_restful.abort(400, message='Source already assigned to a channel of this mixer')
            channel.input = new_input
        return True

    @classmethod
    def delete(cls, mixer_id: str, index: int) -> bool:
        """
        Delete a channel from a mixer
        :param mixer_id:  The ID of the mixer
        :param index:  The index of the channel to remove
        :return:  Always True, aborts on error
        """
        mixer = cls._get_mixer(mixer_id)
        try:
            mixer.mixer.remove_channel(index)
        except IndexError:
            flask_restful.abort(404, message='Unknown channel for mixer')
        return True


def setup_api(api: flask_restful.Api) -> None:
    """
    Configure the REST endpoints for this namespace
    :param flask_restful.Api api:  The API to add the endpoints to
    """
    api.add_resource(CreatedMixers, '/audio/mixer')
    api.add_resource(Mixer, '/audio/mixer/<string:mixer_id>')
    api.add_resource(NewMixerChannel, '/audio/mixer/<string:mixer_id>/channel')
    api.add_resource(MixerChannel, '/audio/mixer/<string:mixer_id>/channel/<int:index>')
