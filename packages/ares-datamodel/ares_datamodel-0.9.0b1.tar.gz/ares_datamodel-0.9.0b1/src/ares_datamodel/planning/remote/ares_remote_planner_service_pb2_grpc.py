"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from ...connection import connection_info_pb2 as connection_dot_connection__info__pb2
from ...connection import connection_state_pb2 as connection_dot_connection__state__pb2
from ...connection import connection_status_pb2 as connection_dot_connection__status__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from ...planning import plan_pb2 as planning_dot_plan__pb2
from ...planning import planner_service_capabilities_pb2 as planning_dot_planner__service__capabilities__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in planning/remote/ares_remote_planner_service_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresRemotePlannerServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Plan = channel.unary_unary('/ares.datamodel.planning.remote.AresRemotePlannerService/Plan', request_serializer=planning_dot_plan__pb2.PlanningRequest.SerializeToString, response_deserializer=planning_dot_plan__pb2.PlanningResponse.FromString, _registered_method=True)
        self.GetPlannerServiceCapabilities = channel.unary_unary('/ares.datamodel.planning.remote.AresRemotePlannerService/GetPlannerServiceCapabilities', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=planning_dot_planner__service__capabilities__pb2.PlannerServiceCapabilities.FromString, _registered_method=True)
        self.GetState = channel.unary_unary('/ares.datamodel.planning.remote.AresRemotePlannerService/GetState', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=connection_dot_connection__state__pb2.StateResponse.FromString, _registered_method=True)
        self.GetConnectionStatus = channel.unary_unary('/ares.datamodel.planning.remote.AresRemotePlannerService/GetConnectionStatus', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=connection_dot_connection__status__pb2.ConnectionStatus.FromString, _registered_method=True)
        self.GetInfo = channel.unary_unary('/ares.datamodel.planning.remote.AresRemotePlannerService/GetInfo', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=connection_dot_connection__info__pb2.InfoResponse.FromString, _registered_method=True)

class AresRemotePlannerServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Plan(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPlannerServiceCapabilities(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetConnectionStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresRemotePlannerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'Plan': grpc.unary_unary_rpc_method_handler(servicer.Plan, request_deserializer=planning_dot_plan__pb2.PlanningRequest.FromString, response_serializer=planning_dot_plan__pb2.PlanningResponse.SerializeToString), 'GetPlannerServiceCapabilities': grpc.unary_unary_rpc_method_handler(servicer.GetPlannerServiceCapabilities, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=planning_dot_planner__service__capabilities__pb2.PlannerServiceCapabilities.SerializeToString), 'GetState': grpc.unary_unary_rpc_method_handler(servicer.GetState, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=connection_dot_connection__state__pb2.StateResponse.SerializeToString), 'GetConnectionStatus': grpc.unary_unary_rpc_method_handler(servicer.GetConnectionStatus, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=connection_dot_connection__status__pb2.ConnectionStatus.SerializeToString), 'GetInfo': grpc.unary_unary_rpc_method_handler(servicer.GetInfo, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=connection_dot_connection__info__pb2.InfoResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.datamodel.planning.remote.AresRemotePlannerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.datamodel.planning.remote.AresRemotePlannerService', rpc_method_handlers)

class AresRemotePlannerService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Plan(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.planning.remote.AresRemotePlannerService/Plan', planning_dot_plan__pb2.PlanningRequest.SerializeToString, planning_dot_plan__pb2.PlanningResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetPlannerServiceCapabilities(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.planning.remote.AresRemotePlannerService/GetPlannerServiceCapabilities', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, planning_dot_planner__service__capabilities__pb2.PlannerServiceCapabilities.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetState(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.planning.remote.AresRemotePlannerService/GetState', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, connection_dot_connection__state__pb2.StateResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetConnectionStatus(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.planning.remote.AresRemotePlannerService/GetConnectionStatus', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, connection_dot_connection__status__pb2.ConnectionStatus.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetInfo(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.planning.remote.AresRemotePlannerService/GetInfo', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, connection_dot_connection__info__pb2.InfoResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)