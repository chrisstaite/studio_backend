import flask
import flask_socketio
import os
import socket
import eventlet.greenio
import audio
import audio_manager


class AudioSession(object):
    """
    A browser audio session for input and output for a unique SocketIO
    session
    """

    # The maximum number of bytes to read at a time
    BLOCK_SIZE = 1024

    def __init__(self, sid):
        """
        Create a new browser audio session
        :param sid:  The SocketIO ID for the session
        """
        self._sid = sid
        self._output = None
        self._socketio = flask.current_app.extensions['socketio']
        self._output_pipe_r, self._output_pipe_w = None, None

    def _send_queue(self):
        """
        The thread that sends data to the web socket
        """
        while True:
            output = self._output_pipe_r.read(AudioSession.BLOCK_SIZE)
            if len(output) == 0:
                break
            self._socketio.emit(
                'output', output, namespace='/audio', room=self._sid
            )
        self._output_pipe_r.close()

    @property
    def input(self):
        """
        Get the current input
        :return:  The current input
        """
        return self._output.input

    @input.setter
    def input(self, source):
        """
        Set the input source for this output
        :param source:  The input source to set
        """
        self._output.input = source

    def _emit_output(self, _, blocks):
        """
        The handler for the output of the MP3
        :param blocks:  The data produced (the MP3)
        """
        self._output_pipe_w.write(blocks)

    def on_disconnect(self):
        """
        Clean up any outputs that may be emitting to the closed socket
        """
        if self._output is not None:
            self._remove_output()
            self._output = None

    def _remove_output(self):
        """
        Remove the output, shutting down its write threads
        """
        self._output.input = None
        self._output.remove_callback(self._emit_output)
        self._output_pipe_w.close()
        output = audio_manager.output.Outputs.get_output(self._output)
        audio_manager.output.Outputs.delete_output(output)
        self._socketio.emit('output_remove', {'id': output.id})

    def _create_pipe(self):
        """
        Create a pipe to talk between the input and the output we
        need to use a pipe because the input is on a native audio
        thread (probably) and the output is on an eventlet thread.
        """
        try:
            r, w = os.pipe()
            self._output_pipe_w = eventlet.greenio.GreenPipe(w, 'wb', 0)
            self._output_pipe_r = eventlet.greenio.GreenPipe(r, 'rb', 0)
        except (ImportError, NotImplementedError):
            # Support for Windows that doesn't support pipes
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', 0))
            sock.listen(1)
            csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            csock.connect(('localhost', sock.getsockname()[1]))
            nsock, addr = sock.accept()
            sock.close()
            self._output_pipe_w = nsock.makefile('wb', 0)
            gsock = eventlet.greenio.GreenSocket(csock)
            self._output_pipe_r = gsock.makefile('rb', 0)

    def on_start_output(self, name):
        """
        Create a new output that streams to the web socket
        :param name:  The name of the new input
        """
        if self._output is not None:
            return
        # Low quality, 64kbit MP3 output for speed
        self._output = audio.mp3.Mp3(7, 64)
        self._create_pipe()
        self._output.add_callback(self._emit_output)
        self._socketio.start_background_task(self._send_queue)
        output = audio_manager.output.Outputs.add_output(name, self._output)
        outputs = [{
            'id': output.id,
            'display_name': name,
            'input_id': '',
            'type': 'browser'
        }]
        self._socketio.emit('output_create', outputs)


class AudioSink(flask_socketio.Namespace):
    """
    A SocketIO namespace to handle audio input and output from the browser
    """

    def __init__(self, *args, **kwargs):
        """
        Configure the audio input and output
        """
        super().__init__(*args, **kwargs)
        self._sessions = {}

    def on_disconnect(self):
        """
        Clean up any outputs that may be emitting to the closed socket
        """
        session = self._sessions.get(flask.request.sid, None)
        if session is not None:
            session.on_disconnect()
            del self._sessions[flask.request.sid]

    def _get_session(self):
        """
        Get the session object for the current SocketIO session
        :return:  The session, created if it didn't already exist
        """
        sid = flask.request.sid
        session = self._sessions.get(sid, None)
        if session is None:
            session = AudioSession(sid)
            self._sessions[sid] = session
        return session

    def on_start_output(self, name):
        """
        Create a new output that streams to the web socket
        :param name:  The name of the new input
        """
        self._get_session().on_start_output(name)


def setup_api(socketio: flask_socketio.SocketIO) -> None:
    """
    Configure the SocketIO endpoints for this namespace
    :param socketio:  The SocketIO to add the namespace to
    """
    socketio.on_namespace(AudioSink('/audio'))
