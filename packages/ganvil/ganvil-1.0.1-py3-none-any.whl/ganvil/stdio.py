# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import io
import queue
from collections.abc import Generator
from typing import AnyStr, TextIO

from ganvil import controller
from ganvil.go_plugin import grpc_stdio_pb2, grpc_stdio_pb2_grpc


class Adapter(TextIO):
    """
    Adapter implements all methods needed to replace default stderr and stdout
    IO objects.
    Any message written to it is being put into a queue.
    """

    def __init__(self, channel: grpc_stdio_pb2.StdioData.Channel, q: queue.SimpleQueue):
        self._chan = channel
        self._q = q

    def __exit__(self, __type, __value, __traceback):
        raise io.UnsupportedOperation()

    def __iter__(self):
        raise io.UnsupportedOperation()

    def __next__(self):
        raise io.UnsupportedOperation()

    def writelines(self, __lines):
        raise io.UnsupportedOperation()

    def writable(self):
        raise io.UnsupportedOperation()

    def truncate(self, __size=None):
        raise io.UnsupportedOperation()

    def tell(self):
        raise io.UnsupportedOperation()

    def seekable(self):
        raise io.UnsupportedOperation()

    def seek(self, __offset, __whence=0):
        raise io.UnsupportedOperation()

    def readlines(self, __hint=-1):
        raise io.UnsupportedOperation()

    def readline(self, __limit=-1):
        raise io.UnsupportedOperation()

    def readable(self):
        raise io.UnsupportedOperation()

    def read(self, __n=-1):
        raise io.UnsupportedOperation()

    def isatty(self):
        raise io.UnsupportedOperation()

    def fileno(self):
        raise io.UnsupportedOperation()

    def close(self):
        raise io.UnsupportedOperation()

    def __enter__(self):
        raise io.UnsupportedOperation()

    def flush(self):
        """
        flush implements TextIO.
        """
        while True:
            if self._q.empty() is True:
                return

    def write(self, msg: AnyStr) -> int:
        """
        write implements TextIO.
        """
        data = msg.encode("utf-8") if isinstance(msg, str) else msg
        self._q.put_nowait(grpc_stdio_pb2.StdioData(channel=self._chan, data=data))
        return len(msg)


class Servicer(grpc_stdio_pb2_grpc.GRPCStdioServicer):
    """
    StdioServicer streams output to the main process of saturn-bot via gRPC.
    """

    def __init__(self, q: queue.SimpleQueue, shutdown_ctrl: controller.Servicer):
        self._q = q
        self._shutdown_ctrl = shutdown_ctrl

    def StreamStdio(
        self, request, context
    ) -> Generator[grpc_stdio_pb2.StdioData, None, None]:
        """
        StreamStdio implements GRPCStdioServicer.
        It reads the messages to forward from a queue.
        """
        while True:
            try:
                entry: grpc_stdio_pb2.StdioData = self._q.get(block=True, timeout=0.1)
                yield entry
            except queue.Empty:
                pass

            if self._shutdown_ctrl.is_shut_down is True:
                return
