"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import telemetry_pb2 as telemetry__pb2

class TelemetryStub(object):
    """Fundamentum Edge's telemetry service.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Publish = channel.stream_unary('/com.fundamentum.edge.v1.Telemetry/Publish', request_serializer=telemetry__pb2.TelemetryRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString)
        self.PublishOne = channel.unary_unary('/com.fundamentum.edge.v1.Telemetry/PublishOne', request_serializer=telemetry__pb2.TelemetryRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString)

class TelemetryServicer(object):
    """Fundamentum Edge's telemetry service.
    """

    def Publish(self, request_iterator, context):
        """Publishes device-specific data to the `event` topic or to one of its sub-topics if specified.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PublishOne(self, request, context):
        """Publish one device-specific data to the `event` topic or to one of its sub-topics if specified.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_TelemetryServicer_to_server(servicer, server):
    rpc_method_handlers = {'Publish': grpc.stream_unary_rpc_method_handler(servicer.Publish, request_deserializer=telemetry__pb2.TelemetryRequest.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'PublishOne': grpc.unary_unary_rpc_method_handler(servicer.PublishOne, request_deserializer=telemetry__pb2.TelemetryRequest.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('com.fundamentum.edge.v1.Telemetry', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

class Telemetry(object):
    """Fundamentum Edge's telemetry service.
    """

    @staticmethod
    def Publish(request_iterator, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/com.fundamentum.edge.v1.Telemetry/Publish', telemetry__pb2.TelemetryRequest.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PublishOne(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.fundamentum.edge.v1.Telemetry/PublishOne', telemetry__pb2.TelemetryRequest.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)