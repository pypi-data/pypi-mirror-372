"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from ...analyzing import analysis_pb2 as analyzing_dot_analysis__pb2
from ...analyzing import analyzer_capabilities_pb2 as analyzing_dot_analyzer__capabilities__pb2
from ...analyzing.remote import ares_remote_analyzer_service_pb2 as analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2
from ...connection import connection_info_pb2 as connection_dot_connection__info__pb2
from ...connection import connection_state_pb2 as connection_dot_connection__state__pb2
from ...connection import connection_status_pb2 as connection_dot_connection__status__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in analyzing/remote/ares_remote_analyzer_service_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresRemoteAnalyzerServiceStub(object):
    """defines a contract for ares to use in order to talk to a remote analyzer
    designed to be similar to the internal ARES analyzer implementation
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Analyze = channel.unary_unary('/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/Analyze', request_serializer=analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.AnalysisRequest.SerializeToString, response_deserializer=analyzing_dot_analysis__pb2.Analysis.FromString, _registered_method=True)
        self.GetAnalyzerCapabilities = channel.unary_unary('/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/GetAnalyzerCapabilities', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=analyzing_dot_analyzer__capabilities__pb2.AnalyzerCapabilities.FromString, _registered_method=True)
        self.ValidateInputs = channel.unary_unary('/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/ValidateInputs', request_serializer=analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.ParameterValidationRequest.SerializeToString, response_deserializer=analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.ParameterValidationResult.FromString, _registered_method=True)
        self.GetAnalysisParameters = channel.unary_unary('/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/GetAnalysisParameters', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.AnalysisParametersResponse.FromString, _registered_method=True)
        self.GetConnectionStatus = channel.unary_unary('/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/GetConnectionStatus', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=connection_dot_connection__status__pb2.ConnectionStatus.FromString, _registered_method=True)
        self.GetState = channel.unary_unary('/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/GetState', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=connection_dot_connection__state__pb2.StateResponse.FromString, _registered_method=True)
        self.GetInfo = channel.unary_unary('/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/GetInfo', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=connection_dot_connection__info__pb2.InfoResponse.FromString, _registered_method=True)

class AresRemoteAnalyzerServiceServicer(object):
    """defines a contract for ares to use in order to talk to a remote analyzer
    designed to be similar to the internal ARES analyzer implementation
    """

    def Analyze(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAnalyzerCapabilities(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ValidateInputs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAnalysisParameters(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetConnectionStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

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

def add_AresRemoteAnalyzerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'Analyze': grpc.unary_unary_rpc_method_handler(servicer.Analyze, request_deserializer=analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.AnalysisRequest.FromString, response_serializer=analyzing_dot_analysis__pb2.Analysis.SerializeToString), 'GetAnalyzerCapabilities': grpc.unary_unary_rpc_method_handler(servicer.GetAnalyzerCapabilities, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=analyzing_dot_analyzer__capabilities__pb2.AnalyzerCapabilities.SerializeToString), 'ValidateInputs': grpc.unary_unary_rpc_method_handler(servicer.ValidateInputs, request_deserializer=analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.ParameterValidationRequest.FromString, response_serializer=analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.ParameterValidationResult.SerializeToString), 'GetAnalysisParameters': grpc.unary_unary_rpc_method_handler(servicer.GetAnalysisParameters, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.AnalysisParametersResponse.SerializeToString), 'GetConnectionStatus': grpc.unary_unary_rpc_method_handler(servicer.GetConnectionStatus, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=connection_dot_connection__status__pb2.ConnectionStatus.SerializeToString), 'GetState': grpc.unary_unary_rpc_method_handler(servicer.GetState, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=connection_dot_connection__state__pb2.StateResponse.SerializeToString), 'GetInfo': grpc.unary_unary_rpc_method_handler(servicer.GetInfo, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=connection_dot_connection__info__pb2.InfoResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.datamodel.analyzing.remote.AresRemoteAnalyzerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.datamodel.analyzing.remote.AresRemoteAnalyzerService', rpc_method_handlers)

class AresRemoteAnalyzerService(object):
    """defines a contract for ares to use in order to talk to a remote analyzer
    designed to be similar to the internal ARES analyzer implementation
    """

    @staticmethod
    def Analyze(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/Analyze', analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.AnalysisRequest.SerializeToString, analyzing_dot_analysis__pb2.Analysis.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetAnalyzerCapabilities(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/GetAnalyzerCapabilities', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, analyzing_dot_analyzer__capabilities__pb2.AnalyzerCapabilities.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ValidateInputs(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/ValidateInputs', analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.ParameterValidationRequest.SerializeToString, analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.ParameterValidationResult.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetAnalysisParameters(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/GetAnalysisParameters', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, analyzing_dot_remote_dot_ares__remote__analyzer__service__pb2.AnalysisParametersResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetConnectionStatus(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/GetConnectionStatus', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, connection_dot_connection__status__pb2.ConnectionStatus.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetState(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/GetState', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, connection_dot_connection__state__pb2.StateResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetInfo(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.analyzing.remote.AresRemoteAnalyzerService/GetInfo', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, connection_dot_connection__info__pb2.InfoResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)