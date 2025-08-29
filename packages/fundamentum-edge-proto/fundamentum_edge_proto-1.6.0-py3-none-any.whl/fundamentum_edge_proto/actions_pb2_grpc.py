"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import actions_pb2 as actions__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

class ActionsStub(object):
    """Fundamentum Edge's actions service.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Subscribe = channel.unary_stream('/com.fundamentum.edge.v1.Actions/Subscribe', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=actions__pb2.ActionRequest.FromString)
        self.UpdateStatus = channel.unary_unary('/com.fundamentum.edge.v1.Actions/UpdateStatus', request_serializer=actions__pb2.ActionResponse.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString)

class ActionsServicer(object):
    """Fundamentum Edge's actions service.
    """

    def Subscribe(self, request, context):
        """Subscribe to actions stream.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateStatus(self, request, context):
        """Update the status of an action.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_ActionsServicer_to_server(servicer, server):
    rpc_method_handlers = {'Subscribe': grpc.unary_stream_rpc_method_handler(servicer.Subscribe, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=actions__pb2.ActionRequest.SerializeToString), 'UpdateStatus': grpc.unary_unary_rpc_method_handler(servicer.UpdateStatus, request_deserializer=actions__pb2.ActionResponse.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('com.fundamentum.edge.v1.Actions', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

class Actions(object):
    """Fundamentum Edge's actions service.
    """

    @staticmethod
    def Subscribe(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/com.fundamentum.edge.v1.Actions/Subscribe', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, actions__pb2.ActionRequest.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateStatus(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.fundamentum.edge.v1.Actions/UpdateStatus', actions__pb2.ActionResponse.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)