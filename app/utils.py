import struct
import re

def receive(conn):
    try:
        header = conn.recv(4)
        if not header:
            return None
        msg_length = struct.unpack('!I', header)[0]
        data = b""
        while len(data) < msg_length:
            packet = conn.recv(min(1024, msg_length - len(data)))
            if not packet:
                return None
            data += packet
        return data.decode('utf-8')
    except Exception as e:
        print(f"Error receiving data: {e}")


def send(conn, data):
    try:
        if not isinstance(data, bytes):
            encoded_data = str(data).encode('utf-8')
        else:
            encoded_data = data
        conn.send(struct.pack('!I', len(encoded_data)))
        conn.send(encoded_data)
    except Exception as e:
        print(f"Error sending data: {e}")


def is_valid_port(port):
    # works for port numbers (0-65535)
    port_pattern = r'^([1-9]\d{0,4}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$'

    return re.match(port_pattern, port) is not None


def is_valid_ip(ip):
    # matches IPv4 addresses
    ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

    return re.match(ipv4_pattern, ip) is not None
