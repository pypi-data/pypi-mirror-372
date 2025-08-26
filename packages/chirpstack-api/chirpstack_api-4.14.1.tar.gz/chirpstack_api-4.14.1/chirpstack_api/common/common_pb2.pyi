import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Modulation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LORA: _ClassVar[Modulation]
    FSK: _ClassVar[Modulation]
    LR_FHSS: _ClassVar[Modulation]

class Region(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EU868: _ClassVar[Region]
    US915: _ClassVar[Region]
    CN779: _ClassVar[Region]
    EU433: _ClassVar[Region]
    AU915: _ClassVar[Region]
    CN470: _ClassVar[Region]
    AS923: _ClassVar[Region]
    AS923_2: _ClassVar[Region]
    AS923_3: _ClassVar[Region]
    AS923_4: _ClassVar[Region]
    KR920: _ClassVar[Region]
    IN865: _ClassVar[Region]
    RU864: _ClassVar[Region]
    ISM2400: _ClassVar[Region]

class FType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOIN_REQUEST: _ClassVar[FType]
    JOIN_ACCEPT: _ClassVar[FType]
    UNCONFIRMED_DATA_UP: _ClassVar[FType]
    UNCONFIRMED_DATA_DOWN: _ClassVar[FType]
    CONFIRMED_DATA_UP: _ClassVar[FType]
    CONFIRMED_DATA_DOWN: _ClassVar[FType]
    REJOIN_REQUEST: _ClassVar[FType]
    PROPRIETARY: _ClassVar[FType]

class MacVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LORAWAN_1_0_0: _ClassVar[MacVersion]
    LORAWAN_1_0_1: _ClassVar[MacVersion]
    LORAWAN_1_0_2: _ClassVar[MacVersion]
    LORAWAN_1_0_3: _ClassVar[MacVersion]
    LORAWAN_1_0_4: _ClassVar[MacVersion]
    LORAWAN_1_1_0: _ClassVar[MacVersion]

class RegParamsRevision(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    A: _ClassVar[RegParamsRevision]
    B: _ClassVar[RegParamsRevision]
    RP002_1_0_0: _ClassVar[RegParamsRevision]
    RP002_1_0_1: _ClassVar[RegParamsRevision]
    RP002_1_0_2: _ClassVar[RegParamsRevision]
    RP002_1_0_3: _ClassVar[RegParamsRevision]
    RP002_1_0_4: _ClassVar[RegParamsRevision]

class LocationSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[LocationSource]
    GPS: _ClassVar[LocationSource]
    CONFIG: _ClassVar[LocationSource]
    GEO_RESOLVER_TDOA: _ClassVar[LocationSource]
    GEO_RESOLVER_RSSI: _ClassVar[LocationSource]
    GEO_RESOLVER_GNSS: _ClassVar[LocationSource]
    GEO_RESOLVER_WIFI: _ClassVar[LocationSource]

class Aggregation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HOUR: _ClassVar[Aggregation]
    DAY: _ClassVar[Aggregation]
    MONTH: _ClassVar[Aggregation]
    MINUTE: _ClassVar[Aggregation]

class MetricKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COUNTER: _ClassVar[MetricKind]
    ABSOLUTE: _ClassVar[MetricKind]
    GAUGE: _ClassVar[MetricKind]

class Regulation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REGULATION_UNKNOWN: _ClassVar[Regulation]
    ETSI_EN_300_220: _ClassVar[Regulation]

class DeviceClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLASS_A: _ClassVar[DeviceClass]
    CLASS_B: _ClassVar[DeviceClass]
    CLASS_C: _ClassVar[DeviceClass]
LORA: Modulation
FSK: Modulation
LR_FHSS: Modulation
EU868: Region
US915: Region
CN779: Region
EU433: Region
AU915: Region
CN470: Region
AS923: Region
AS923_2: Region
AS923_3: Region
AS923_4: Region
KR920: Region
IN865: Region
RU864: Region
ISM2400: Region
JOIN_REQUEST: FType
JOIN_ACCEPT: FType
UNCONFIRMED_DATA_UP: FType
UNCONFIRMED_DATA_DOWN: FType
CONFIRMED_DATA_UP: FType
CONFIRMED_DATA_DOWN: FType
REJOIN_REQUEST: FType
PROPRIETARY: FType
LORAWAN_1_0_0: MacVersion
LORAWAN_1_0_1: MacVersion
LORAWAN_1_0_2: MacVersion
LORAWAN_1_0_3: MacVersion
LORAWAN_1_0_4: MacVersion
LORAWAN_1_1_0: MacVersion
A: RegParamsRevision
B: RegParamsRevision
RP002_1_0_0: RegParamsRevision
RP002_1_0_1: RegParamsRevision
RP002_1_0_2: RegParamsRevision
RP002_1_0_3: RegParamsRevision
RP002_1_0_4: RegParamsRevision
UNKNOWN: LocationSource
GPS: LocationSource
CONFIG: LocationSource
GEO_RESOLVER_TDOA: LocationSource
GEO_RESOLVER_RSSI: LocationSource
GEO_RESOLVER_GNSS: LocationSource
GEO_RESOLVER_WIFI: LocationSource
HOUR: Aggregation
DAY: Aggregation
MONTH: Aggregation
MINUTE: Aggregation
COUNTER: MetricKind
ABSOLUTE: MetricKind
GAUGE: MetricKind
REGULATION_UNKNOWN: Regulation
ETSI_EN_300_220: Regulation
CLASS_A: DeviceClass
CLASS_B: DeviceClass
CLASS_C: DeviceClass

class Location(_message.Message):
    __slots__ = ("latitude", "longitude", "altitude", "source", "accuracy")
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    latitude: float
    longitude: float
    altitude: float
    source: LocationSource
    accuracy: float
    def __init__(self, latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., altitude: _Optional[float] = ..., source: _Optional[_Union[LocationSource, str]] = ..., accuracy: _Optional[float] = ...) -> None: ...

class KeyEnvelope(_message.Message):
    __slots__ = ("kek_label", "aes_key")
    KEK_LABEL_FIELD_NUMBER: _ClassVar[int]
    AES_KEY_FIELD_NUMBER: _ClassVar[int]
    kek_label: str
    aes_key: bytes
    def __init__(self, kek_label: _Optional[str] = ..., aes_key: _Optional[bytes] = ...) -> None: ...

class Metric(_message.Message):
    __slots__ = ("name", "timestamps", "datasets", "kind")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    DATASETS_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    name: str
    timestamps: _containers.RepeatedCompositeFieldContainer[_timestamp_pb2.Timestamp]
    datasets: _containers.RepeatedCompositeFieldContainer[MetricDataset]
    kind: MetricKind
    def __init__(self, name: _Optional[str] = ..., timestamps: _Optional[_Iterable[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]] = ..., datasets: _Optional[_Iterable[_Union[MetricDataset, _Mapping]]] = ..., kind: _Optional[_Union[MetricKind, str]] = ...) -> None: ...

class MetricDataset(_message.Message):
    __slots__ = ("label", "data")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    label: str
    data: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, label: _Optional[str] = ..., data: _Optional[_Iterable[float]] = ...) -> None: ...

class JoinServerContext(_message.Message):
    __slots__ = ("session_key_id", "app_s_key")
    SESSION_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    APP_S_KEY_FIELD_NUMBER: _ClassVar[int]
    session_key_id: str
    app_s_key: KeyEnvelope
    def __init__(self, session_key_id: _Optional[str] = ..., app_s_key: _Optional[_Union[KeyEnvelope, _Mapping]] = ...) -> None: ...
