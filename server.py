import eventlet
eventlet.monkey_patch()
import flask
import flask_restful
import flask_socketio
import subprocess
import sys
import os
import os.path
import functools
import rest
import uuid
import settings
import certifi


class Server(object):
    """
    A class managing the server configuration and running
    """

    def __init__(self):
        """
        Construct the Flask instance and configure the REST API
        """
        self._app = flask.Flask(__name__)
        self._app.config['SECRET_KEY'] = str(uuid.uuid4())
        self._socketio = flask_socketio.SocketIO(self._app, async_mode='eventlet')
        self._angular = None
        self._setup_rest()
        self._setup_socketio()
        self._setup_angular()

    def _setup_socketio(self) -> None:
        """
        Setup the SocketIO event handlers
        """

    def _setup_rest(self) -> None:
        """
        Add all of the resources to the server
        """
        api = flask_restful.Api(self._app)
        rest.audio_output.setup_api(api)
        rest.audio_input.setup_api(api)
        rest.stream_sink.setup_api(api)
        rest.audio_mix.setup_api(api)
        rest.library.setup_api(api)

    def _setup_angular(self) -> None:
        """
        Download any Angular modules required, build and add routes
        """
        bin_dir = os.path.dirname(sys.executable)
        npm = os.path.join(bin_dir, 'npm')
        node = os.path.join(bin_dir, 'node')
        frontend = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'frontend')
        ng = os.path.join(frontend, 'node_modules', '.bin', 'ng')
        # Install the required packages
        new_env = os.environ.copy()
        new_env['PATH'] = bin_dir + os.pathsep + os.environ['PATH']
        subprocess.call([npm, 'config', 'set', 'cafile', certifi.where()], env=new_env)
        subprocess.call([npm, 'install'], cwd=frontend, env=new_env)
        # Run the build and allow it to watch for changes
        node_builder = [
            node, ng, 'build',
            '--aot',
            '--base-href', '/frontend/',
            '--watch'
        ]
        if not getattr(settings, 'FRONTEND_DEBUG', False):
            node_builder += ['--prod', '--configuration', 'production']
        self._angular = subprocess.Popen(node_builder, cwd=frontend, env=new_env)
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

    def run(self) -> None:
        """
        Start the server running
        """
        self._socketio.run(self._app)
        if self._angular is not None:
            self._angular.kill()
            self._angular = None


if __name__ == "__main__":
    Server().run()
