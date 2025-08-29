"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from . import ares_planner_management_service_pb2 as ares__planner__management__service__pb2
from . import ares_struct_pb2 as ares__struct__pb2
from .connection import connection_state_pb2 as connection_dot_connection__state__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from .planning import manual_planner_pb2 as planning_dot_manual__planner__pb2
from .planning import planner_settings_pb2 as planning_dot_planner__settings__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in ares_planner_management_service_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresPlannerManagementServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetState = channel.unary_unary('/ares.services.AresPlannerManagementService/GetState', request_serializer=connection_dot_connection__state__pb2.StateRequest.SerializeToString, response_deserializer=connection_dot_connection__state__pb2.StateResponse.FromString, _registered_method=True)
        self.GetInfo = channel.unary_unary('/ares.services.AresPlannerManagementService/GetInfo', request_serializer=ares__planner__management__service__pb2.PlannerInfoRequest.SerializeToString, response_deserializer=ares__planner__management__service__pb2.PlannerInfoResponse.FromString, _registered_method=True)
        self.SetPlannerSettings = channel.unary_unary('/ares.services.AresPlannerManagementService/SetPlannerSettings', request_serializer=planning_dot_planner__settings__pb2.PlannerSettings.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.GetPlannerSettings = channel.unary_unary('/ares.services.AresPlannerManagementService/GetPlannerSettings', request_serializer=ares__planner__management__service__pb2.PlannerSettingsRequest.SerializeToString, response_deserializer=ares__struct__pb2.AresStruct.FromString, _registered_method=True)
        self.SeedManualPlanner = channel.unary_unary('/ares.services.AresPlannerManagementService/SeedManualPlanner', request_serializer=planning_dot_manual__planner__pb2.ManualPlannerSeed.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.GetManualPlannerSeed = channel.unary_unary('/ares.services.AresPlannerManagementService/GetManualPlannerSeed', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=planning_dot_manual__planner__pb2.ManualPlannerSetCollection.FromString, _registered_method=True)
        self.ResetManualPlanner = channel.unary_unary('/ares.services.AresPlannerManagementService/ResetManualPlanner', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.GetAllPlanners = channel.unary_unary('/ares.services.AresPlannerManagementService/GetAllPlanners', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__planner__management__service__pb2.GetAllPlannersResponse.FromString, _registered_method=True)
        self.AddPlanner = channel.unary_unary('/ares.services.AresPlannerManagementService/AddPlanner', request_serializer=ares__planner__management__service__pb2.AddPlannerRequest.SerializeToString, response_deserializer=ares__planner__management__service__pb2.AddPlannerResponse.FromString, _registered_method=True)
        self.UpdatePlanner = channel.unary_unary('/ares.services.AresPlannerManagementService/UpdatePlanner', request_serializer=ares__planner__management__service__pb2.UpdatePlannerRequest.SerializeToString, response_deserializer=ares__planner__management__service__pb2.UpdatePlannerResponse.FromString, _registered_method=True)
        self.RemovePlanner = channel.unary_unary('/ares.services.AresPlannerManagementService/RemovePlanner', request_serializer=ares__planner__management__service__pb2.RemovePlannerRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)

class AresPlannerManagementServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetPlannerSettings(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPlannerSettings(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SeedManualPlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetManualPlannerSeed(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ResetManualPlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAllPlanners(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddPlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdatePlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemovePlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresPlannerManagementServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetState': grpc.unary_unary_rpc_method_handler(servicer.GetState, request_deserializer=connection_dot_connection__state__pb2.StateRequest.FromString, response_serializer=connection_dot_connection__state__pb2.StateResponse.SerializeToString), 'GetInfo': grpc.unary_unary_rpc_method_handler(servicer.GetInfo, request_deserializer=ares__planner__management__service__pb2.PlannerInfoRequest.FromString, response_serializer=ares__planner__management__service__pb2.PlannerInfoResponse.SerializeToString), 'SetPlannerSettings': grpc.unary_unary_rpc_method_handler(servicer.SetPlannerSettings, request_deserializer=planning_dot_planner__settings__pb2.PlannerSettings.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'GetPlannerSettings': grpc.unary_unary_rpc_method_handler(servicer.GetPlannerSettings, request_deserializer=ares__planner__management__service__pb2.PlannerSettingsRequest.FromString, response_serializer=ares__struct__pb2.AresStruct.SerializeToString), 'SeedManualPlanner': grpc.unary_unary_rpc_method_handler(servicer.SeedManualPlanner, request_deserializer=planning_dot_manual__planner__pb2.ManualPlannerSeed.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'GetManualPlannerSeed': grpc.unary_unary_rpc_method_handler(servicer.GetManualPlannerSeed, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=planning_dot_manual__planner__pb2.ManualPlannerSetCollection.SerializeToString), 'ResetManualPlanner': grpc.unary_unary_rpc_method_handler(servicer.ResetManualPlanner, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'GetAllPlanners': grpc.unary_unary_rpc_method_handler(servicer.GetAllPlanners, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__planner__management__service__pb2.GetAllPlannersResponse.SerializeToString), 'AddPlanner': grpc.unary_unary_rpc_method_handler(servicer.AddPlanner, request_deserializer=ares__planner__management__service__pb2.AddPlannerRequest.FromString, response_serializer=ares__planner__management__service__pb2.AddPlannerResponse.SerializeToString), 'UpdatePlanner': grpc.unary_unary_rpc_method_handler(servicer.UpdatePlanner, request_deserializer=ares__planner__management__service__pb2.UpdatePlannerRequest.FromString, response_serializer=ares__planner__management__service__pb2.UpdatePlannerResponse.SerializeToString), 'RemovePlanner': grpc.unary_unary_rpc_method_handler(servicer.RemovePlanner, request_deserializer=ares__planner__management__service__pb2.RemovePlannerRequest.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.services.AresPlannerManagementService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.services.AresPlannerManagementService', rpc_method_handlers)

class AresPlannerManagementService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetState(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/GetState', connection_dot_connection__state__pb2.StateRequest.SerializeToString, connection_dot_connection__state__pb2.StateResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetInfo(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/GetInfo', ares__planner__management__service__pb2.PlannerInfoRequest.SerializeToString, ares__planner__management__service__pb2.PlannerInfoResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def SetPlannerSettings(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/SetPlannerSettings', planning_dot_planner__settings__pb2.PlannerSettings.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetPlannerSettings(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/GetPlannerSettings', ares__planner__management__service__pb2.PlannerSettingsRequest.SerializeToString, ares__struct__pb2.AresStruct.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def SeedManualPlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/SeedManualPlanner', planning_dot_manual__planner__pb2.ManualPlannerSeed.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetManualPlannerSeed(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/GetManualPlannerSeed', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, planning_dot_manual__planner__pb2.ManualPlannerSetCollection.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ResetManualPlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/ResetManualPlanner', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetAllPlanners(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/GetAllPlanners', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__planner__management__service__pb2.GetAllPlannersResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def AddPlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/AddPlanner', ares__planner__management__service__pb2.AddPlannerRequest.SerializeToString, ares__planner__management__service__pb2.AddPlannerResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdatePlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/UpdatePlanner', ares__planner__management__service__pb2.UpdatePlannerRequest.SerializeToString, ares__planner__management__service__pb2.UpdatePlannerResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RemovePlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresPlannerManagementService/RemovePlanner', ares__planner__management__service__pb2.RemovePlannerRequest.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)