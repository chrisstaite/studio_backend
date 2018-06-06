import flask
import flask_restful
import audio
import queue


class Mp3Generator(object):
    """
    A class that wraps an MP3 encoder that can stream the output to a HTTP response
    """

    def __init__(self, name):
        """
        Create a new encoder and configure its output callback
        :param name:  The name of the output to create
        """
        # Low quality, 64kbit MP3 output for speed
        # TODO: Add to list of available outputs
        self._output = audio.mp3.Mp3(7, 64)
        self._output.add_callback(self._enqueue)
        self._queue = queue.Queue(maxsize=16)

    def _enqueue(self, source, blocks):
        """
        The handler for the output of the MP3
        :param source:  The input source (unused)
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
        self._output.remove_callback(self._enqueue)
        # TODO: Remove from list of available outputs

    def __iter__(self):
        """
        Stream the output of the MP3 encoder
        :return:  A generator of the MP3 blocks
        """
        while True:
            try:
                block = self._queue.get(timeout=10)
            except queue.Empty:
                # Send an empty block to check the connection
                block = b''
            yield block


class StreamSink(flask_restful.Resource):

    def get(self, name):
        return flask.Response(Mp3Generator(name), mimetype="audio/mp3")
