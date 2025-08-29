"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import states_pb2 as states__pb2

class StatesEventStub(object):
    """Fundamentum Edge's states event service.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.PublishJson = channel.unary_unary('/com.fundamentum.edge.v1.StatesEvent/PublishJson', request_serializer=states__pb2.StateJsonData.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString)

class StatesEventServicer(object):
    """Fundamentum Edge's states event service.
    """

    def PublishJson(self, request, context):
        """Publishes device-specific JSON data to the `state` topic.
        Can be used to send state of a device's sub-devices.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_StatesEventServicer_to_server(servicer, server):
    rpc_method_handlers = {'PublishJson': grpc.unary_unary_rpc_method_handler(servicer.PublishJson, request_deserializer=states__pb2.StateJsonData.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('com.fundamentum.edge.v1.StatesEvent', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

class StatesEvent(object):
    """Fundamentum Edge's states event service.
    """

    @staticmethod
    def PublishJson(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.fundamentum.edge.v1.StatesEvent/PublishJson', states__pb2.StateJsonData.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)