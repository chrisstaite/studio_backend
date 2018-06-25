import typing
import flask
import flask_restful
import audio
import queue
import audio_manager


class Mp3Generator(object):
    """
    A class that wraps an MP3 encoder that can stream the output to a HTTP response
    """

    def __init__(self, name: str):
        """
        Create a new encoder and configure its output callback
        :param name:  The name of the output to create
        """
        # Low quality, 64kbit MP3 output for speed
        self._output = audio.mp3.Mp3(7, 64)
        self._output.add_callback(self._enqueue)
        self._queue = queue.Queue(maxsize=512)
        output = audio_manager.output.Outputs.add_output(name, self._output)
        outputs = [{
            'id': output.id,
            'display_name': name,
            'input_id': '',
            'type': 'browser'
        }]
        self._socketio = flask.current_app.extensions['socketio']
        self._socketio.emit('output_create', outputs)

    @property
    def input(self):
        """
        Get the current input
        :return:  The current input
        """
        return self._output.input

    @input.setter
    def input(self, source):
        self._output.input = source

    def _enqueue(self, _, blocks: typing.List[bytes]):
        """
        The handler for the output of the MP3
        :param blocks:  The data produced (the MP3)
        """
        try:
            self._queue.put_nowait(blocks)
        except queue.Full:
            self._queue.get_nowait()
            self._queue.put_nowait(blocks)

    def close(self):
        """
        Stop generating MP3 output because the stream has stopped
        """
        self._output.input = None
        self._output.remove_callback(self._enqueue)
        try:
            output = audio_manager.output.Outputs.get_output(self._output)
            audio_manager.output.Outputs.delete_output(output)
            self._socketio.emit('output_remove', {'id': output.id})
        except ValueError:
            pass

    def __iter__(self):
        """
        Stream the output of the MP3 encoder
        :return:  A generator of the MP3 blocks
        """
        while True:
            try:
                yield self._queue.get(timeout=5)
            except queue.Empty:
                # Send an empty block to check the connection
                yield b''


class StreamSink(flask_restful.Resource):
    """
    Handler for creating a new output
    """

    @staticmethod
    def get(name: str) -> flask.Response:
        """
        Create a new MP3 output stream
        :param name:  The name to give the stream
        :return:  The streaming response
        """
        return flask.Response(Mp3Generator(name), mimetype="audio/mpeg")


def setup_api(api: flask_restful.Api) -> None:
    """
    Configure the REST endpoints for this namespace
    :param api:  The API to add the endpoints to
    """
    api.add_resource(StreamSink, '/audio/output_stream/<string:name>')
