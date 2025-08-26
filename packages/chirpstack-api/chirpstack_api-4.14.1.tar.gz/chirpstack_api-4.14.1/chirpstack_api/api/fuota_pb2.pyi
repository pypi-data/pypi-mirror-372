import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from chirpstack_api.common import common_pb2 as _common_pb2
from chirpstack_api.api import multicast_group_pb2 as _multicast_group_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RequestFragmentationSessionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NO_REQUEST: _ClassVar[RequestFragmentationSessionStatus]
    AFTER_FRAGMENT_ENQUEUE: _ClassVar[RequestFragmentationSessionStatus]
    AFTER_SESSION_TIMEOUT: _ClassVar[RequestFragmentationSessionStatus]
NO_REQUEST: RequestFragmentationSessionStatus
AFTER_FRAGMENT_ENQUEUE: RequestFragmentationSessionStatus
AFTER_SESSION_TIMEOUT: RequestFragmentationSessionStatus

class FuotaDeployment(_message.Message):
    __slots__ = ("id", "application_id", "device_profile_id", "name", "multicast_group_type", "multicast_class_c_scheduling_type", "multicast_dr", "multicast_class_b_ping_slot_periodicity", "multicast_frequency", "multicast_timeout", "calculate_multicast_timeout", "unicast_max_retry_count", "fragmentation_fragment_size", "calculate_fragmentation_fragment_size", "fragmentation_redundancy_percentage", "fragmentation_session_index", "fragmentation_matrix", "fragmentation_block_ack_delay", "fragmentation_descriptor", "request_fragmentation_session_status", "payload", "on_complete_set_device_tags")
    class OnCompleteSetDeviceTagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_PROFILE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MULTICAST_GROUP_TYPE_FIELD_NUMBER: _ClassVar[int]
    MULTICAST_CLASS_C_SCHEDULING_TYPE_FIELD_NUMBER: _ClassVar[int]
    MULTICAST_DR_FIELD_NUMBER: _ClassVar[int]
    MULTICAST_CLASS_B_PING_SLOT_PERIODICITY_FIELD_NUMBER: _ClassVar[int]
    MULTICAST_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    MULTICAST_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    CALCULATE_MULTICAST_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    UNICAST_MAX_RETRY_COUNT_FIELD_NUMBER: _ClassVar[int]
    FRAGMENTATION_FRAGMENT_SIZE_FIELD_NUMBER: _ClassVar[int]
    CALCULATE_FRAGMENTATION_FRAGMENT_SIZE_FIELD_NUMBER: _ClassVar[int]
    FRAGMENTATION_REDUNDANCY_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    FRAGMENTATION_SESSION_INDEX_FIELD_NUMBER: _ClassVar[int]
    FRAGMENTATION_MATRIX_FIELD_NUMBER: _ClassVar[int]
    FRAGMENTATION_BLOCK_ACK_DELAY_FIELD_NUMBER: _ClassVar[int]
    FRAGMENTATION_DESCRIPTOR_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FRAGMENTATION_SESSION_STATUS_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    ON_COMPLETE_SET_DEVICE_TAGS_FIELD_NUMBER: _ClassVar[int]
    id: str
    application_id: str
    device_profile_id: str
    name: str
    multicast_group_type: _multicast_group_pb2.MulticastGroupType
    multicast_class_c_scheduling_type: _multicast_group_pb2.MulticastGroupSchedulingType
    multicast_dr: int
    multicast_class_b_ping_slot_periodicity: int
    multicast_frequency: int
    multicast_timeout: int
    calculate_multicast_timeout: bool
    unicast_max_retry_count: int
    fragmentation_fragment_size: int
    calculate_fragmentation_fragment_size: bool
    fragmentation_redundancy_percentage: int
    fragmentation_session_index: int
    fragmentation_matrix: int
    fragmentation_block_ack_delay: int
    fragmentation_descriptor: bytes
    request_fragmentation_session_status: RequestFragmentationSessionStatus
    payload: bytes
    on_complete_set_device_tags: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[str] = ..., application_id: _Optional[str] = ..., device_profile_id: _Optional[str] = ..., name: _Optional[str] = ..., multicast_group_type: _Optional[_Union[_multicast_group_pb2.MulticastGroupType, str]] = ..., multicast_class_c_scheduling_type: _Optional[_Union[_multicast_group_pb2.MulticastGroupSchedulingType, str]] = ..., multicast_dr: _Optional[int] = ..., multicast_class_b_ping_slot_periodicity: _Optional[int] = ..., multicast_frequency: _Optional[int] = ..., multicast_timeout: _Optional[int] = ..., calculate_multicast_timeout: bool = ..., unicast_max_retry_count: _Optional[int] = ..., fragmentation_fragment_size: _Optional[int] = ..., calculate_fragmentation_fragment_size: bool = ..., fragmentation_redundancy_percentage: _Optional[int] = ..., fragmentation_session_index: _Optional[int] = ..., fragmentation_matrix: _Optional[int] = ..., fragmentation_block_ack_delay: _Optional[int] = ..., fragmentation_descriptor: _Optional[bytes] = ..., request_fragmentation_session_status: _Optional[_Union[RequestFragmentationSessionStatus, str]] = ..., payload: _Optional[bytes] = ..., on_complete_set_device_tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class FuotaDeploymentListItem(_message.Message):
    __slots__ = ("id", "created_at", "updated_at", "started_at", "completed_at", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    started_at: _timestamp_pb2.Timestamp
    completed_at: _timestamp_pb2.Timestamp
    name: str
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., completed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., name: _Optional[str] = ...) -> None: ...

