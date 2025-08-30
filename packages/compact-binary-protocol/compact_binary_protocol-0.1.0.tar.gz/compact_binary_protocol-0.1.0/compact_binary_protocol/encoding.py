import struct

def encode_var_string(input_str: str) -> bytes:
    """
    Encode a variable length ASCII string with a 1-byte big-endian length prefix.
    Length is truncated to 255 bytes if the input is longer.
    """
    bytes_data = input_str.encode('ascii')
    if len(bytes_data) > 255:
        bytes_data = bytes_data[:255]
    return struct.pack('>B', len(bytes_data)) + bytes_data
