import datetime

from chirpstack_api.common import common_pb2 as _common_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CodeRate(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CR_UNDEFINED: _ClassVar[CodeRate]
    CR_4_5: _ClassVar[CodeRate]
    CR_4_6: _ClassVar[CodeRate]
    CR_4_7: _ClassVar[CodeRate]
    CR_4_8: _ClassVar[CodeRate]
    CR_3_8: _ClassVar[CodeRate]
    CR_2_6: _ClassVar[CodeRate]
    CR_1_4: _ClassVar[CodeRate]
    CR_1_6: _ClassVar[CodeRate]
    CR_5_6: _ClassVar[CodeRate]
    CR_LI_4_5: _ClassVar[CodeRate]
    CR_LI_4_6: _ClassVar[CodeRate]
    CR_LI_4_8: _ClassVar[CodeRate]

class DownlinkTiming(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMMEDIATELY: _ClassVar[DownlinkTiming]
    DELAY: _ClassVar[DownlinkTiming]
    GPS_EPOCH: _ClassVar[DownlinkTiming]

class FineTimestampType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NONE: _ClassVar[FineTimestampType]
    ENCRYPTED: _ClassVar[FineTimestampType]
    PLAIN: _ClassVar[FineTimestampType]

class CRCStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NO_CRC: _ClassVar[CRCStatus]
    BAD_CRC: _ClassVar[CRCStatus]
    CRC_OK: _ClassVar[CRCStatus]

class TxAckStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IGNORED: _ClassVar[TxAckStatus]
    OK: _ClassVar[TxAckStatus]
    TOO_LATE: _ClassVar[TxAckStatus]
    TOO_EARLY: _ClassVar[TxAckStatus]
    COLLISION_PACKET: _ClassVar[TxAckStatus]
    COLLISION_BEACON: _ClassVar[TxAckStatus]
    TX_FREQ: _ClassVar[TxAckStatus]
    TX_POWER: _ClassVar[TxAckStatus]
    GPS_UNLOCKED: _ClassVar[TxAckStatus]
    QUEUE_FULL: _ClassVar[TxAckStatus]
    INTERNAL_ERROR: _ClassVar[TxAckStatus]
    DUTY_CYCLE_OVERFLOW: _ClassVar[TxAckStatus]
CR_UNDEFINED: CodeRate
CR_4_5: CodeRate
CR_4_6: CodeRate
CR_4_7: CodeRate
CR_4_8: CodeRate
CR_3_8: CodeRate
CR_2_6: CodeRate
CR_1_4: CodeRate
CR_1_6: CodeRate
CR_5_6: CodeRate
CR_LI_4_5: CodeRate
CR_LI_4_6: CodeRate
CR_LI_4_8: CodeRate
IMMEDIATELY: DownlinkTiming
DELAY: DownlinkTiming
GPS_EPOCH: DownlinkTiming
NONE: FineTimestampType
ENCRYPTED: FineTimestampType
PLAIN: FineTimestampType
NO_CRC: CRCStatus
BAD_CRC: CRCStatus
CRC_OK: CRCStatus
IGNORED: TxAckStatus
OK: TxAckStatus
TOO_LATE: TxAckStatus
TOO_EARLY: TxAckStatus
COLLISION_PACKET: TxAckStatus
COLLISION_BEACON: TxAckStatus
TX_FREQ: TxAckStatus
TX_POWER: TxAckStatus
GPS_UNLOCKED: TxAckStatus
QUEUE_FULL: TxAckStatus
INTERNAL_ERROR: TxAckStatus
DUTY_CYCLE_OVERFLOW: TxAckStatus

class Event(_message.Message):
    __slots__ = ("uplink_frame", "gateway_stats", "mesh")
    UPLINK_FRAME_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_STATS_FIELD_NUMBER: _ClassVar[int]
    MESH_FIELD_NUMBER: _ClassVar[int]
    uplink_frame: UplinkFrame
    gateway_stats: GatewayStats
    mesh: MeshEvent
    def __init__(self, uplink_frame: _Optional[_Union[UplinkFrame, _Mapping]] = ..., gateway_stats: _Optional[_Union[GatewayStats, _Mapping]] = ..., mesh: _Optional[_Union[MeshEvent, _Mapping]] = ...) -> None: ...

class Command(_message.Message):
    __slots__ = ("send_downlink_frame", "set_gateway_configuration", "get_gateway_id", "get_location", "mesh")
    SEND_DOWNLINK_FRAME_FIELD_NUMBER: _ClassVar[int]
    SET_GATEWAY_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    GET_GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    GET_LOCATION_FIELD_NUMBER: _ClassVar[int]
    MESH_FIELD_NUMBER: _ClassVar[int]
    send_downlink_frame: DownlinkFrame
    set_gateway_configuration: GatewayConfiguration
    get_gateway_id: GetGatewayIdRequest
    get_location: GetLocationRequest
    mesh: MeshCommand
    def __init__(self, send_downlink_frame: _Optional[_Union[DownlinkFrame, _Mapping]] = ..., set_gateway_configuration: _Optional[_Union[GatewayConfiguration, _Mapping]] = ..., get_gateway_id: _Optional[_Union[GetGatewayIdRequest, _Mapping]] = ..., get_location: _Optional[_Union[GetLocationRequest, _Mapping]] = ..., mesh: _Optional[_Union[MeshCommand, _Mapping]] = ...) -> None: ...

class MeshEvent(_message.Message):
    __slots__ = ("gateway_id", "relay_id", "time", "events")
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    RELAY_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    gateway_id: str
    relay_id: str
    time: _timestamp_pb2.Timestamp
    events: _containers.RepeatedCompositeFieldContainer[MeshEventItem]
    def __init__(self, gateway_id: _Optional[str] = ..., relay_id: _Optional[str] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., events: _Optional[_Iterable[_Union[MeshEventItem, _Mapping]]] = ...) -> None: ...

class MeshEventItem(_message.Message):
    __slots__ = ("proprietary", "heartbeat")
    PROPRIETARY_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    proprietary: MeshEventProprietary
    heartbeat: MeshEventHeartbeat
    def __init__(self, proprietary: _Optional[_Union[MeshEventProprietary, _Mapping]] = ..., heartbeat: _Optional[_Union[MeshEventHeartbeat, _Mapping]] = ...) -> None: ...

class MeshCommand(_message.Message):
    __slots__ = ("gateway_id", "relay_id", "commands")
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    RELAY_ID_FIELD_NUMBER: _ClassVar[int]
    COMMANDS_FIELD_NUMBER: _ClassVar[int]
    gateway_id: str
    relay_id: str
    commands: _containers.RepeatedCompositeFieldContainer[MeshCommandItem]
    def __init__(self, gateway_id: _Optional[str] = ..., relay_id: _Optional[str] = ..., commands: _Optional[_Iterable[_Union[MeshCommandItem, _Mapping]]] = ...) -> None: ...

class MeshCommandItem(_message.Message):
    __slots__ = ("proprietary",)
    PROPRIETARY_FIELD_NUMBER: _ClassVar[int]
    proprietary: MeshCommandProprietary
    def __init__(self, proprietary: _Optional[_Union[MeshCommandProprietary, _Mapping]] = ...) -> None: ...

class Modulation(_message.Message):
    __slots__ = ("lora", "fsk", "lr_fhss")
    LORA_FIELD_NUMBER: _ClassVar[int]
    FSK_FIELD_NUMBER: _ClassVar[int]
    LR_FHSS_FIELD_NUMBER: _ClassVar[int]
    lora: LoraModulationInfo
    fsk: FskModulationInfo
    lr_fhss: LrFhssModulationInfo
    def __init__(self, lora: _Optional[_Union[LoraModulationInfo, _Mapping]] = ..., fsk: _Optional[_Union[FskModulationInfo, _Mapping]] = ..., lr_fhss: _Optional[_Union[LrFhssModulationInfo, _Mapping]] = ...) -> None: ...

class UplinkTxInfoLegacy(_message.Message):
    __slots__ = ("frequency", "modulation", "lora_modulation_info", "fsk_modulation_info", "lr_fhss_modulation_info")
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    MODULATION_FIELD_NUMBER: _ClassVar[int]
    LORA_MODULATION_INFO_FIELD_NUMBER: _ClassVar[int]
    FSK_MODULATION_INFO_FIELD_NUMBER: _ClassVar[int]
    LR_FHSS_MODULATION_INFO_FIELD_NUMBER: _ClassVar[int]
    frequency: int
    modulation: _common_pb2.Modulation
    lora_modulation_info: LoraModulationInfo
    fsk_modulation_info: FskModulationInfo
    lr_fhss_modulation_info: LrFhssModulationInfo
    def __init__(self, frequency: _Optional[int] = ..., modulation: _Optional[_Union[_common_pb2.Modulation, str]] = ..., lora_modulation_info: _Optional[_Union[LoraModulationInfo, _Mapping]] = ..., fsk_modulation_info: _Optional[_Union[FskModulationInfo, _Mapping]] = ..., lr_fhss_modulation_info: _Optional[_Union[LrFhssModulationInfo, _Mapping]] = ...) -> None: ...

class UplinkTxInfo(_message.Message):
    __slots__ = ("frequency", "modulation")
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    MODULATION_FIELD_NUMBER: _ClassVar[int]
    frequency: int
    modulation: Modulation
    def __init__(self, frequency: _Optional[int] = ..., modulation: _Optional[_Union[Modulation, _Mapping]] = ...) -> None: ...

class LoraModulationInfo(_message.Message):
    __slots__ = ("bandwidth", "spreading_factor", "code_rate_legacy", "code_rate", "polarization_inversion", "preamble", "no_crc")
    BANDWIDTH_FIELD_NUMBER: _ClassVar[int]
    SPREADING_FACTOR_FIELD_NUMBER: _ClassVar[int]
    CODE_RATE_LEGACY_FIELD_NUMBER: _ClassVar[int]
    CODE_RATE_FIELD_NUMBER: _ClassVar[int]
    POLARIZATION_INVERSION_FIELD_NUMBER: _ClassVar[int]
    PREAMBLE_FIELD_NUMBER: _ClassVar[int]
    NO_CRC_FIELD_NUMBER: _ClassVar[int]
    bandwidth: int
    spreading_factor: int
    code_rate_legacy: str
    code_rate: CodeRate
    polarization_inversion: bool
    preamble: int
    no_crc: bool
    def __init__(self, bandwidth: _Optional[int] = ..., spreading_factor: _Optional[int] = ..., code_rate_legacy: _Optional[str] = ..., code_rate: _Optional[_Union[CodeRate, str]] = ..., polarization_inversion: bool = ..., preamble: _Optional[int] = ..., no_crc: bool = ...) -> None: ...

class FskModulationInfo(_message.Message):
    __slots__ = ("frequency_deviation", "datarate")
    FREQUENCY_DEVIATION_FIELD_NUMBER: _ClassVar[int]
    DATARATE_FIELD_NUMBER: _ClassVar[int]
    frequency_deviation: int
    datarate: int
    def __init__(self, frequency_deviation: _Optional[int] = ..., datarate: _Optional[int] = ...) -> None: ...

class LrFhssModulationInfo(_message.Message):
    __slots__ = ("operating_channel_width", "code_rate_legacy", "code_rate", "grid_steps")
    OPERATING_CHANNEL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    CODE_RATE_LEGACY_FIELD_NUMBER: _ClassVar[int]
    CODE_RATE_FIELD_NUMBER: _ClassVar[int]
    GRID_STEPS_FIELD_NUMBER: _ClassVar[int]
    operating_channel_width: int
    code_rate_legacy: str
    code_rate: CodeRate
    grid_steps: int
    def __init__(self, operating_channel_width: _Optional[int] = ..., code_rate_legacy: _Optional[str] = ..., code_rate: _Optional[_Union[CodeRate, str]] = ..., grid_steps: _Optional[int] = ...) -> None: ...

class EncryptedFineTimestamp(_message.Message):
    __slots__ = ("aes_key_index", "encrypted_ns", "fpga_id")
    AES_KEY_INDEX_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTED_NS_FIELD_NUMBER: _ClassVar[int]
    FPGA_ID_FIELD_NUMBER: _ClassVar[int]
    aes_key_index: int
    encrypted_ns: bytes
    fpga_id: bytes
    def __init__(self, aes_key_index: _Optional[int] = ..., encrypted_ns: _Optional[bytes] = ..., fpga_id: _Optional[bytes] = ...) -> None: ...

class PlainFineTimestamp(_message.Message):
    __slots__ = ("time",)
    TIME_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    def __init__(self, time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GatewayStats(_message.Message):
    __slots__ = ("gateway_id_legacy", "gateway_id", "time", "location", "config_version", "rx_packets_received", "rx_packets_received_ok", "tx_packets_received", "tx_packets_emitted", "metadata", "tx_packets_per_frequency", "rx_packets_per_frequency", "tx_packets_per_modulation", "rx_packets_per_modulation", "tx_packets_per_status", "duty_cycle_stats")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class TxPacketsPerFrequencyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    class RxPacketsPerFrequencyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    class TxPacketsPerStatusEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    GATEWAY_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    CONFIG_VERSION_FIELD_NUMBER: _ClassVar[int]
    RX_PACKETS_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    RX_PACKETS_RECEIVED_OK_FIELD_NUMBER: _ClassVar[int]
    TX_PACKETS_RECEIVED_FIELD_NUMBER: _ClassVar[int]
    TX_PACKETS_EMITTED_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TX_PACKETS_PER_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    RX_PACKETS_PER_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    TX_PACKETS_PER_MODULATION_FIELD_NUMBER: _ClassVar[int]
    RX_PACKETS_PER_MODULATION_FIELD_NUMBER: _ClassVar[int]
    TX_PACKETS_PER_STATUS_FIELD_NUMBER: _ClassVar[int]
    DUTY_CYCLE_STATS_FIELD_NUMBER: _ClassVar[int]
    gateway_id_legacy: bytes
    gateway_id: str
    time: _timestamp_pb2.Timestamp
    location: _common_pb2.Location
    config_version: str
    rx_packets_received: int
    rx_packets_received_ok: int
    tx_packets_received: int
    tx_packets_emitted: int
    metadata: _containers.ScalarMap[str, str]
    tx_packets_per_frequency: _containers.ScalarMap[int, int]
    rx_packets_per_frequency: _containers.ScalarMap[int, int]
    tx_packets_per_modulation: _containers.RepeatedCompositeFieldContainer[PerModulationCount]
    rx_packets_per_modulation: _containers.RepeatedCompositeFieldContainer[PerModulationCount]
    tx_packets_per_status: _containers.ScalarMap[str, int]
    duty_cycle_stats: DutyCycleStats
    def __init__(self, gateway_id_legacy: _Optional[bytes] = ..., gateway_id: _Optional[str] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., location: _Optional[_Union[_common_pb2.Location, _Mapping]] = ..., config_version: _Optional[str] = ..., rx_packets_received: _Optional[int] = ..., rx_packets_received_ok: _Optional[int] = ..., tx_packets_received: _Optional[int] = ..., tx_packets_emitted: _Optional[int] = ..., metadata: _Optional[_Mapping[str, str]] = ..., tx_packets_per_frequency: _Optional[_Mapping[int, int]] = ..., rx_packets_per_frequency: _Optional[_Mapping[int, int]] = ..., tx_packets_per_modulation: _Optional[_Iterable[_Union[PerModulationCount, _Mapping]]] = ..., rx_packets_per_modulation: _Optional[_Iterable[_Union[PerModulationCount, _Mapping]]] = ..., tx_packets_per_status: _Optional[_Mapping[str, int]] = ..., duty_cycle_stats: _Optional[_Union[DutyCycleStats, _Mapping]] = ...) -> None: ...

class PerModulationCount(_message.Message):
    __slots__ = ("modulation", "count")
    MODULATION_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    modulation: Modulation
    count: int
    def __init__(self, modulation: _Optional[_Union[Modulation, _Mapping]] = ..., count: _Optional[int] = ...) -> None: ...

class DutyCycleStats(_message.Message):
    __slots__ = ("regulation", "window", "bands")
    REGULATION_FIELD_NUMBER: _ClassVar[int]
    WINDOW_FIELD_NUMBER: _ClassVar[int]
    BANDS_FIELD_NUMBER: _ClassVar[int]
    regulation: _common_pb2.Regulation
    window: _duration_pb2.Duration
    bands: _containers.RepeatedCompositeFieldContainer[DutyCycleBand]
    def __init__(self, regulation: _Optional[_Union[_common_pb2.Regulation, str]] = ..., window: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., bands: _Optional[_Iterable[_Union[DutyCycleBand, _Mapping]]] = ...) -> None: ...

class DutyCycleBand(_message.Message):
    __slots__ = ("name", "frequency_min", "frequency_max", "load_max", "load_tracked")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_MIN_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_MAX_FIELD_NUMBER: _ClassVar[int]
    LOAD_MAX_FIELD_NUMBER: _ClassVar[int]
    LOAD_TRACKED_FIELD_NUMBER: _ClassVar[int]
    name: str
    frequency_min: int
    frequency_max: int
    load_max: _duration_pb2.Duration
    load_tracked: _duration_pb2.Duration
    def __init__(self, name: _Optional[str] = ..., frequency_min: _Optional[int] = ..., frequency_max: _Optional[int] = ..., load_max: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., load_tracked: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class UplinkRxInfoLegacy(_message.Message):
    __slots__ = ("gateway_id", "time", "time_since_gps_epoch", "rssi", "lora_snr", "channel", "rf_chain", "board", "antenna", "location", "fine_timestamp_type", "encrypted_fine_timestamp", "plain_fine_timestamp", "context", "uplink_id", "crc_status", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    TIME_SINCE_GPS_EPOCH_FIELD_NUMBER: _ClassVar[int]
    RSSI_FIELD_NUMBER: _ClassVar[int]
    LORA_SNR_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    RF_CHAIN_FIELD_NUMBER: _ClassVar[int]
    BOARD_FIELD_NUMBER: _ClassVar[int]
    ANTENNA_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    FINE_TIMESTAMP_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTED_FINE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PLAIN_FINE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    UPLINK_ID_FIELD_NUMBER: _ClassVar[int]
    CRC_STATUS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    gateway_id: bytes
    time: _timestamp_pb2.Timestamp
    time_since_gps_epoch: _duration_pb2.Duration
    rssi: int
    lora_snr: float
    channel: int
    rf_chain: int
    board: int
    antenna: int
    location: _common_pb2.Location
    fine_timestamp_type: FineTimestampType
    encrypted_fine_timestamp: EncryptedFineTimestamp
    plain_fine_timestamp: PlainFineTimestamp
    context: bytes
    uplink_id: bytes
    crc_status: CRCStatus
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, gateway_id: _Optional[bytes] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., time_since_gps_epoch: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., rssi: _Optional[int] = ..., lora_snr: _Optional[float] = ..., channel: _Optional[int] = ..., rf_chain: _Optional[int] = ..., board: _Optional[int] = ..., antenna: _Optional[int] = ..., location: _Optional[_Union[_common_pb2.Location, _Mapping]] = ..., fine_timestamp_type: _Optional[_Union[FineTimestampType, str]] = ..., encrypted_fine_timestamp: _Optional[_Union[EncryptedFineTimestamp, _Mapping]] = ..., plain_fine_timestamp: _Optional[_Union[PlainFineTimestamp, _Mapping]] = ..., context: _Optional[bytes] = ..., uplink_id: _Optional[bytes] = ..., crc_status: _Optional[_Union[CRCStatus, str]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UplinkRxInfo(_message.Message):
    __slots__ = ("gateway_id", "uplink_id", "gw_time", "ns_time", "time_since_gps_epoch", "fine_time_since_gps_epoch", "rssi", "snr", "channel", "rf_chain", "board", "antenna", "location", "context", "metadata", "crc_status")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    UPLINK_ID_FIELD_NUMBER: _ClassVar[int]
    GW_TIME_FIELD_NUMBER: _ClassVar[int]
    NS_TIME_FIELD_NUMBER: _ClassVar[int]
    TIME_SINCE_GPS_EPOCH_FIELD_NUMBER: _ClassVar[int]
    FINE_TIME_SINCE_GPS_EPOCH_FIELD_NUMBER: _ClassVar[int]
    RSSI_FIELD_NUMBER: _ClassVar[int]
    SNR_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    RF_CHAIN_FIELD_NUMBER: _ClassVar[int]
    BOARD_FIELD_NUMBER: _ClassVar[int]
    ANTENNA_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CRC_STATUS_FIELD_NUMBER: _ClassVar[int]
    gateway_id: str
    uplink_id: int
    gw_time: _timestamp_pb2.Timestamp
    ns_time: _timestamp_pb2.Timestamp
    time_since_gps_epoch: _duration_pb2.Duration
    fine_time_since_gps_epoch: _duration_pb2.Duration
    rssi: int
    snr: float
    channel: int
    rf_chain: int
    board: int
    antenna: int
    location: _common_pb2.Location
    context: bytes
    metadata: _containers.ScalarMap[str, str]
    crc_status: CRCStatus
    def __init__(self, gateway_id: _Optional[str] = ..., uplink_id: _Optional[int] = ..., gw_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., ns_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., time_since_gps_epoch: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., fine_time_since_gps_epoch: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., rssi: _Optional[int] = ..., snr: _Optional[float] = ..., channel: _Optional[int] = ..., rf_chain: _Optional[int] = ..., board: _Optional[int] = ..., antenna: _Optional[int] = ..., location: _Optional[_Union[_common_pb2.Location, _Mapping]] = ..., context: _Optional[bytes] = ..., metadata: _Optional[_Mapping[str, str]] = ..., crc_status: _Optional[_Union[CRCStatus, str]] = ...) -> None: ...

class DownlinkTxInfoLegacy(_message.Message):
    __slots__ = ("gateway_id", "frequency", "power", "modulation", "lora_modulation_info", "fsk_modulation_info", "board", "antenna", "timing", "immediately_timing_info", "delay_timing_info", "gps_epoch_timing_info", "context")
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    MODULATION_FIELD_NUMBER: _ClassVar[int]
    LORA_MODULATION_INFO_FIELD_NUMBER: _ClassVar[int]
    FSK_MODULATION_INFO_FIELD_NUMBER: _ClassVar[int]
    BOARD_FIELD_NUMBER: _ClassVar[int]
    ANTENNA_FIELD_NUMBER: _ClassVar[int]
    TIMING_FIELD_NUMBER: _ClassVar[int]
    IMMEDIATELY_TIMING_INFO_FIELD_NUMBER: _ClassVar[int]
    DELAY_TIMING_INFO_FIELD_NUMBER: _ClassVar[int]
    GPS_EPOCH_TIMING_INFO_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    gateway_id: bytes
    frequency: int
    power: int
    modulation: _common_pb2.Modulation
    lora_modulation_info: LoraModulationInfo
    fsk_modulation_info: FskModulationInfo
    board: int
    antenna: int
    timing: DownlinkTiming
    immediately_timing_info: ImmediatelyTimingInfo
    delay_timing_info: DelayTimingInfo
    gps_epoch_timing_info: GPSEpochTimingInfo
    context: bytes
    def __init__(self, gateway_id: _Optional[bytes] = ..., frequency: _Optional[int] = ..., power: _Optional[int] = ..., modulation: _Optional[_Union[_common_pb2.Modulation, str]] = ..., lora_modulation_info: _Optional[_Union[LoraModulationInfo, _Mapping]] = ..., fsk_modulation_info: _Optional[_Union[FskModulationInfo, _Mapping]] = ..., board: _Optional[int] = ..., antenna: _Optional[int] = ..., timing: _Optional[_Union[DownlinkTiming, str]] = ..., immediately_timing_info: _Optional[_Union[ImmediatelyTimingInfo, _Mapping]] = ..., delay_timing_info: _Optional[_Union[DelayTimingInfo, _Mapping]] = ..., gps_epoch_timing_info: _Optional[_Union[GPSEpochTimingInfo, _Mapping]] = ..., context: _Optional[bytes] = ...) -> None: ...

class DownlinkTxInfo(_message.Message):
    __slots__ = ("frequency", "power", "modulation", "board", "antenna", "timing", "context")
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    MODULATION_FIELD_NUMBER: _ClassVar[int]
    BOARD_FIELD_NUMBER: _ClassVar[int]
    ANTENNA_FIELD_NUMBER: _ClassVar[int]
    TIMING_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    frequency: int
    power: int
    modulation: Modulation
    board: int
    antenna: int
    timing: Timing
    context: bytes
    def __init__(self, frequency: _Optional[int] = ..., power: _Optional[int] = ..., modulation: _Optional[_Union[Modulation, _Mapping]] = ..., board: _Optional[int] = ..., antenna: _Optional[int] = ..., timing: _Optional[_Union[Timing, _Mapping]] = ..., context: _Optional[bytes] = ...) -> None: ...

class Timing(_message.Message):
    __slots__ = ("immediately", "delay", "gps_epoch")
    IMMEDIATELY_FIELD_NUMBER: _ClassVar[int]
    DELAY_FIELD_NUMBER: _ClassVar[int]
    GPS_EPOCH_FIELD_NUMBER: _ClassVar[int]
    immediately: ImmediatelyTimingInfo
    delay: DelayTimingInfo
    gps_epoch: GPSEpochTimingInfo
    def __init__(self, immediately: _Optional[_Union[ImmediatelyTimingInfo, _Mapping]] = ..., delay: _Optional[_Union[DelayTimingInfo, _Mapping]] = ..., gps_epoch: _Optional[_Union[GPSEpochTimingInfo, _Mapping]] = ...) -> None: ...

class ImmediatelyTimingInfo(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DelayTimingInfo(_message.Message):
    __slots__ = ("delay",)
    DELAY_FIELD_NUMBER: _ClassVar[int]
    delay: _duration_pb2.Duration
    def __init__(self, delay: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class GPSEpochTimingInfo(_message.Message):
    __slots__ = ("time_since_gps_epoch",)
    TIME_SINCE_GPS_EPOCH_FIELD_NUMBER: _ClassVar[int]
    time_since_gps_epoch: _duration_pb2.Duration
    def __init__(self, time_since_gps_epoch: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class UplinkFrame(_message.Message):
    __slots__ = ("phy_payload", "tx_info_legacy", "rx_info_legacy", "tx_info", "rx_info")
    PHY_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    TX_INFO_LEGACY_FIELD_NUMBER: _ClassVar[int]
    RX_INFO_LEGACY_FIELD_NUMBER: _ClassVar[int]
    TX_INFO_FIELD_NUMBER: _ClassVar[int]
    RX_INFO_FIELD_NUMBER: _ClassVar[int]
    phy_payload: bytes
    tx_info_legacy: UplinkTxInfoLegacy
    rx_info_legacy: UplinkRxInfoLegacy
    tx_info: UplinkTxInfo
    rx_info: UplinkRxInfo
    def __init__(self, phy_payload: _Optional[bytes] = ..., tx_info_legacy: _Optional[_Union[UplinkTxInfoLegacy, _Mapping]] = ..., rx_info_legacy: _Optional[_Union[UplinkRxInfoLegacy, _Mapping]] = ..., tx_info: _Optional[_Union[UplinkTxInfo, _Mapping]] = ..., rx_info: _Optional[_Union[UplinkRxInfo, _Mapping]] = ...) -> None: ...

class UplinkFrameSet(_message.Message):
    __slots__ = ("phy_payload", "tx_info", "rx_info")
    PHY_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    TX_INFO_FIELD_NUMBER: _ClassVar[int]
    RX_INFO_FIELD_NUMBER: _ClassVar[int]
    phy_payload: bytes
    tx_info: UplinkTxInfo
    rx_info: _containers.RepeatedCompositeFieldContainer[UplinkRxInfo]
    def __init__(self, phy_payload: _Optional[bytes] = ..., tx_info: _Optional[_Union[UplinkTxInfo, _Mapping]] = ..., rx_info: _Optional[_Iterable[_Union[UplinkRxInfo, _Mapping]]] = ...) -> None: ...

class DownlinkFrame(_message.Message):
    __slots__ = ("downlink_id", "downlink_id_legacy", "items", "gateway_id_legacy", "gateway_id")
    DOWNLINK_ID_FIELD_NUMBER: _ClassVar[int]
    DOWNLINK_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    downlink_id: int
    downlink_id_legacy: bytes
    items: _containers.RepeatedCompositeFieldContainer[DownlinkFrameItem]
    gateway_id_legacy: bytes
    gateway_id: str
    def __init__(self, downlink_id: _Optional[int] = ..., downlink_id_legacy: _Optional[bytes] = ..., items: _Optional[_Iterable[_Union[DownlinkFrameItem, _Mapping]]] = ..., gateway_id_legacy: _Optional[bytes] = ..., gateway_id: _Optional[str] = ...) -> None: ...

class DownlinkFrameItem(_message.Message):
    __slots__ = ("phy_payload", "tx_info_legacy", "tx_info")
    PHY_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    TX_INFO_LEGACY_FIELD_NUMBER: _ClassVar[int]
    TX_INFO_FIELD_NUMBER: _ClassVar[int]
    phy_payload: bytes
    tx_info_legacy: DownlinkTxInfoLegacy
    tx_info: DownlinkTxInfo
    def __init__(self, phy_payload: _Optional[bytes] = ..., tx_info_legacy: _Optional[_Union[DownlinkTxInfoLegacy, _Mapping]] = ..., tx_info: _Optional[_Union[DownlinkTxInfo, _Mapping]] = ...) -> None: ...

class DownlinkTxAck(_message.Message):
    __slots__ = ("gateway_id_legacy", "gateway_id", "downlink_id", "downlink_id_legacy", "items")
    GATEWAY_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    DOWNLINK_ID_FIELD_NUMBER: _ClassVar[int]
    DOWNLINK_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    gateway_id_legacy: bytes
    gateway_id: str
    downlink_id: int
    downlink_id_legacy: bytes
    items: _containers.RepeatedCompositeFieldContainer[DownlinkTxAckItem]
    def __init__(self, gateway_id_legacy: _Optional[bytes] = ..., gateway_id: _Optional[str] = ..., downlink_id: _Optional[int] = ..., downlink_id_legacy: _Optional[bytes] = ..., items: _Optional[_Iterable[_Union[DownlinkTxAckItem, _Mapping]]] = ...) -> None: ...

class DownlinkTxAckItem(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: TxAckStatus
    def __init__(self, status: _Optional[_Union[TxAckStatus, str]] = ...) -> None: ...

class GatewayConfiguration(_message.Message):
    __slots__ = ("gateway_id_legacy", "gateway_id", "version", "channels", "stats_interval")
    GATEWAY_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    STATS_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    gateway_id_legacy: bytes
    gateway_id: str
    version: str
    channels: _containers.RepeatedCompositeFieldContainer[ChannelConfiguration]
    stats_interval: _duration_pb2.Duration
    def __init__(self, gateway_id_legacy: _Optional[bytes] = ..., gateway_id: _Optional[str] = ..., version: _Optional[str] = ..., channels: _Optional[_Iterable[_Union[ChannelConfiguration, _Mapping]]] = ..., stats_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class GetGatewayIdRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetGatewayIdResponse(_message.Message):
    __slots__ = ("gateway_id",)
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    gateway_id: str
    def __init__(self, gateway_id: _Optional[str] = ...) -> None: ...

class GetLocationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetLocationResponse(_message.Message):
    __slots__ = ("location", "updated_at")
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    location: _common_pb2.Location
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, location: _Optional[_Union[_common_pb2.Location, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ChannelConfiguration(_message.Message):
    __slots__ = ("frequency", "modulation_legacy", "lora_modulation_config", "fsk_modulation_config", "board", "demodulator")
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    MODULATION_LEGACY_FIELD_NUMBER: _ClassVar[int]
    LORA_MODULATION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FSK_MODULATION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    BOARD_FIELD_NUMBER: _ClassVar[int]
    DEMODULATOR_FIELD_NUMBER: _ClassVar[int]
    frequency: int
    modulation_legacy: _common_pb2.Modulation
    lora_modulation_config: LoraModulationConfig
    fsk_modulation_config: FskModulationConfig
    board: int
    demodulator: int
    def __init__(self, frequency: _Optional[int] = ..., modulation_legacy: _Optional[_Union[_common_pb2.Modulation, str]] = ..., lora_modulation_config: _Optional[_Union[LoraModulationConfig, _Mapping]] = ..., fsk_modulation_config: _Optional[_Union[FskModulationConfig, _Mapping]] = ..., board: _Optional[int] = ..., demodulator: _Optional[int] = ...) -> None: ...

class LoraModulationConfig(_message.Message):
    __slots__ = ("bandwidth_legacy", "bandwidth", "spreading_factors")
    BANDWIDTH_LEGACY_FIELD_NUMBER: _ClassVar[int]
    BANDWIDTH_FIELD_NUMBER: _ClassVar[int]
    SPREADING_FACTORS_FIELD_NUMBER: _ClassVar[int]
    bandwidth_legacy: int
    bandwidth: int
    spreading_factors: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, bandwidth_legacy: _Optional[int] = ..., bandwidth: _Optional[int] = ..., spreading_factors: _Optional[_Iterable[int]] = ...) -> None: ...

class FskModulationConfig(_message.Message):
    __slots__ = ("bandwidth_legacy", "bandwidth", "bitrate")
    BANDWIDTH_LEGACY_FIELD_NUMBER: _ClassVar[int]
    BANDWIDTH_FIELD_NUMBER: _ClassVar[int]
    BITRATE_FIELD_NUMBER: _ClassVar[int]
    bandwidth_legacy: int
    bandwidth: int
    bitrate: int
    def __init__(self, bandwidth_legacy: _Optional[int] = ..., bandwidth: _Optional[int] = ..., bitrate: _Optional[int] = ...) -> None: ...

class GatewayCommandExecRequest(_message.Message):
    __slots__ = ("gateway_id_legacy", "gateway_id", "command", "exec_id", "stdin", "environment")
    class EnvironmentEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    GATEWAY_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    EXEC_ID_FIELD_NUMBER: _ClassVar[int]
    STDIN_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    gateway_id_legacy: bytes
    gateway_id: str
    command: str
    exec_id: int
    stdin: bytes
    environment: _containers.ScalarMap[str, str]
    def __init__(self, gateway_id_legacy: _Optional[bytes] = ..., gateway_id: _Optional[str] = ..., command: _Optional[str] = ..., exec_id: _Optional[int] = ..., stdin: _Optional[bytes] = ..., environment: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GatewayCommandExecResponse(_message.Message):
    __slots__ = ("gateway_id_legacy", "gateway_id", "exec_id", "stdout", "stderr", "error")
    GATEWAY_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    EXEC_ID_FIELD_NUMBER: _ClassVar[int]
    STDOUT_FIELD_NUMBER: _ClassVar[int]
    STDERR_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    gateway_id_legacy: bytes
    gateway_id: str
    exec_id: int
    stdout: bytes
    stderr: bytes
    error: str
    def __init__(self, gateway_id_legacy: _Optional[bytes] = ..., gateway_id: _Optional[str] = ..., exec_id: _Optional[int] = ..., stdout: _Optional[bytes] = ..., stderr: _Optional[bytes] = ..., error: _Optional[str] = ...) -> None: ...

class RawPacketForwarderEvent(_message.Message):
    __slots__ = ("gateway_id_legacy", "gateway_id", "payload")
    GATEWAY_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    gateway_id_legacy: bytes
    gateway_id: str
    payload: bytes
    def __init__(self, gateway_id_legacy: _Optional[bytes] = ..., gateway_id: _Optional[str] = ..., payload: _Optional[bytes] = ...) -> None: ...

class RawPacketForwarderCommand(_message.Message):
    __slots__ = ("gateway_id_legacy", "gateway_id", "payload")
    GATEWAY_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    gateway_id_legacy: bytes
    gateway_id: str
    payload: bytes
    def __init__(self, gateway_id_legacy: _Optional[bytes] = ..., gateway_id: _Optional[str] = ..., payload: _Optional[bytes] = ...) -> None: ...

class ConnState(_message.Message):
    __slots__ = ("gateway_id_legacy", "gateway_id", "state")
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OFFLINE: _ClassVar[ConnState.State]
        ONLINE: _ClassVar[ConnState.State]
    OFFLINE: ConnState.State
    ONLINE: ConnState.State
    GATEWAY_ID_LEGACY_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    gateway_id_legacy: bytes
    gateway_id: str
    state: ConnState.State
    def __init__(self, gateway_id_legacy: _Optional[bytes] = ..., gateway_id: _Optional[str] = ..., state: _Optional[_Union[ConnState.State, str]] = ...) -> None: ...

class MeshEventHeartbeat(_message.Message):
    __slots__ = ("relay_path",)
    RELAY_PATH_FIELD_NUMBER: _ClassVar[int]
    relay_path: _containers.RepeatedCompositeFieldContainer[MeshEventHeartbeatRelayPath]
    def __init__(self, relay_path: _Optional[_Iterable[_Union[MeshEventHeartbeatRelayPath, _Mapping]]] = ...) -> None: ...

class MeshEventHeartbeatRelayPath(_message.Message):
    __slots__ = ("relay_id", "rssi", "snr")
    RELAY_ID_FIELD_NUMBER: _ClassVar[int]
    RSSI_FIELD_NUMBER: _ClassVar[int]
    SNR_FIELD_NUMBER: _ClassVar[int]
    relay_id: str
    rssi: int
    snr: int
    def __init__(self, relay_id: _Optional[str] = ..., rssi: _Optional[int] = ..., snr: _Optional[int] = ...) -> None: ...

class MeshEventProprietary(_message.Message):
    __slots__ = ("event_type", "payload")
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    event_type: int
    payload: bytes
    def __init__(self, event_type: _Optional[int] = ..., payload: _Optional[bytes] = ...) -> None: ...

class MeshCommandProprietary(_message.Message):
    __slots__ = ("command_type", "payload")
    COMMAND_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    command_type: int
    payload: bytes
    def __init__(self, command_type: _Optional[int] = ..., payload: _Optional[bytes] = ...) -> None: ...
