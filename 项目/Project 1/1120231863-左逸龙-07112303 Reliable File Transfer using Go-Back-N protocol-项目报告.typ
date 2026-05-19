#let course-code = "100071011"
#let course-name = "Computer Networks"
#let term = "2025-2026-2"
#let project-no = "Project-1"
#let project-title = "Reliable File Transfer using Go-Back-N protocol"
#let report-kind = "Project Report"

#let student-id = "1120231863"
#let student-name = "左逸龙"
#let class-no = "07112303"
#let instructor = "宿红毅"
#let report-date = datetime.today().display("[month repr:long] [day], [year]")

#set document(
  title: project-no + ": " + project-title,
  author: student-name,
)

#set page(
  paper: "a4",
  margin: (top: 2.2cm, bottom: 2cm, left: 2.45cm, right: 2.45cm),
)

#set text(
  font: ("Times New Roman", "Source Han Serif SC"),
  size: 11pt,
  lang: "en",
)

#set par(
  justify: true,
  first-line-indent: 2em,
  leading: 0.52em,
)

#show heading: it => {
  set par(first-line-indent: 0pt)
  block(above: 1.15em, below: 0.75em)[#it]
}

#let info-row(label, value) = (
  text(weight: "bold")[#label],
  if value == "" { [] } else { [#value] },
)

#let source-root = "1120231863-左逸龙-07112303 Reliable File Transfer using Go-Back-N protocol-源工程"

#align(center)[
  #v(3.3cm)

  #text(size: 15pt, weight: "bold")[
    #course-code #course-name #term \
    #project-no \
    #project-title \
    #report-kind
  ]

  #v(2.35cm)

  #table(
    columns: (6.2cm, 6.2cm),
    rows: 4 * (0.78cm,),
    align: (center + horizon, left + horizon),
    stroke: 0.75pt,
    inset: (x: 0.35em, y: 0.15em),
    ..info-row("学号 (Student ID)", student-id),
    ..info-row("姓名 (Name)", student-name),
    ..info-row("班号 (Class No.)", class-no),
    ..info-row("授课教师 (Instructor)", instructor),
  )

  #v(2.55cm)

  #text(size: 15pt, weight: "bold")[
    School of Computer \
    Beijing Institute of Technology \
    #report-date
  ]
]

#pagebreak()
#counter(page).update(1)

#set page(
  paper: "a4",
  margin: (top: 2.05cm, bottom: 1.75cm, left: 2.45cm, right: 2.45cm),
  header: context [
    #set text(size: 7.5pt)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [#course-code #course-name #term],
      [#project-no: #project-title],
    )
    #line(length: 100%, stroke: 0.65pt)
  ],
  footer: context [
    #set text(size: 8.5pt)
    #align(center)[#counter(page).display("1") / #numbering("1", ..counter(page).final())]
  ],
)

#set heading(numbering: "1.")
#set par(
  justify: true,
  first-line-indent: 2em,
  leading: 0.52em,
)

= Requirement Analysis

The goal of this project is to implement reliable file transfer on top of UDP. UDP only provides datagram delivery and does not guarantee reliable delivery, ordering, duplicate suppression, or error recovery. Therefore, the reliability mechanism must be implemented in the application layer.

In this project, each UDP datagram carries one self-defined PDU. The sender divides a file into data blocks, attaches protocol fields and a CRC checksum, and sends the PDUs through a UDP socket. The receiver checks the PDU, accepts only the expected sequence number, writes correct data into the output file, and sends cumulative acknowledgements. When the sender does not receive the expected acknowledgement before timeout, it retransmits the unacknowledged PDUs according to the Go-Back-N protocol.

