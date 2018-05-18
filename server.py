import flask
import flask_restful
import rest


class Server(object):

    def __init__(self):
        """
        Construct the Flask instance and configure the REST API
        """
        self._app = flask.Flask(__name__)
        self._setup_rest()

    def _setup_rest(self):
        """
        Add all of the resources to the server
        """
        api = flask_restful.Api(self._app)
        api.add_resource(rest.audio_output.OutputDevice, '/audio/output')
        api.add_resource(rest.audio_input.InputDevice, '/audio/input')
        api.add_resource(rest.audio_mix.Mixers, '/audio/mixers')
        api.add_resource(rest.audio_mix.MixerInputs, '/audio/mixers/<string:mixer_id>/inputs')
        api.add_resource(rest.audio_mix.MixerOutput, '/audio/mixers/<string:mixer_id>/output')

    def start(self):
        """
        Start the server running
        """
        self._app.run()


if __name__ == "__main__":
    server = Server()
    server.start()
