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
import platform
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
        self._react = None
        with self._app.app_context():
            self._setup_db()
            self._setup_rest()
            self._setup_angular()

    def _setup_db(self):
        """
        Configure the SQLAlchemy databases for use with Flask
        """
        import library
        library.database.init_app(self._app)
        with self._app.app_context():
            library.Library.restore()

    def _setup_rest(self) -> None:
        """
        Add all of the resources to the server
        """
        api = flask_restful.Api(self._app)
        import rest
        rest.audio_output.setup_api(api)
        rest.audio_input.setup_api(api)
        rest.stream_sink.setup_api(api)
        rest.audio_mix.setup_api(api)
        rest.library.setup_api(api)
        rest.live_player.setup_api(api)

    def _setup_angular(self) -> None:
        """
        Download any Angular modules required, build and add routes
        """
        bin_dir = os.path.dirname(sys.executable)
        if 'windows' in platform.platform().lower():
            npm_bin = 'npm.cmd'
            npx_bin = 'npx.cmd'
            node_bin = 'node.exe'
        else:
            npm_bin = 'npm'
            npx_bin = 'npx'
            node_bin = 'node'
        npm = os.path.join(bin_dir, npm_bin)
        npx = os.path.join(bin_dir, npx_bin)
        node = os.path.join(bin_dir, node_bin)
        # Configure the react frontend
        react = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'react')
        # Install the react dependencies
        new_env = os.environ.copy()
        new_env['PATH'] = bin_dir + os.pathsep + os.environ['PATH']
        subprocess.call([npm, 'config', 'set', 'cafile', certifi.where()], env=new_env)
        subprocess.call([npm, 'install'], cwd=react, env=new_env)
        babel_run = [
            npx, 'webpack',
            '--watch',
            '--config', 'webpack.config.js',
        ]
        if getattr(settings, 'FRONTEND_DEBUG', False):
            new_env['DEV'] = 'true'
        self._react = subprocess.Popen(babel_run, cwd=react, env=new_env)
        # Serve the react frontend
        self._app.add_url_rule(
            '/react/<path:filename>',
            endpoint='react',
            view_func=functools.partial(flask.send_from_directory, react)
        )
        self._app.add_url_rule(
            '/react/',
            endpoint='react_index',
            view_func=functools.partial(flask.send_from_directory, react, 'index.html')
        )
        # Redirect home page to the frontend
        self._app.add_url_rule(
            '/',
            endpoint='root',
            view_func=functools.partial(flask.redirect, '/react/')
        )

    def run(self) -> None:
        """
        Start the server running
        """
        self._socketio.run(self._app)
        if self._angular is not None:
            self._angular.kill()
            self._angular = None
        if self._react is not None:
            self._react.kill()
            self._react = None


if __name__ == "__main__":
    Server().run()
