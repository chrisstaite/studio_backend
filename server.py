import flask
import flask_restful
import flask_socketio
import subprocess
import sys
import os.path
import functools
import rest
import uuid


class Server(object):

    def __init__(self):
        """
        Construct the Flask instance and configure the REST API
        """
        self._app = flask.Flask(__name__)
        self._app.config['SECRET_KEY'] = str(uuid.uuid4())
        self._socketio = flask_socketio.SocketIO(self._app)
        self._angular = None
        self._setup_rest()
        self._setup_socketio()
        self._setup_angular()

    def _setup_socketio(self):
        """
        Setup the SocketIO event handlers
        """

    def _setup_rest(self):
        """
        Add all of the resources to the server
        """
        api = flask_restful.Api(self._app)
        api.add_resource(rest.audio_output.CreatedOutputs, '/audio/output')
        api.add_resource(rest.audio_output.OutputDevice, '/audio/output/devices')
        api.add_resource(rest.audio_input.InputDevice, '/audio/input')
        api.add_resource(rest.audio_mix.Mixers, '/audio/mixers')
        api.add_resource(rest.audio_mix.MixerInputs, '/audio/mixers/<string:mixer_id>/inputs')
        api.add_resource(rest.audio_mix.MixerInput, '/audio/mixers/<string:mixer_id>/inputs/<string:input_id>')
        api.add_resource(rest.audio_mix.MixerOutput, '/audio/mixers/<string:mixer_id>/output')
        api.add_resource(rest.stream_sink.StreamSink, '/audio/output_stream/<string:name>')

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
        # Run the build and allow it to watch for changes
        self._angular = subprocess.Popen(
            [
                node, ng, 'build',
                '--aot',
                '--base-href', '/frontend/',
                '--watch',
                # '--prod', '--configuration', 'production'
            ],
            cwd=frontend
        )
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
            view_func=functools.partial(flask.redirect, '/frontend/')
        )

    def run(self):
        """
        Start the server running
        """
        self._socketio.run(self._app)
        if self._angular is not None:
            self._angular.kill()
            self._angular = None


if __name__ == "__main__":
    server = Server()
    server.run()
