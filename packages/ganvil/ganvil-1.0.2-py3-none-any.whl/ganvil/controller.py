# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from ganvil.go_plugin import grpc_controller_pb2_grpc


class Servicer(grpc_controller_pb2_grpc.GRPCControllerServicer):
    def __init__(self):
        self.is_shut_down = False

    def Shutdown(self, request, context):
        self.is_shut_down = True
