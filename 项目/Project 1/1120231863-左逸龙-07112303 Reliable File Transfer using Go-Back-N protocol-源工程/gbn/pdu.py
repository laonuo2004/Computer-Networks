from __future__ import annotations

from dataclasses import dataclass
import struct


MAGIC = 0x4742
VERSION = 1
MAX_DATA_SIZE = 4096

TYPE_DATA = 1
TYPE_ACK = 2
TYPE_FIN = 3
TYPE_FIN_ACK = 4

TYPE_NAMES = {
    TYPE_DATA: "DATA",
    TYPE_ACK: "ACK",
    TYPE_FIN: "FIN",
    TYPE_FIN_ACK: "FIN_ACK",
}

HEADER_STRUCT = struct.Struct("!HBBIHHHH")
HEADER_SIZE = HEADER_STRUCT.size


class PDUError(ValueError):
    pass


def crc_ccitt_false(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def seq_mod(abs_no: int, seq_bits: int) -> int:
    return abs_no % (1 << seq_bits)


def previous_seq(seq: int, seq_bits: int) -> int:
    return (seq - 1) % (1 << seq_bits)


def in_window(seq: int, start: int, size: int, seq_bits: int) -> bool:
    space = 1 << seq_bits
    distance = (seq - start) % space
    return distance < size


@dataclass(frozen=True)
class PDU:
    pdu_type: int
    session_id: int
    seq: int
    ack: int
    data: bytes = b""

    def encode(self) -> bytes:
        if len(self.data) > MAX_DATA_SIZE:
            raise PDUError(f"data length {len(self.data)} exceeds {MAX_DATA_SIZE}")
        header = HEADER_STRUCT.pack(
            MAGIC,
            VERSION,
            self.pdu_type,
            self.session_id & 0xFFFFFFFF,
            self.seq & 0xFFFF,
            self.ack & 0xFFFF,
            len(self.data),
            0,
        )
        checksum = crc_ccitt_false(header + self.data)
        header = HEADER_STRUCT.pack(
            MAGIC,
            VERSION,
            self.pdu_type,
            self.session_id & 0xFFFFFFFF,
            self.seq & 0xFFFF,
            self.ack & 0xFFFF,
            len(self.data),
            checksum,
        )
        return header + self.data

    @classmethod
    def decode(cls, packet: bytes, verify_checksum: bool = True) -> "PDU":
        fields = parse_header(packet)
        magic, version, pdu_type, session_id, seq, ack, length, checksum = fields
        if magic != MAGIC:
            raise PDUError("bad magic")
        if version != VERSION:
            raise PDUError("bad version")
        if pdu_type not in TYPE_NAMES:
            raise PDUError("bad pdu type")
        if len(packet) != HEADER_SIZE + length:
            raise PDUError("bad length")
        data = packet[HEADER_SIZE:]
        if verify_checksum:
            zeroed = HEADER_STRUCT.pack(magic, version, pdu_type, session_id, seq, ack, length, 0)
            actual = crc_ccitt_false(zeroed + data)
            if actual != checksum:
                raise PDUError("bad checksum")
        return cls(pdu_type=pdu_type, session_id=session_id, seq=seq, ack=ack, data=data)


def parse_header(packet: bytes) -> tuple[int, int, int, int, int, int, int, int]:
    if len(packet) < HEADER_SIZE:
        raise PDUError("packet shorter than header")
    return HEADER_STRUCT.unpack(packet[:HEADER_SIZE])

