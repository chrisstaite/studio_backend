import flask_restful
import flask_restful.reqparse
import audio_manager


class CreatedMixers(flask_restful.Resource):

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'display_name', type=str, required=True, help='The name of the new mixer'
        )
        self._parser.add_argument(
            'channels', type=int, default=2, help='The number of output channels for the mixer'
        )

    @staticmethod
    def _to_json(mixers):
        """
        Take a list of Mixer objects and prepare them for jsonification
        :param mixers:  List of Mixer instances
        :return:  A list of dictionary objects
        """
        def to_dict(mixer):
            ret = {
                'id': mixer.id,
                'display_name': mixer.display_name,
                'channels': mixer.mixer.get_channel_count()
            }
            return ret
        return [to_dict(mixer) for mixer in mixers]

    def get(self):
        """
        Get a list of the Mixers
        :return:  A list of the current Mixer instances
        """
        return self._to_json(audio_manager.mixer.Mixers.get())

    def post(self):
        """
        Create a new mixer
        :return:  The new mixer object
        """
        args = self._parser.parse_args(strict=True)
        inputs = [audio_manager.mixer.Mixers.add_mixer(args['display_name'], args['channels'])]
        return self._to_json(inputs)


class Mixer(flask_restful.Resource):

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'display_name', type=str, help='The name to call this mixer'
        )

    def put(self, mixer_id):
        try:
            mixer = audio_manager.mixer.Mixers.get_mixer(mixer_id)
        except ValueError:
            flask_restful.abort(404, message='No such mixer exists')
            raise  # No-op
        args = self._parser.parse_args(strict=True)
        if 'display_name' in args:
            mixer.display_name = args['display_name']

    @staticmethod
    def delete(mixer_id):
        try:
            mixer = audio_manager.mixer.Mixers.get_mixer(mixer_id)
            audio_manager.mixer.Mixers.delete_mixer(mixer)
        except ValueError:
            flask_restful.abort(404, message='No such mixer exists')
        except audio_manager.exception.InUseException:
            flask_restful.abort(400, message='Mixer is in use')
        return True


class NewMixerChannel(flask_restful.Resource):

    @staticmethod
    def post(mixer_id):
        try:
            mixer = audio_manager.mixer.Mixers.get_mixer(mixer_id)
            channel = mixer.mixer.add_channel()
            return mixer.mixer.get_channel_index(channel)
        except ValueError:
            flask_restful.abort(404, message='No such mixer exists')
        except audio_manager.exception.InUseException:
            flask_restful.abort(400, message='Mixer is in use')


class MixerChannel(flask_restful.Resource):

    def __init__(self):
        self._parser = flask_restful.reqparse.RequestParser()
        self._parser.add_argument(
            'input', type=str, help='The ID of the input to set to the channel'
        )
        self._parser.add_argument(
            'volume', type=float, help='The volume to set the channel to'
        )

    @staticmethod
    def _get_mixer(mixer_id):
        try:
            return audio_manager.mixer.Mixers.get_mixer(mixer_id)
        except ValueError:
            flask_restful.abort(404, message='No such mixer exists')

    @staticmethod
    def _get_input(input_id):
        """
        Get an input for a given input ID
        :param input_id:  The ID of the input to find
        :return:  The input for the given ID
        """
        # An empty ID means set it to nothing
        if input_id == '':
            return None
        # Look for a device input first
        try:
            return audio_manager.input.Inputs.get_input(input_id).input
        except ValueError:
            pass
        # Look for another mixer next
        try:
            audio_manager.mixer.Mixers.get_mixer(input_id).mixer
        except ValueError:
            flask_restful.abort(400, message='Input with the given ID does not exist')
        # TODO: Add a playlist source lookup

    def put(self, mixer_id, index):
        mixer = self._get_mixer(mixer_id)
        try:
            channel = mixer.mixer.get_channel(index)
        except IndexError:
            flask_restful.abort(404, message='Channel does not exist on the mixer')
            raise  # No-op
        args = self._parser.parse_args(strict=True)
        if 'volume' in args:
            channel.volume = args['volume']
        if 'input' in args:
            new_input = self._get_input(args['input'])
            for i in range(mixer.mixer.get_channel_count()):
                if index != i and mixer.mixer.get_channel(i).input is new_input:
                    flask_restful.abort(400, message='Source already assigned to a channel of this mixer')
            channel.input = new_input

    @classmethod
    def delete(cls, mixer_id, index):
        mixer = cls._get_mixer(mixer_id)
        mixer.mixer.remove_channel(index)
        return True


def setup_api(api):
    """
    Configure the REST endpoints for this namespace
    :param flask_restful.Api api:  The API to add the endpoints to
    """
    api.add_resource(CreatedMixers, '/audio/mixer')
    api.add_resource(Mixer, '/audio/mixer/<string:mixer_id>')
    api.add_resource(NewMixerChannel, '/audio/mixer/<string:mixer_id>/channel')
    api.add_resource(MixerChannel, '/audio/mixer/<string:mixer_id>/channel/<int:index>')
