"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import configuration_pb2 as configuration__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

class ConfigurationStub(object):
    """Fundamentum Edge's configuration service.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Get = channel.unary_unary('/com.fundamentum.edge.v1.Configuration/Get', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=configuration__pb2.ConfigData.FromString)
        self.UpdateStream = channel.unary_stream('/com.fundamentum.edge.v1.Configuration/UpdateStream', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=configuration__pb2.UpdateData.FromString)

class ConfigurationServicer(object):
    """Fundamentum Edge's configuration service.
    """

    def Get(self, request, context):
        """Get the device's current configuration.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateStream(self, request, context):
        """Subscribe to configuration updates.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_ConfigurationServicer_to_server(servicer, server):
    rpc_method_handlers = {'Get': grpc.unary_unary_rpc_method_handler(servicer.Get, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=configuration__pb2.ConfigData.SerializeToString), 'UpdateStream': grpc.unary_stream_rpc_method_handler(servicer.UpdateStream, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=configuration__pb2.UpdateData.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('com.fundamentum.edge.v1.Configuration', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

class Configuration(object):
    """Fundamentum Edge's configuration service.
    """

    @staticmethod
    def Get(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.fundamentum.edge.v1.Configuration/Get', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, configuration__pb2.ConfigData.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateStream(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/com.fundamentum.edge.v1.Configuration/UpdateStream', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, configuration__pb2.UpdateData.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)