import json
from datetime import datetime
import socket
import time
from subprocess import DEVNULL, PIPE, Popen
from threading import Event, Thread

from moku import MOKU_CLI_PATH
from moku.utilities import check_mokucli_version
from moku.exceptions import StreamException
from moku import version


class MokuCLIThread(Thread):
    """
    Threadinng class responsible to run the mokucli command.

    :param command: Command to execute as a subprocess
    :param start_evt: Event object to set once the subprocess is launched
    """

    def __init__(self, command, error_event, start_evt=None):
        self.command = command
        self.start_evt = start_evt
        self.error_event = error_event
        super(MokuCLIThread, self).__init__()

    def run(self):
        process = Popen(self.command, stdout=DEVNULL, stderr=PIPE)
        # signal subprocess launch...
        if self.start_evt:
            self.start_evt.set()
        process.wait()  # waits until the subprocess is finished executing
        error = process.stderr.read().decode("utf8")
        if error:
            self.error_event.set()
            raise StreamException(error)


class StreamInstrument:
    """
    Base class for all streaming features. Any instrument
    supporting Data streaming should inherit this class
    """

    def __init__(self, mokuOS_version):
        self.stream_id = None
        self.ip_address = None
        self.port = None
        self._socket_rdr = None
        self._running = False
        self._error_event = Event()

    @staticmethod
    def _get_next_available_port():
        sock = socket.socket()
        sock.bind(("", 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    def _reset_stream_config(self):
        self.stream_id = None
        self.ip_address = None
        self.port = None
        self._socket_rdr = None
        self._running = False
        self._error_event = Event()

    def _connect(self):
        """
        Tries to connect to the tcp port or raises Exception
        """
        i = 0
        while True:
            try:
                i += 1
                if self._error_event.is_set():
                    raise Exception
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(("localhost", self.port))
                self._socket_rdr = client.makefile("r")
                break
            except socket.error:
                if i == 5:
                    raise Exception(f"Cannot connect to port {self.port}")
                time.sleep(0.5)

    def _begin_streaming(self):
        self.port = self._get_next_available_port()
        _ip = f"--ip-address={self.ip_address}"
        _stream = f"--stream-id={self.stream_id}"
        _target = f"--target={self.port}"
        command = [MOKU_CLI_PATH, "stream", _ip, _stream, _target]
        _start_event = Event()

        cli_thread = MokuCLIThread(command, self._error_event, _start_event)
        cli_thread.start()
        _start_event.wait()
        self._running = True
        self._connect()

    def start_streaming(self):
        """
        Base class start_streaming, verifies if streaming is possible
        """
        check_mokucli_version(MOKU_CLI_PATH)

    def stream_to_file(self, name=None):
        """
        Streams the data to the file of desired format

        :type name: `string`
        :param name: Base name with one of csv, npy, mat extensions (defaults to csv) # noqa

        """
        if not self.stream_id:
            raise StreamException(
                "No streaming session in progress, start one using start_streaming"
            )  # noqa
        if not self._running:
            check_mokucli_version(MOKU_CLI_PATH)
            _ip = f"--ip-address={self.ip_address}"
            _stream = f"--stream-id={self.stream_id}"

            if not name:
                _ts = datetime.now()
                name = f"STREAM_{_ts.strftime('%d%m%Y%H%M%S')}.csv"

            _target = f"--target={name}"
            command = [MOKU_CLI_PATH, "stream", _ip, _stream, _target]
            cli_thread = MokuCLIThread(command, self._error_event)
            cli_thread.start()

    def get_stream_data(self):
        """
        Get the converted stream of data

        :raises StreamException: Indicates END OF STREAM
        """
        if not self.stream_id:
            raise StreamException(
                "No streaming session in progress, start one using start_streaming"
            )  # noqa
        if self._error_event.is_set():
            raise Exception
        if not self._running:
            check_mokucli_version(MOKU_CLI_PATH)
            self._begin_streaming()
        data = self._socket_rdr.readline()
        if data:
            if data == "EOS\n":
                self._reset_stream_config()
                raise StreamException("End of stream")
            return json.loads(data)