class FuotaDeploymentDeviceListItem(_message.Message):
    __slots__ = ("fuota_deployment_id", "dev_eui", "created_at", "completed_at", "mc_group_setup_completed_at", "mc_session_completed_at", "frag_session_setup_completed_at", "frag_status_completed_at", "error_msg")
    FUOTA_DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DEV_EUI_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    MC_GROUP_SETUP_COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    MC_SESSION_COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    FRAG_SESSION_SETUP_COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    FRAG_STATUS_COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MSG_FIELD_NUMBER: _ClassVar[int]
    fuota_deployment_id: str
    dev_eui: str
    created_at: _timestamp_pb2.Timestamp
    completed_at: _timestamp_pb2.Timestamp
    mc_group_setup_completed_at: _timestamp_pb2.Timestamp
    mc_session_completed_at: _timestamp_pb2.Timestamp
    frag_session_setup_completed_at: _timestamp_pb2.Timestamp
    frag_status_completed_at: _timestamp_pb2.Timestamp
    error_msg: str
    def __init__(self, fuota_deployment_id: _Optional[str] = ..., dev_eui: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., completed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., mc_group_setup_completed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., mc_session_completed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., frag_session_setup_completed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., frag_status_completed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., error_msg: _Optional[str] = ...) -> None: ...

