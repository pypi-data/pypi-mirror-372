"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import provisioning_pb2 as provisioning__pb2

class ProvisioningStub(object):
    """Fundamentum Edge's provisioning service.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Provision = channel.unary_unary('/com.fundamentum.edge.v1.Provisioning/Provision', request_serializer=provisioning__pb2.ProvisionRequest.SerializeToString, response_deserializer=provisioning__pb2.ProvisionResponse.FromString)
        self.RegisterShelfDevice = channel.unary_unary('/com.fundamentum.edge.v1.Provisioning/RegisterShelfDevice', request_serializer=provisioning__pb2.RegisterShelfRequest.SerializeToString, response_deserializer=provisioning__pb2.RegisterShelfResponse.FromString)

class ProvisioningServicer(object):
    """Fundamentum Edge's provisioning service.
    """

    def Provision(self, request, context):
        """Provision this device against cloud-side.

        On successful provisioning, amongst other things, the edge daemon will be
        granted MQTT connectivity to the cloud-side broker thus enabling more
        features.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RegisterShelfDevice(self, request, context):
        """Register this device as a shelf device against cloud-side.

        Once registered as a shelf device, Edge will periodically check with Fundamentum
        if the device has been assigned to a registry. Until then, the device is not fully
        provisionned to Fundamentum and most functionnalities will not be available.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_ProvisioningServicer_to_server(servicer, server):
    rpc_method_handlers = {'Provision': grpc.unary_unary_rpc_method_handler(servicer.Provision, request_deserializer=provisioning__pb2.ProvisionRequest.FromString, response_serializer=provisioning__pb2.ProvisionResponse.SerializeToString), 'RegisterShelfDevice': grpc.unary_unary_rpc_method_handler(servicer.RegisterShelfDevice, request_deserializer=provisioning__pb2.RegisterShelfRequest.FromString, response_serializer=provisioning__pb2.RegisterShelfResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('com.fundamentum.edge.v1.Provisioning', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

class Provisioning(object):
    """Fundamentum Edge's provisioning service.
    """

    @staticmethod
    def Provision(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.fundamentum.edge.v1.Provisioning/Provision', provisioning__pb2.ProvisionRequest.SerializeToString, provisioning__pb2.ProvisionResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RegisterShelfDevice(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.fundamentum.edge.v1.Provisioning/RegisterShelfDevice', provisioning__pb2.RegisterShelfRequest.SerializeToString, provisioning__pb2.RegisterShelfResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata)