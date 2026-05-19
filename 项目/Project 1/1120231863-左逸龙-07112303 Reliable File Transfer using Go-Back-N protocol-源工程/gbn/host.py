from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import queue
import socket
import threading
import time
import zlib

from .channel import UnreliableChannel
from .logging_utils import CsvLogger
from .pdu import (
    PDU,
    PDUError,
    TYPE_ACK,
    TYPE_DATA,
    TYPE_FIN,
    TYPE_FIN_ACK,
    TYPE_NAMES,
    in_window,
    parse_header,
    previous_seq,
    seq_mod,
)


@dataclass
class PeerConfig:
    peer_id: str
    peer_ip: str
    peer_port: int
    send_file: str | None = None
    receive_file: str | None = None


class Host:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self.root = self.config_path.parent.parent
        cfg = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.host_id = cfg["host_id"]
        self.local_ip = cfg.get("local_ip", "127.0.0.1")
        self.local_port = int(cfg["local_port"])
        self.data_size = int(cfg.get("data_size", 1024))
        self.seq_bits = int(cfg.get("seq_bits", 8))
        self.seq_space = 1 << self.seq_bits
        self.sw_size = int(cfg.get("sw_size", 8))
        self.init_seq_no = int(cfg.get("init_seq_no", 0)) % self.seq_space
        self.timeout = int(cfg.get("timeout_ms", 500)) / 1000.0
        self.log_dir = self._resolve(cfg.get("log_dir", "logs"))
        self.receive_dir = self._resolve(cfg.get("receive_dir", "received"))
        self.channel = UnreliableChannel(
            cfg.get("lost_rate", 0),
            cfg.get("error_rate", 0),
            cfg.get("random_seed"),
        )
        self.peers = [PeerConfig(**peer) for peer in cfg.get("peers", [])]
        self.peer_by_addr = {(p.peer_ip, int(p.peer_port)): p for p in self.peers}
        self.peer_by_id = {p.peer_id: p for p in self.peers}
        if self.data_size > 4096:
            raise ValueError("data_size must not exceed 4096")
        if self.sw_size > self.seq_space - 1:
            raise ValueError("sw_size must be <= 2^seq_bits - 1")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.2)
        self.stop_event = threading.Event()
        self.ack_queues: dict[int, queue.Queue[PDU]] = {}
        self.recv_sessions: dict[tuple[int, str], dict[str, object]] = {}
        self.recv_lock = threading.Lock()
        self.sender_threads: list[threading.Thread] = []
        self.receiver_thread: threading.Thread | None = None

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        return p if p.is_absolute() else self.root / p

    def start(self, wait: bool = True, linger: float = 1.0) -> None:
        self.sock.bind((self.local_ip, self.local_port))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.receive_dir.mkdir(parents=True, exist_ok=True)
        rx = threading.Thread(target=self._receive_loop, name=f"{self.host_id}-rx", daemon=True)
        rx.start()
        self.receiver_thread = rx
        senders = []
        for peer in self.peers:
            if peer.send_file:
                t = threading.Thread(target=self._send_file, args=(peer,), name=f"{self.host_id}-send-{peer.peer_id}")
                t.start()
                senders.append(t)
        self.sender_threads = senders
        if wait:
            for t in senders:
                t.join()
            time.sleep(linger)
            self.stop()
            rx.join(timeout=1.0)

    def stop(self) -> None:
        self.stop_event.set()
        self.sock.close()

    def senders_done(self) -> bool:
        return all(not t.is_alive() for t in self.sender_threads)

    def session_id_for(self, peer: PeerConfig) -> int:
        raw = f"{self.host_id}->{peer.peer_id}:{peer.send_file or ''}".encode("utf-8")
        return zlib.crc32(raw) & 0xFFFFFFFF

    def _read_frames(self, path: Path, session_id: int) -> list[PDU]:
        frames = []
        abs_no = 0
        with path.open("rb") as f:
            while True:
                chunk = f.read(self.data_size)
                if not chunk:
                    break
                frames.append(PDU(TYPE_DATA, session_id, seq_mod(self.init_seq_no + abs_no, self.seq_bits), 0, chunk))
                abs_no += 1
        frames.append(PDU(TYPE_FIN, session_id, seq_mod(self.init_seq_no + abs_no, self.seq_bits), 0, b""))
        return frames

    def _send_file(self, peer: PeerConfig) -> None:
        session_id = self.session_id_for(peer)
        ack_queue: queue.Queue[PDU] = queue.Queue()
        self.ack_queues[session_id] = ack_queue
        path = self._resolve(peer.send_file or "")
        frames = self._read_frames(path, session_id)
        log = CsvLogger(self.log_dir / f"{self.host_id}_to_{peer.peer_id}_{session_id:08x}.csv", self.host_id, peer.peer_id, session_id)
        base = 0
        next_abs = 0
        timer_started: float | None = None
        address = (peer.peer_ip, peer.peer_port)
        try:
            while base < len(frames):
                while next_abs < len(frames) and next_abs < base + self.sw_size:
                    self._send_pdu(frames[next_abs], address, log, "New", base, next_abs + 1)
                    if base == next_abs:
                        timer_started = time.monotonic()
                    next_abs += 1
                try:
                    ack = ack_queue.get(timeout=0.02)
                    for abs_no in range(base, next_abs):
                        if frames[abs_no].seq == ack.ack:
                            base = abs_no + 1
                            timer_started = time.monotonic() if base < next_abs else None
                            break
                    log.log(direction="recv", event="ack", pdu_type=TYPE_NAMES.get(ack.pdu_type), seq=ack.seq, ack=ack.ack, status="ACK", base=base, next_seq=next_abs)
                except queue.Empty:
                    pass
                if timer_started is not None and time.monotonic() - timer_started >= self.timeout:
                    log.log(direction="send", event="timeout", status="TO", base=base, next_seq=next_abs)
                    for abs_no in range(base, next_abs):
                        self._send_pdu(frames[abs_no], address, log, "TO", base, next_abs)
                    timer_started = time.monotonic()
        finally:
            log.close()
            self.ack_queues.pop(session_id, None)

    def _send_pdu(self, pdu: PDU, address: tuple[str, int], log: CsvLogger | None, status: str, base: int = 0, next_seq: int = 0) -> None:
        encoded = pdu.encode()
        packet, channel_status = self.channel.transmit(encoded, pdu)
        if packet is not None:
            self.sock.sendto(packet, address)
        if log:
            note = channel_status if channel_status != "sent" else ""
            log.log(direction="send", event="pdu", pdu_type=TYPE_NAMES[pdu.pdu_type], seq=pdu.seq, ack=pdu.ack, status=status, base=base, next_seq=next_seq, bytes=len(pdu.data), note=note)

    def _receive_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                packet, addr = self.sock.recvfrom(65535)
            except (socket.timeout, OSError):
                continue
            peer = self.peer_by_addr.get(addr)
            peer_id = peer.peer_id if peer else f"{addr[0]}:{addr[1]}"
            try:
                pdu = PDU.decode(packet)
            except PDUError:
                self._handle_bad_packet(packet, addr, peer, peer_id)
                continue
            if pdu.pdu_type in (TYPE_ACK, TYPE_FIN_ACK):
                q = self.ack_queues.get(pdu.session_id)
                if q:
                    q.put(pdu)
            elif pdu.pdu_type in (TYPE_DATA, TYPE_FIN):
                self._handle_data(pdu, addr, peer, peer_id)

    def _session_state(self, pdu: PDU, peer: PeerConfig | None, peer_id: str) -> dict[str, object]:
        key = (pdu.session_id, peer_id)
        with self.recv_lock:
            state = self.recv_sessions.get(key)
            if state is None:
                receive_file = peer.receive_file if peer and peer.receive_file else f"{peer_id}_{pdu.session_id:08x}.bin"
                out_path = self._resolve(receive_file)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                log = CsvLogger(self.log_dir / f"{self.host_id}_recv_{peer_id}_{pdu.session_id:08x}.csv", self.host_id, peer_id, pdu.session_id)
                state = {
                    "expected": self.init_seq_no,
                    "file": out_path.open("wb"),
                    "log": log,
                    "done": False,
                }
                self.recv_sessions[key] = state
            return state

    def _handle_data(self, pdu: PDU, addr: tuple[str, int], peer: PeerConfig | None, peer_id: str) -> None:
        state = self._session_state(pdu, peer, peer_id)
        expected = int(state["expected"])
        log: CsvLogger = state["log"]  # type: ignore[assignment]
        if pdu.seq == expected and not state["done"]:
            status = "OK"
            if pdu.pdu_type == TYPE_DATA:
                f = state["file"]
                f.write(pdu.data)  # type: ignore[attr-defined]
            else:
                state["done"] = True
                state["file"].close()  # type: ignore[attr-defined]
            ack_no = expected
            state["expected"] = (expected + 1) % self.seq_space
        else:
            status = "NoErr"
            ack_no = previous_seq(expected, self.seq_bits)
        ack_type = TYPE_FIN_ACK if pdu.pdu_type == TYPE_FIN and status == "OK" else TYPE_ACK
        ack = PDU(ack_type, pdu.session_id, 0, ack_no, b"")
        self.sock.sendto(ack.encode(), addr)
        log.log(direction="recv", event="pdu", pdu_type=TYPE_NAMES[pdu.pdu_type], seq=pdu.seq, ack=ack_no, status=status, expected_seq=expected, bytes=len(pdu.data))

    def _handle_bad_packet(self, packet: bytes, addr: tuple[str, int], peer: PeerConfig | None, peer_id: str) -> None:
        try:
            _, _, pdu_type, session_id, seq, _, _, _ = parse_header(packet)
        except PDUError:
            return
        state = self.recv_sessions.get((session_id, peer_id))
        if state is None:
            return
        expected = int(state["expected"])
        ack_no = previous_seq(expected, self.seq_bits)
        self.sock.sendto(PDU(TYPE_ACK, session_id, 0, ack_no, b"").encode(), addr)
        log: CsvLogger = state["log"]  # type: ignore[assignment]
        log.log(direction="recv", event="pdu", pdu_type=TYPE_NAMES.get(pdu_type, "BAD"), seq=seq, ack=ack_no, status="DataErr", expected_seq=expected, note="checksum/header error")


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