class FuotaDeploymentGatewayListItem(_message.Message):
    __slots__ = ("fuota_deployment_id", "gateway_id", "created_at")
    FUOTA_DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    fuota_deployment_id: str
    gateway_id: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, fuota_deployment_id: _Optional[str] = ..., gateway_id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateFuotaDeploymentRequest(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: FuotaDeployment
    def __init__(self, deployment: _Optional[_Union[FuotaDeployment, _Mapping]] = ...) -> None: ...

class CreateFuotaDeploymentResponse(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetFuotaDeploymentRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetFuotaDeploymentResponse(_message.Message):
    __slots__ = ("deployment", "created_at", "updated_at", "started_at", "completed_at")
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    deployment: FuotaDeployment
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    started_at: _timestamp_pb2.Timestamp
    completed_at: _timestamp_pb2.Timestamp
    def __init__(self, deployment: _Optional[_Union[FuotaDeployment, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., completed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class UpdateFuotaDeploymentRequest(_message.Message):
    __slots__ = ("deployment",)
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    deployment: FuotaDeployment
    def __init__(self, deployment: _Optional[_Union[FuotaDeployment, _Mapping]] = ...) -> None: ...

class DeleteFuotaDeploymentRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class StartFuotaDeploymentRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListFuotaDeploymentsRequest(_message.Message):
    __slots__ = ("limit", "offset", "application_id")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    application_id: str
    def __init__(self, limit: _Optional[int] = ..., offset: _Optional[int] = ..., application_id: _Optional[str] = ...) -> None: ...

class ListFuotaDeploymentsResponse(_message.Message):
    __slots__ = ("total_count", "result")
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    total_count: int
    result: _containers.RepeatedCompositeFieldContainer[FuotaDeploymentListItem]
    def __init__(self, total_count: _Optional[int] = ..., result: _Optional[_Iterable[_Union[FuotaDeploymentListItem, _Mapping]]] = ...) -> None: ...

class AddDevicesToFuotaDeploymentRequest(_message.Message):
    __slots__ = ("fuota_deployment_id", "dev_euis")
    FUOTA_DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DEV_EUIS_FIELD_NUMBER: _ClassVar[int]
    fuota_deployment_id: str
    dev_euis: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fuota_deployment_id: _Optional[str] = ..., dev_euis: _Optional[_Iterable[str]] = ...) -> None: ...

class RemoveDevicesFromFuotaDeploymentRequest(_message.Message):
    __slots__ = ("fuota_deployment_id", "dev_euis")
    FUOTA_DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    DEV_EUIS_FIELD_NUMBER: _ClassVar[int]
    fuota_deployment_id: str
    dev_euis: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fuota_deployment_id: _Optional[str] = ..., dev_euis: _Optional[_Iterable[str]] = ...) -> None: ...

class ListFuotaDeploymentDevicesRequest(_message.Message):
    __slots__ = ("limit", "offset", "fuota_deployment_id")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    FUOTA_DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    fuota_deployment_id: str
    def __init__(self, limit: _Optional[int] = ..., offset: _Optional[int] = ..., fuota_deployment_id: _Optional[str] = ...) -> None: ...

class ListFuotaDeploymentDevicesResponse(_message.Message):
    __slots__ = ("total_count", "result")
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    total_count: int
    result: _containers.RepeatedCompositeFieldContainer[FuotaDeploymentDeviceListItem]
    def __init__(self, total_count: _Optional[int] = ..., result: _Optional[_Iterable[_Union[FuotaDeploymentDeviceListItem, _Mapping]]] = ...) -> None: ...

class AddGatewaysToFuotaDeploymentRequest(_message.Message):
    __slots__ = ("fuota_deployment_id", "gateway_ids")
    FUOTA_DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_IDS_FIELD_NUMBER: _ClassVar[int]
    fuota_deployment_id: str
    gateway_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fuota_deployment_id: _Optional[str] = ..., gateway_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class RemoveGatewaysFromFuotaDeploymentRequest(_message.Message):
    __slots__ = ("fuota_deployment_id", "gateway_ids")
    FUOTA_DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_IDS_FIELD_NUMBER: _ClassVar[int]
    fuota_deployment_id: str
    gateway_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, fuota_deployment_id: _Optional[str] = ..., gateway_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ListFuotaDeploymentGatewaysRequest(_message.Message):
    __slots__ = ("limit", "offset", "fuota_deployment_id")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    FUOTA_DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    fuota_deployment_id: str
    def __init__(self, limit: _Optional[int] = ..., offset: _Optional[int] = ..., fuota_deployment_id: _Optional[str] = ...) -> None: ...

class ListFuotaDeploymentGatewaysResponse(_message.Message):
    __slots__ = ("total_count", "result")
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    total_count: int
    result: _containers.RepeatedCompositeFieldContainer[FuotaDeploymentGatewayListItem]
    def __init__(self, total_count: _Optional[int] = ..., result: _Optional[_Iterable[_Union[FuotaDeploymentGatewayListItem, _Mapping]]] = ...) -> None: ...

class ListFuotaDeploymentJobsRequest(_message.Message):
    __slots__ = ("fuota_deployment_id",)
    FUOTA_DEPLOYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    fuota_deployment_id: str
    def __init__(self, fuota_deployment_id: _Optional[str] = ...) -> None: ...

class ListFuotaDeploymentJobsResponse(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[FuotaDeploymentJob]
    def __init__(self, jobs: _Optional[_Iterable[_Union[FuotaDeploymentJob, _Mapping]]] = ...) -> None: ...

class FuotaDeploymentJob(_message.Message):
    __slots__ = ("job", "created_at", "completed_at", "max_retry_count", "attempt_count", "scheduler_run_after", "warning_msg", "error_msg")
    JOB_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    MAX_RETRY_COUNT_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_COUNT_FIELD_NUMBER: _ClassVar[int]
    SCHEDULER_RUN_AFTER_FIELD_NUMBER: _ClassVar[int]
    WARNING_MSG_FIELD_NUMBER: _ClassVar[int]
    ERROR_MSG_FIELD_NUMBER: _ClassVar[int]
    job: str
    created_at: _timestamp_pb2.Timestamp
    completed_at: _timestamp_pb2.Timestamp
    max_retry_count: int
    attempt_count: int
    scheduler_run_after: _timestamp_pb2.Timestamp
    warning_msg: str
    error_msg: str
    def __init__(self, job: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., completed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., max_retry_count: _Optional[int] = ..., attempt_count: _Optional[int] = ..., scheduler_run_after: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., warning_msg: _Optional[str] = ..., error_msg: _Optional[str] = ...) -> None: ...
