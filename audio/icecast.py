import socket
import ssl
import base64
import urllib.parse
from . import mp3


class Icecast(object):
    """
    A class that can sink to an Icecast server
    """

    def __init__(self, quality=7, bitrate=64):
        """
        Create a new Icecast stream
        :param quality:  The MP3 encoding quality - 2 is best, 7 is fastest
        :param bitrate:  The constant bitrate to encode using
        """
        self._output = mp3.Mp3(quality, bitrate)
        self._output.add_callback(self._enqueue)
        self._socket = None
        self._source = None
        self._endpoint = None
        # Icecast doesn't actually support chunked encoding
        self._chunk = False

    @property
    def endpoint(self):
        return self._endpoint

    @staticmethod
    def _socket_connect(endpoint):
        """
        Connect to the remote endpoint
        :param endpoint:  The Icecast endpoint to connect to
        :return:  The created socket
        """
        address = endpoint.netloc.split(':')
        if endpoint.scheme == 'https':
            if len(address) == 1:
                address.append(443)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            context.load_default_certs()
            sock = socket.socket()
            connection = context.wrap_socket(sock, server_hostname=address[0])
        else:
            if len(address) == 1:
                address.append(80)
            connection = socket.socket()
        if isinstance(address[1], str):
            address[1] = int(address[1])
        connection.connect((address[0], address[1]))
        return connection

    @staticmethod
    def _authenticate(connection, endpoint, username, password):
        """
        Send the PUT request to the given connection
        :param connection:  The connection to send the request to
        :param endpoint:  The Icecast endpoint to connect to
        :param username:  The username to authenticate with
        :param password:  The password to authenticate with
        """
        auth_token = base64.b64encode(b':'.join((username.encode('latin1'), password.encode('latin1'))))
        headers = [
            'PUT ' + endpoint.path + ' HTTP/1.1',
            'Host: ' + endpoint.netloc,
            'Authorization: Basic ' + auth_token.strip().decode('latin1'),
            'User-Agent: studio',
            'Accept: */*',
            'Transfer-Encoding: chunked',
            'Content-Type: audio/mpeg',
            'Ice-Public: 1',
            'Ice-Name: Radio stream',
            'Ice-Description: Stream from the radio studio',
            'Expect: 100-continue',
            '',
            ''
        ]
        connection.send('\r\n'.join(headers).encode('latin1'))

    @staticmethod
    def _expect_100(connection):
        """
        Read the response headers from the connection
        :param connection:  The connection to expect a 100 response from
        :return:  True if a 100 response was received
        """
        try:
            headers = b''
            while b'\r\n\r\n' not in headers:
                headers += connection.recv(1024)
            return b' 100 ' in headers.split(b'\r\n')[0]
        except IOError:
            return False

    def connect(self, endpoint, password):
        """
        Connect to the Icecast endpoint
        :param endpoint:  The Icecast endpoint to connect to
        :param password:  The password to authenticate with
        :return:  True if the server is now accepting the stream, False if it fails
        """
        self._endpoint = endpoint
        endpoint = urllib.parse.urlparse(endpoint)
        try:
            connection = self._socket_connect(endpoint)
        except ConnectionRefusedError:
            return False
        self._authenticate(connection, endpoint, 'source', password)
        result = self._expect_100(connection)
        if result:
            self._socket = connection
            if self._source is not None:
                self._output.set_input(self._source)
        return result

    def _enqueue(self, source, blocks):
        """
        The handler for MP3 blocks to send to the server
        :param source:  The input source (unused)
        :param blocks:  The data produced (the MP3)
        """
        sock = self._socket
        if sock is not None and len(blocks) > 0:
            length = (hex(len(blocks))[2:]).encode('latin1')
            if self._chunk:
                sock.send(b'\r\n'.join((length, blocks, b'')))
            else:
                sock.send(blocks)

    def set_input(self, source):
        """
        Set the audio source to upload
        :param source:  The source
        """
        if source is self._source:
            return
        self._source = source
        if self._socket is not None:
            self._output.set_input(source)

    def close(self):
        """
        Stop generating MP3 output because the stream has stopped
        """
        self._output.remove_callback(self._enqueue)
        if self._source is not None:
            self._output.set_input(None)
        if self._socket is not None:
            if self._chunk:
                self._socket.send(b'0\r\n\r\n')
            self._socket.close()