#align(center)[
  #table(
    columns: (2.8cm, 6.5cm, 4.5cm),
    align: (left + horizon, left + horizon, left + horizon),
    table.header([*Requirement*], [*Implementation*], [*Evidence*]),
    [Custom PDU], [A fixed header and variable data field are defined.], [`gbn/pdu.py`],
    [CRC checksum], [CRC-CCITT-FALSE is used to detect corrupted PDUs.], [`crc_ccitt_false()`],
    [UDP socket], [One UDP datagram contains one encoded PDU.], [`socket.SOCK_DGRAM`],
    [Go-Back-N], [The sender maintains a sliding window and retransmits outstanding PDUs after timeout.], [`gbn/host.py`],
    [Full duplex], [Each host has sender and receiver threads.], [`run_demo.py`],
    [Loss and error simulation], [The channel randomly drops or corrupts DATA/FIN PDUs.], [`gbn/channel.py`],
    [Configuration], [Protocol and host parameters are read from JSON files.], [`configs/*.json`],
    [Logging and analysis], [CSV logs are analyzed into summary tables and SVG charts.], [`gbn/analyzer.py`],
  )
]

The expected output is a received file that is byte-by-byte identical to the original file. In the tests, this was verified by SHA-256 hash comparison.

= Design

== System Model

The system contains multiple hosts. Each host can send files to its configured peers and receive files from other peers at the same time. A sender thread reads the file, builds DATA and FIN PDUs, and sends them through an unreliable channel wrapper before the UDP socket. A receiver thread continuously receives UDP datagrams, decodes PDUs, checks CRC, updates the receive state, and sends ACK or FIN_ACK PDUs.

#figure(
  image("attachments/p1-system-architecture.svg", width: 90%),
  caption: [System architecture of the reliable file transfer system.]
)

== PDU Format

The PDU header is encoded with network byte order. Its fixed header size is 16 bytes. The data field is variable-length, but the implementation rejects data blocks larger than 4096 bytes.

#align(center)[
  #table(
    columns: (3cm, 2.1cm, 7.2cm),
    align: (left + horizon, center + horizon, left + horizon),
    table.header([*Field*], [*Size*], [*Meaning*]),
    [Magic], [2 bytes], [Protocol identifier, value `0x4742`.],
    [Version], [1 byte], [Protocol version, currently `1`.],
    [Type], [1 byte], [`DATA`, `ACK`, `FIN`, or `FIN_ACK`.],
    [Session ID], [4 bytes], [Identifier of one file transfer session.],
    [Seq], [2 bytes], [PDU sequence number in the configured sequence space.],
    [Ack], [2 bytes], [Cumulative acknowledgement number.],
    [Length], [2 bytes], [Length of the data field.],
    [Checksum], [2 bytes], [CRC-CCITT-FALSE checksum.],
    [Data], [0-4096 bytes], [File payload for DATA PDUs.],
  )
]

When encoding a PDU, the checksum field is first set to zero. Then CRC-CCITT-FALSE is calculated over the header and data. When decoding a PDU, the receiver recalculates the checksum with the checksum field zeroed. If the recalculated value is different from the received checksum, the PDU is treated as corrupted.

== Go-Back-N Protocol

The sender stores all sent but unacknowledged PDUs in the current sending window. The variable `base` records the first unacknowledged absolute frame number, and `next_abs` records the next frame to send. ACKs are cumulative. When an ACK matches a sequence number in the current outstanding window, `base` moves forward.

The receiver window size is 1. The receiver only accepts the PDU whose sequence number equals the current expected sequence number. Out-of-order DATA PDUs are discarded and not buffered. The receiver acknowledges the last correctly received in-order PDU.

#figure(
  image("attachments/p1-gbn-sequence.svg", width: 90%),
  caption: [Go-Back-N retransmission after a lost or corrupted DATA PDU.]
)

#figure(
  image("attachments/p1-receiver-flow.svg", width: 82%),
  caption: [Receiver behavior with receive window size 1.]
)

The sequence number in the PDU is a modular value. The implementation uses absolute frame numbers internally and writes `absolute_number mod 2^seq_bits` into the PDU. The sending window size must satisfy `sw_size <= 2^seq_bits - 1`. This check avoids ambiguity between old and new sequence numbers after wrap-around.

== Configuration and Error Simulation

The main communication parameters are configured in JSON files. The default local ports are based on the last four digits of the student ID.

