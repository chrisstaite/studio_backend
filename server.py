import flask
import flask_restful
import subprocess
import sys
import os.path
import functools
import rest


class Server(object):

    def __init__(self):
        """
        Construct the Flask instance and configure the REST API
        """
        self._app = flask.Flask(__name__)
        self._setup_rest()
        self._setup_angular()

    def _setup_rest(self):
        """
        Add all of the resources to the server
        """
        api = flask_restful.Api(self._app)
        api.add_resource(rest.audio_output.OutputDevice, '/audio/output')
        api.add_resource(rest.audio_input.InputDevice, '/audio/input')
        api.add_resource(rest.audio_mix.Mixers, '/audio/mixers')
        api.add_resource(rest.audio_mix.MixerInputs, '/audio/mixers/<string:mixer_id>/inputs')
        api.add_resource(rest.audio_mix.MixerInput, '/audio/mixers/<string:mixer_id>/inputs/<string:input_id>')
        api.add_resource(rest.audio_mix.MixerOutput, '/audio/mixers/<string:mixer_id>/output')

    def _setup_angular(self):
        """
        Download any Angular modules required, build and add routes
        """
        bin_dir = os.path.dirname(sys.executable)
        npm = os.path.join(bin_dir, 'npm')
        node = os.path.join(bin_dir, 'node')
        frontend = os.path.join(os.path.dirname(__file__), 'frontend')
        ng = os.path.join(frontend, 'node_modules', '.bin', 'ng')
        # Install the required packages
        subprocess.call([npm, 'install'], cwd=frontend)
        # Run the build
        subprocess.call([node, ng, 'build', '--aot'])
        # Serve the built directory
        dist = os.path.join(frontend, 'dist', 'frontend')
        self._app.add_url_rule(
            '/frontend/<path:filename>',
            endpoint='frontend',
            view_func=functools.partial(flask.send_from_directory, dist)
        )
        # Serve the frontend index
        self._app.add_url_rule(
            '/frontend/',
            endpoint='frontend_index',
            view_func=functools.partial(flask.send_from_directory, dist, 'index.html')
        )
        # Redirect home page to the frontend
        self._app.add_url_rule(
            '/',
            endpoint='root',
            view_func=Server._redirect_home
        )

    @staticmethod
    def _redirect_home():
        """
        Handle the homepage
        """
        return flask.redirect('/frontend/')

    def start(self):
        """
        Start the server running
        """
        self._app.run()


if __name__ == "__main__":
    Server().start()
