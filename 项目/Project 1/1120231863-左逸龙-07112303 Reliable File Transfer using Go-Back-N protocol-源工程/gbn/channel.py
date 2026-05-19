from __future__ import annotations

import random

from .pdu import PDU, TYPE_ACK, TYPE_FIN_ACK


class UnreliableChannel:
    def __init__(self, lost_rate: float = 0.0, error_rate: float = 0.0, seed: int | None = None):
        self.lost_rate = max(0.0, float(lost_rate))
        self.error_rate = max(0.0, float(error_rate))
        self.random = random.Random(seed)

    def transmit(self, encoded: bytes, pdu: PDU) -> tuple[bytes | None, str]:
        if pdu.pdu_type in (TYPE_ACK, TYPE_FIN_ACK):
            return encoded, "sent"
        if self.lost_rate and self.random.random() < self.lost_rate / 100.0:
            return None, "lost"
        if self.error_rate and self.random.random() < self.error_rate / 100.0:
            damaged = bytearray(encoded)
            if damaged:
                index = self.random.randrange(len(damaged))
                damaged[index] ^= 0x01
            return bytes(damaged), "error"
        return encoded, "sent"

