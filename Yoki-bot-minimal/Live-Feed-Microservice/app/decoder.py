# decoder.py
import struct
from typing import Dict, Any

def decode_ltp_packet(packet: bytes) -> Dict[str, Any]:
    """
    Decode Angel One SmartStream LTP binary packet.
    Returns a dict with keys: mode, exchange_type, token, sequence_no, timestamp, ltp
    """
    try:
        if not packet or len(packet) < 47:
            return {"error": "packet_too_small", "length": len(packet) if packet else 0}

        # 1 byte mode, 1 byte exchange type
        mode = packet[0]
        exchange_type = packet[1]

        # 25 bytes token (null-terminated)
        token_raw = packet[2:27]
        token = token_raw.split(b'\x00')[0].decode("utf-8", errors="ignore")

        # seq_no (8 bytes, little-endian)
        seq_no = struct.unpack_from("<Q", packet, 27)[0]

        # exchange timestamp (8 bytes, little-endian, ms)
        timestamp = struct.unpack_from("<Q", packet, 35)[0]

        # ltp int32 (4 bytes, little-endian) at offset 43 - value in paise
        ltp_int = struct.unpack_from("<i", packet, 43)[0]
        ltp = ltp_int / 100.0

        return {
            "mode": int(mode),
            "exchange_type": int(exchange_type),
            "token": token,
            "sequence_no": int(seq_no),
            "timestamp": int(timestamp),
            "ltp": float(ltp)
        }
    except Exception as e:
        return {"error": f"decode_error: {e}"}
