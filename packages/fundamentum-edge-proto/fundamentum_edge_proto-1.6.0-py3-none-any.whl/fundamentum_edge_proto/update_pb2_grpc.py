"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import update_pb2 as update__pb2

class FirmwareUpdateStub(object):
    """Fundamentum Edge's firmware update service.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Subscribe = channel.unary_stream('/com.fundamentum.edge.v1.FirmwareUpdate/Subscribe', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=update__pb2.FirmwareUpdateRequest.FromString)
        self.UpdateStatus = channel.unary_unary('/com.fundamentum.edge.v1.FirmwareUpdate/UpdateStatus', request_serializer=update__pb2.FirmwareUpdateResponse.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString)

class FirmwareUpdateServicer(object):
    """Fundamentum Edge's firmware update service.
    """

    def Subscribe(self, request, context):
        """Subscribe to firmware update stream.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateStatus(self, request, context):
        """Update the status of the firmware update.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_FirmwareUpdateServicer_to_server(servicer, server):
    rpc_method_handlers = {'Subscribe': grpc.unary_stream_rpc_method_handler(servicer.Subscribe, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=update__pb2.FirmwareUpdateRequest.SerializeToString), 'UpdateStatus': grpc.unary_unary_rpc_method_handler(servicer.UpdateStatus, request_deserializer=update__pb2.FirmwareUpdateResponse.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('com.fundamentum.edge.v1.FirmwareUpdate', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

class FirmwareUpdate(object):
    """Fundamentum Edge's firmware update service.
    """

    @staticmethod
    def Subscribe(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/com.fundamentum.edge.v1.FirmwareUpdate/Subscribe', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, update__pb2.FirmwareUpdateRequest.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateStatus(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.fundamentum.edge.v1.FirmwareUpdate/UpdateStatus', update__pb2.FirmwareUpdateResponse.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)