#align(center)[
  #table(
    columns: (3.2cm, 3.1cm, 6.3cm),
    align: (left + horizon, center + horizon, left + horizon),
    table.header([*Parameter*], [*Default value*], [*Meaning*]),
    [`data_size`], [`1024`], [Bytes of file data in one DATA PDU.],
    [`seq_bits`], [`8`], [Sequence number space is `2^8`.],
    [`sw_size`], [`8`], [Maximum number of outstanding PDUs.],
    [`init_seq_no`], [`1`], [Initial sequence number used by both sides.],
    [`timeout_ms`], [`300`], [Timeout value of the sender base timer.],
    [`lost_rate`], [`0`], [Random DATA/FIN loss percentage.],
    [`error_rate`], [`0`], [Random DATA/FIN corruption percentage.],
    [`local_port`], [`41863`/`41864`], [UDP ports used by Host1 and Host2.],
  )
]

ACK and FIN_ACK PDUs are not randomly dropped or corrupted by default. This is a design choice used to focus the error simulation on data transfer. The report and tests therefore mainly analyze DATA/FIN loss and corruption. Another design note is that `InitSeqNo` is not negotiated by a handshake, so the sender and receiver configurations must use the same initial sequence number.

= Development and Implementation

The project was implemented in Python using only the standard library. No database or third-party network library is required at runtime. The tested Python version was Python 3.13.5, while Python 3.10 or later is sufficient.

#align(center)[
  #table(
    columns: (5cm, 8cm),
    align: (left + horizon, left + horizon),
    table.header([*Path*], [*Responsibility*]),
    [`gbn/pdu.py`], [PDU encoding, decoding, CRC, and sequence number utilities.],
    [`gbn/host.py`], [Host configuration, sender logic, receiver logic, ACK handling, and file hashing.],
    [`gbn/channel.py`], [Random packet loss and corruption simulation.],
    [`gbn/logging_utils.py`], [CSV logging of send and receive events.],
    [`gbn/analyzer.py`], [Log statistics, Markdown summary, and SVG charts.],
    [`run_demo.py`], [Starts Host1 and Host2 in one process for local full-duplex testing.],
    [`run_host.py`], [Starts one host from a JSON configuration file.],
    [`tests/test_pdu.py`], [Unit tests for CRC, PDU round trip, checksum failure, and sequence wrap-around.],
  )
]

The PDU implementation uses `struct.Struct("!HBBIHHHH")`. This format matches the header fields described in the design section. A corrupted PDU raises `PDUError` during decoding.

```python
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
```

The sender uses one base timer. If the timer expires, it logs a timeout event and retransmits all PDUs from `base` to `next_abs - 1`, which is the outstanding window.

```python
if timer_started is not None and time.monotonic() - timer_started >= self.timeout:
    log.log(direction="send", event="timeout", status="TO", base=base, next_seq=next_abs)
    for abs_no in range(base, next_abs):
        self._send_pdu(frames[abs_no], address, log, "TO", base, next_abs)
    timer_started = time.monotonic()
```

The CSV log contains enough information to reconstruct the transfer process.

#align(center)[
  #table(
    columns: (3.1cm, 9.8cm),
    align: (left + horizon, left + horizon),
    table.header([*Log field*], [*Meaning*]),
    [`timestamp`], [Wall-clock timestamp of the event.],
    [`host_id`, `peer_id`], [Local host and peer host identifiers.],
    [`session_id`], [Transfer session identifier.],
    [`direction`, `event`], [Whether the row is send/receive and PDU/ACK/timeout.],
    [`pdu_type`], [`DATA`, `ACK`, `FIN`, or `FIN_ACK`.],
    [`seq`, `ack`], [PDU sequence number and acknowledgement number.],
    [`status`], [`New`, `TO`, `OK`, `NoErr`, or `DataErr`.],
    [`base`, `next_seq`, `expected_seq`], [Sender and receiver protocol states.],
    [`bytes`, `note`], [Payload length and channel note such as lost/error.],
  )
]

= System Deployment, Startup, and Use

The source project directory contains a virtual environment and all required scripts. The following commands are run in the source directory.

```bash
python3 -m venv .venv
./.venv/bin/python --version
./.venv/bin/python generate_test_file.py data/host1.bin
./.venv/bin/python generate_test_file.py data/host2.bin --seed 202
```

