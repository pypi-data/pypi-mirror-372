"""
compact_binary_protocol

A small, self-contained Python library that defines the compact binary protocol
used by Tartabit client components. It provides:
- Encoding helpers
- Data model classes for location and sensor data
- Packet classes for telemetry/configuration/power/motion events
- Decoding helpers for responses and header parsing

All multi-byte values are encoded using big-endian format.
"""

from .encoding import encode_var_string
from .decoder import PacketDecoder, DataReader
from .data import (
    LocationData,
    SensorData,
    SensorMultiData,
    NullSensorData,
    MotionSensorData,
)
from .packets import (
    Packet,
    TelemetryPacket,
    ConfigPacket,
    PowerOnPacket,
    MotionStartPacket,
    MotionStopPacket,
)

__all__ = [
    'encode_var_string',
    'PacketDecoder', 'DataReader',
    'LocationData', 'SensorData', 'SensorMultiData', 'NullSensorData', 'MotionSensorData',
    'Packet', 'TelemetryPacket', 'ConfigPacket', 'PowerOnPacket', 'MotionStartPacket', 'MotionStopPacket',
]
