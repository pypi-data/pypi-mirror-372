import struct

from .encoding import encode_var_string

class Packet:
    def __init__(self, command, imei, transaction_id=0, version=1):
        # Ensure command is exactly 2 characters (pad or truncate)
        if len(command) == 1:
            self.command = command + '\0'
        elif len(command) >= 2:
            self.command = command[:2]
        else:
            self.command = '\0\0'
        self.imei = imei
        self.transaction_id = transaction_id
        self.version = version

    @staticmethod
    def _encode_imei_bcd(imei_str: str) -> bytes:
        digits = ''.join(ch for ch in imei_str if ch.isdigit())
        if len(digits) == 0:
            return b"\x00" * 8
        if len(digits) % 2 == 1:
            digits = '0' + digits
        b = bytearray()
        for i in range(0, len(digits), 2):
            low = int(digits[i+1])
            high = int(digits[i])
            b.append((high << 4) | low)
        if len(b) < 8:
            b.extend(b"\x00" * (8 - len(b)))
        elif len(b) > 8:
            b = b[:8]
        return bytes(b)

    def build_header(self):
        imei_bytes = Packet._encode_imei_bcd(self.imei)
        header = struct.pack('>BBBH',
                             self.version,
                             ord(self.command[0]),
                             ord(self.command[1]),
                             self.transaction_id) + imei_bytes
        return header

    def to_bytes(self):
        raise NotImplementedError()

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)


class TelemetryPacket(Packet):
    def __init__(self, imei, timestamp, transaction_id, location_data, sensor_data):
        super().__init__('T', imei, transaction_id, 1)
        self.timestamp = timestamp
        self.location_data = location_data
        self.sensor_data = sensor_data

    def to_bytes(self):
        header = self.build_header()
        loc_bytes = self.location_data.to_bytes()
        sensor_bytes = self.sensor_data.to_bytes()
        sensor_count = struct.pack('>B', 1)
        data = struct.pack('>I', int(self.timestamp)) + loc_bytes + sensor_count + sensor_bytes
        return header + data

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Location: {self.location_data.describe()}")
        try:
            sensor_str = self.sensor_data.describe()
        except Exception:
            sensor_str = str(self.sensor_data)
        print(f"  Sensors: {sensor_str}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)


class ConfigPacket(Packet):
    def __init__(self, imei, server_address, reporting_interval, reading_interval, transaction_id=0):
        super().__init__('C', imei, transaction_id)
        self.server_address = server_address
        self.reporting_interval = int(reporting_interval)
        self.reading_interval = int(reading_interval)

    def to_bytes(self):
        header = self.build_header()
        address_with_length = encode_var_string(self.server_address)
        data = address_with_length + struct.pack('>II', self.reporting_interval, self.reading_interval)
        return header + data

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Server: {self.server_address}")
        print(f"  Reporting Interval: {self.reporting_interval} seconds")
        print(f"  Reading Interval: {self.reading_interval} seconds")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)


class PowerOnPacket(Packet):
    def __init__(self, imei, transaction_id, customer_id, software_version, modem_version, mcc, mnc, rat):
        super().__init__('P+', imei, transaction_id, 1)
        self.customer_id = customer_id
        self.software_version = software_version
        self.modem_version = modem_version
        self.mcc = mcc
        self.mnc = mnc
        self.rat = rat

    def to_bytes(self):
        header = self.build_header()
        cid_bytes = b""
        try:
            if isinstance(self.customer_id, str):
                hex_str = self.customer_id.strip().lower()
                if hex_str.startswith('0x'):
                    hex_str = hex_str[2:]
                if len(hex_str) % 2 != 0:
                    raise ValueError("customer_id hex must have even length")
                cid_bytes = bytes.fromhex(hex_str) if hex_str else b""
            elif isinstance(self.customer_id, (bytes, bytearray)):
                cid_bytes = bytes(self.customer_id)
        except Exception as e:
            print(f"Warning: invalid customer_id '{self.customer_id}': {e}. Using zero-length.")
            cid_bytes = b""
        if len(cid_bytes) > 255:
            print(f"Warning: customer_id too long ({len(cid_bytes)} bytes). Truncating to 255 bytes.")
            cid_bytes = cid_bytes[:255]
        customer_id_with_length = struct.pack('>B', len(cid_bytes)) + cid_bytes
        software_version_with_length = encode_var_string(self.software_version)
        modem_version_with_length = encode_var_string(self.modem_version)
        mcc_with_length = encode_var_string(self.mcc)
        mnc_with_length = encode_var_string(self.mnc)
        rat_with_length = encode_var_string(self.rat)
        data = customer_id_with_length + software_version_with_length + modem_version_with_length + mcc_with_length + mnc_with_length + rat_with_length
        return header + data

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Software Version: {self.software_version}")
        print(f"  Modem Version: {self.modem_version}")
        print(f"  Network: MCC:{self.mcc}, MNC:{self.mnc}, RAT:{self.rat}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)


class MotionStartPacket(Packet):
    def __init__(self, imei, timestamp, transaction_id, location_data, sensor_data):
        super().__init__('M+', imei, transaction_id, 1)
        self.timestamp = int(timestamp)
        self.location_data = location_data
        self.sensor_data = sensor_data

    def to_bytes(self):
        header = self.build_header()
        loc_bytes = self.location_data.to_bytes()
        sensor_bytes = self.sensor_data.to_bytes()
        sensor_count = struct.pack('>B', 1)
        body = struct.pack('>I', self.timestamp) + loc_bytes + sensor_count + sensor_bytes
        return header + body

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Location: {self.location_data.describe()}")
        try:
            sensor_str = self.sensor_data.describe()
        except Exception:
            sensor_str = str(self.sensor_data)
        print(f"  Sensors: {sensor_str}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)


class MotionStopPacket(Packet):
    def __init__(self, imei, timestamp, transaction_id, location_data, sensor_data):
        super().__init__('M-', imei, transaction_id, 1)
        self.timestamp = int(timestamp)
        self.location_data = location_data
        self.sensor_data = sensor_data

    def to_bytes(self):
        header = self.build_header()
        loc_bytes = self.location_data.to_bytes()
        sensor_bytes = self.sensor_data.to_bytes()
        sensor_count = struct.pack('>B', 1)
        body = struct.pack('>I', self.timestamp) + loc_bytes + sensor_count + sensor_bytes
        return header + body

    def print(self, packet_type):
        packet_bytes = self.to_bytes()
        print("v" * 50)
        print(f"  Type: {packet_type}")
        print(f"  Transaction ID: {self.transaction_id}")
        print(f"  Location: {self.location_data.describe()}")
        try:
            sensor_str = self.sensor_data.describe()
        except Exception:
            sensor_str = str(self.sensor_data)
        print(f"  Sensors: {sensor_str}")
        print(f"  Packet: {packet_bytes.hex()}")
        print(f"  Packet size: {len(packet_bytes)} bytes")
        print("^" * 50)