The local full-duplex demo starts Host1 and Host2 in one process. Host1 sends `data/host1.bin` to Host2, and Host2 sends `data/host2.bin` to Host1.

```bash
./.venv/bin/python run_demo.py --clean
./.venv/bin/python analyze_logs.py --log-dir logs --output-dir results
```

#figure(
  image("attachments/p1-run-demo-screenshot.svg", width: 90%),
  caption: [Terminal output of the local full-duplex demo.]
)

The hosts can also be started manually in two terminals.

```bash
./.venv/bin/python run_host.py configs/host1.json
./.venv/bin/python run_host.py configs/host2.json
```

#figure(
  image("attachments/p1-config-screenshot.svg", width: 82%),
  caption: [Key fields in the Host1 configuration file.]
)

After transfer, logs are written to `logs/`, received files are written to `received/`, and statistical outputs are written to `results/`.

= System Test

== Unit Tests

The unit tests check the CRC standard vector, PDU encoding and decoding, checksum failure detection, and sequence number wrap-around window logic.

```bash
PYTHONPATH=. ./.venv/bin/python -m unittest discover -s tests -p "test_*.py"
```

#figure(
  image("attachments/p1-unit-test-screenshot.svg", width: 90%),
  caption: [Unit test result for PDU, CRC, and sequence number utilities.]
)

== Integrated Transfer Test

The default demo transferred two files larger than 3 MB at the same time. The output files were verified by SHA-256.

#figure(
  image("attachments/p1-sha256-screenshot.svg", width: 96%),
  caption: [SHA-256 comparison between original and received files.]
)

#align(center)[
  #table(
    columns: (3cm, 3.9cm, 3.4cm, 2.3cm),
    align: (left + horizon, left + horizon, left + horizon, center + horizon),
    table.header([*Test case*], [*Configuration*], [*Actual result*], [*Status*]),
    [Unit tests], [Default test suite], [`Ran 3 tests`, `OK`], [Passed],
    [Full-duplex transfer], [Host1 `<->` Host2], [Both demo outputs were `OK`.], [Passed],
    [File integrity], [Two 3 MB+ files], [Both SHA-256 pairs matched.], [Passed],
    [Packet loss], [`lost_rate=5`, `error_rate=0`], [`retransmits=2463`, `timeouts=308`], [Passed],
    [Packet corruption], [`lost_rate=0`, `error_rate=5`], [`DataErr=430`], [Passed],
    [Loss and corruption], [`lost_rate=5`, `error_rate=5`], [`retransmits=5440`, `timeouts=680`, `DataErr=556`], [Passed],
    [Maximum data size], [`data_size=4096`], [Transfer passed.], [Passed],
    [Invalid data size], [`data_size=4097`], [`ValueError` was raised.], [Passed],
    [Sequence wrap-around], [`seq_bits=3`, `sw_size=7`], [Transfer passed with wrap-around.], [Passed],
    [Invalid window size], [`seq_bits=3`, `sw_size=8`], [Startup was rejected.], [Passed],
    [Multi-host transfer], [Host1 to Host2/3/4], [All received files matched Host1 source file.], [Passed],
  )
]

The following sender log excerpt shows the main Go-Back-N behavior. The sender first sends eight new DATA PDUs. After timeout, it retransmits the whole outstanding window.

#align(center)[
  #table(
    columns: (2.2cm, 1.8cm, 1.8cm, 1.8cm, 1.7cm, 1.8cm),
    align: center + horizon,
    table.header([*Event*], [*Type*], [*Seq*], [*Status*], [*Base*], [*Next*]),
    [`pdu`], [`DATA`], [`1`], [`New`], [`0`], [`1`],
    [`pdu`], [`DATA`], [`2`], [`New`], [`0`], [`2`],
    [`pdu`], [`DATA`], [`8`], [`New`], [`0`], [`8`],
    [`timeout`], [``], [``], [`TO`], [`0`], [`8`],
    [`pdu`], [`DATA`], [`1`], [`TO`], [`0`], [`8`],
    [`pdu`], [`DATA`], [`2`], [`TO`], [`0`], [`8`],
    [`pdu`], [`DATA`], [`3`], [`TO`], [`0`], [`8`],
  )
]

