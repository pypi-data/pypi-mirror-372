# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import contextlib
import dataclasses
import errno
import os
import queue
import random
import socket
import sys
import time
import traceback
from collections.abc import Iterator, Mapping, MutableMapping
from concurrent import futures

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_health.v1.health import HealthServicer

from ganvil import controller, stdio
from ganvil.go_plugin import (
    grpc_controller_pb2_grpc,
    grpc_stdio_pb2,
    grpc_stdio_pb2_grpc,
)
from ganvil.protocol.v1 import ganvil_pb2, ganvil_pb2_grpc

BIND_IP: str = "127.0.0.1"

# Capture original streams for later use before stderr/stdout redirection.
sys_stderr = sys.stderr
sys_stdout = sys.stdout


@dataclasses.dataclass
class Context:
    pull_request: ganvil_pb2.PullRequest
    repository: ganvil_pb2.Repository
    run_data: MutableMapping[str, str]


class Plugin:
    name: str
    priority: int = 0

    def init(self, config: Mapping[str, str]) -> None:
        pass

    def apply(self, ctx: Context) -> None:
        return None

    def filter(self, ctx: Context) -> bool:
        return True

    def on_pr_closed(self, ctx: Context):
        pass

    def on_pr_created(self, ctx: Context):
        pass

    def on_pr_merged(self, ctx: Context):
        pass

    def shutdown(self):
        pass


@contextlib.contextmanager
def in_checkout_dir(d: str) -> Iterator[None]:
    current = os.getcwd()
    os.chdir(d)
    try:
        yield
    finally:
        os.chdir(current)


class PluginService(ganvil_pb2_grpc.PluginServiceServicer):
    def __init__(self, p: Plugin):
        self._plugin = p

    def ExecuteActions(
        self, request: ganvil_pb2.ExecuteActionsRequest, context
    ) -> ganvil_pb2.ExecuteActionsResponse:
        ctx = Context(
            pull_request=request.context.pull_request,
            repository=request.context.repository,
            run_data=request.context.run_data,
        )
        try:
            with in_checkout_dir(request.path):
                self._plugin.apply(ctx=ctx)
        except Exception:
            return ganvil_pb2.ExecuteActionsResponse(
                error=traceback.format_exc(),
            )

        return ganvil_pb2.ExecuteActionsResponse(error=None, run_data=ctx.run_data)

    def ExecuteFilters(
        self, request: ganvil_pb2.ExecuteFiltersRequest, context
    ) -> ganvil_pb2.ExecuteFiltersResponse:
        ctx = Context(
            pull_request=request.context.pull_request,
            repository=request.context.repository,
            run_data=request.context.run_data,
        )
        try:
            result = self._plugin.filter(ctx=ctx)
            return ganvil_pb2.ExecuteFiltersResponse(
                match=result,
                error=None,
                run_data=request.context.run_data,
            )
        except Exception:
            return ganvil_pb2.ExecuteFiltersResponse(
                match=False,
                error=traceback.format_exc(),
            )

    def GetPlugin(
        self, request: ganvil_pb2.GetPluginRequest, context
    ) -> ganvil_pb2.GetPluginResponse:
        try:
            self._plugin.init(config=request.config)
            return ganvil_pb2.GetPluginResponse(
                name=self._plugin.name, priority=self._plugin.priority, error=None
            )
        except Exception:
            return ganvil_pb2.GetPluginResponse(
                error=traceback.format_exc(),
            )

    def OnPrClosed(
        self, request: ganvil_pb2.OnPrClosedRequest, context
    ) -> ganvil_pb2.OnPrClosedResponse:
        ctx = Context(
            pull_request=request.context.pull_request,
            repository=request.context.repository,
            run_data=request.context.run_data,
        )
        try:
            self._plugin.on_pr_closed(ctx=ctx)
            return ganvil_pb2.OnPrClosedResponse(error=None)
        except Exception:
            return ganvil_pb2.OnPrClosedResponse(
                error=traceback.format_exc(),
            )

    def OnPrCreated(
        self, request: ganvil_pb2.OnPrCreatedRequest, context
    ) -> ganvil_pb2.OnPrCreatedResponse:
        ctx = Context(
            pull_request=request.context.pull_request,
            repository=request.context.repository,
            run_data=request.context.run_data,
        )
        try:
            self._plugin.on_pr_created(ctx=ctx)
            return ganvil_pb2.OnPrCreatedResponse(error=None)
        except Exception:
            return ganvil_pb2.OnPrCreatedResponse(
                error=traceback.format_exc(),
            )

    def OnPrMerged(
        self, request: ganvil_pb2.OnPrMergedRequest, context
    ) -> ganvil_pb2.OnPrMergedResponse:
        ctx = Context(
            pull_request=request.context.pull_request,
            repository=request.context.repository,
            run_data=request.context.run_data,
        )
        try:
            self._plugin.on_pr_merged(ctx=ctx)
            return ganvil_pb2.OnPrMergedResponse(error=None)
        except Exception:
            return ganvil_pb2.OnPrMergedResponse(
                error=traceback.format_exc(),
            )

    def Shutdown(
        self, request: ganvil_pb2.ShutdownRequest, context
    ) -> ganvil_pb2.ShutdownResponse:
        try:
            self._plugin.shutdown()
            return ganvil_pb2.ShutdownResponse()
        except Exception:
            return ganvil_pb2.ShutdownResponse()


def serve(port: int, shutdown: controller.Servicer, plugin: Plugin):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_insecure_port(f"{BIND_IP}:{port}")

    # Set up redirection of stderr and stdout.
    stdio_queue: queue.SimpleQueue = queue.SimpleQueue()
    stdio_servicer = stdio.Servicer(q=stdio_queue, shutdown_ctrl=shutdown)
    sys.stderr = stdio.Adapter(channel=grpc_stdio_pb2.StdioData.STDERR, q=stdio_queue)
    sys.stdout = stdio.Adapter(channel=grpc_stdio_pb2.StdioData.STDOUT, q=stdio_queue)
    grpc_stdio_pb2_grpc.add_GRPCStdioServicer_to_server(
        servicer=stdio_servicer, server=server
    )

    ganvil_pb2_grpc.add_PluginServiceServicer_to_server(
        servicer=PluginService(plugin), server=server
    )

    grpc_controller_pb2_grpc.add_GRPCControllerServicer_to_server(
        servicer=shutdown, server=server
    )

    health = HealthServicer()
    health.set("plugin", health_pb2.HealthCheckResponse.ServingStatus.Value("SERVING"))
    health_pb2_grpc.add_HealthServicer_to_server(servicer=health, server=server)
    server.start()
    return server


def serve_plugin(plugin: Plugin) -> None:
    port = _find_open_port()
    grpc_controller = controller.Servicer()
    server = serve(port=port, shutdown=grpc_controller, plugin=plugin)
    # Default sys.stdout is being redirected.
    # Use the original stream to write to stdout of the plugin process.
    print(f"1|1|tcp|{BIND_IP}:{port}|grpc", file=sys_stdout)
    sys_stdout.flush()
    try:
        while True:
            time.sleep(0.1)
            if grpc_controller.is_shut_down is True:
                server.stop(0)
                sys.exit(0)
    except KeyboardInterrupt:
        server.stop(0)


def _find_open_port() -> int:
    while True:
        port = random.randrange(start=11000, stop=12000)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((BIND_IP, port))
            return port
        except OSError as e:
            if e.errno != errno.EADDRINUSE:
                raise e
        finally:
            if s is not None:
                s.close()