= Performance and Analysis

The default full-duplex demo generated four CSV log files: two sender logs and two receiver logs. Throughput is meaningful for receiver logs because successfully received bytes are counted on the receiving side. Sender logs have `bytes_ok=0` in the analyzer output, so they should not be interpreted as zero real transfer throughput.

#align(center)[
  #table(
    columns: (5.5cm, 2.3cm, 2.2cm, 2.4cm),
    align: (left + horizon, center + horizon, center + horizon, center + horizon),
    table.header([*Receiver log*], [*Duration*], [*Bytes OK*], [*Throughput*]),
    [`Host1_recv_Host2_ec50f047.csv`], [`17.046089 s`], [`3145851`], [`180.22 KiB/s`],
    [`Host2_recv_Host1_f4dd0758.csv`], [`16.816290 s`], [`3145851`], [`182.69 KiB/s`],
  )
]

#figure(
  image("attachments/p1-throughput-receiver.svg", width: 88%),
  caption: [Receiver-side throughput in the default full-duplex demo.]
)

#figure(
  image("attachments/p1-retransmit-default.svg", width: 88%),
  caption: [Retransmitted PDU count in the default full-duplex demo.]
)

The error injection tests show the expected behavior of Go-Back-N. Packet loss causes timeouts and retransmissions. Packet corruption is detected by CRC and recorded as `DataErr`. When both loss and corruption are enabled, the number of retransmissions increases because one lost or corrupted PDU can force retransmission of multiple outstanding PDUs.

#align(center)[
  #table(
    columns: (3.5cm, 1.8cm, 1.8cm, 2.2cm, 2cm, 1.8cm),
    align: center + horizon,
    table.header([*Scenario*], [*Loss*], [*Error*], [*Retransmits*], [*Timeouts*], [*DataErr*]),
    [Loss only], [`5%`], [`0%`], [`2463`], [`308`], [`0`],
    [Corruption only], [`0%`], [`5%`], [`-`], [`-`], [`430`],
    [Loss and corruption], [`5%`], [`5%`], [`5440`], [`680`], [`556`],
  )
]

These stress tests were executed on a copied project directory during code checking, so the submitted source directory was not polluted by temporary configurations. In all tested cases, the received files matched the original files.

= Summary or Conclusions

This project implemented reliable file transfer over UDP using the Go-Back-N protocol. The implementation includes a self-defined PDU format, CRC-CCITT-FALSE checksum, sliding-window sending, cumulative acknowledgements, timeout retransmission, receiver-side in-order delivery, full-duplex transfer, configurable packet loss and corruption, CSV logging, and log analysis.

The tests show that the implementation can transfer files larger than 3 MB correctly. SHA-256 comparison proved that the received files were identical to the original files. Additional tests with packet loss, packet corruption, boundary data sizes, sequence number wrap-around, invalid parameters, and multi-host transfer also passed.

The main limitation is that `InitSeqNo` must be configured consistently on both sides because there is no handshake to negotiate it. Also, ACK and FIN_ACK PDUs are not randomly lost or corrupted by default. These choices simplify the project and make the DATA transfer behavior easier to analyze.

= References

#set par(first-line-indent: 0pt)

1. Andrew S. Tanenbaum and David J. Wetherall, _Computer Networks_, 5th Edition, Prentice Hall, 2011.

2. Python Software Foundation, "socket -- Low-level networking interface", Python Documentation.

3. Python Software Foundation, "struct -- Interpret bytes as packed binary data", Python Documentation.

4. Python Software Foundation, "threading -- Thread-based parallelism", Python Documentation.

5. RevEng CRC Catalogue, "CRC-16/IBM-3740", a CRC-CCITT-FALSE compatible parameter set.

6. Typst Documentation, "Typst Reference".

#set par(first-line-indent: 2em)

= Comments

This project helped me understand why reliability cannot be assumed when UDP is used. Implementing Go-Back-N also made the relationship between sequence numbers, cumulative ACKs, timeout retransmission, and receiver-side ordering clearer. The logging and analysis part was useful because it showed the cost of reliability under packet loss and packet corruption.
