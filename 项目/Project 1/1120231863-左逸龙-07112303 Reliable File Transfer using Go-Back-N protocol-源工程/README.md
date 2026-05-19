# Reliable File Transfer using Go-Back-N

This source project implements reliable file transfer over UDP with Go-Back-N, CRC-CCITT-FALSE, configurable packet loss/corruption, full-duplex transfer, CSV logging, and log analysis. Runtime code uses only the Python standard library.

## Environment

Create and use the virtual environment in this source directory:

```bash
python3 -m venv .venv
./.venv/bin/python --version
./.venv/bin/python generate_test_file.py data/host1.bin
./.venv/bin/python generate_test_file.py data/host2.bin --seed 202
```

Python 3.10+ is sufficient; it was verified with Python 3.13.5.

## Run a Local Full-Duplex Demo

```bash
./.venv/bin/python run_demo.py --clean
./.venv/bin/python analyze_logs.py --log-dir logs --output-dir results
```

The demo starts Host1 and Host2 in one process. Host1 sends `data/host1.bin` to Host2 while Host2 sends `data/host2.bin` to Host1. Received files are written to `received/`, and the demo prints SHA-256 equality results.

## Run Hosts Manually

Open two terminals in this directory:

```bash
./.venv/bin/python run_host.py configs/host1.json
./.venv/bin/python run_host.py configs/host2.json
```

The default ports are `41863` to `41866`, using the last four digits of the student ID. Edit `configs/*.json` to change `data_size`, `sw_size`, `timeout_ms`, `error_rate`, and `lost_rate`.

## Analyze Logs

```bash
./.venv/bin/python analyze_logs.py --log-dir logs --output-dir results
```

Outputs:

- `results/summary.csv`
- `results/summary.md`
- `results/throughput.svg`
- `results/retransmit.svg`

## Tests

```bash
PYTHONPATH=. ./.venv/bin/python -m unittest discover -s tests -p "test_*.py"
```

The included tests verify the CRC standard vector, PDU round-trip encoding/decoding, checksum failure detection, and sequence-number wrap-around window checks.

## Windows exe Packaging

PyInstaller cannot cross-compile a Windows exe from WSL/Linux. On Windows, run these commands in this source directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\pyinstaller.exe --onefile --name 1120231863ReliableFileTransfer run_host.py
```

The expected executable path is:

```text
dist\1120231863ReliableFileTransfer.exe
```

Do not treat a Linux binary as the required Windows exe.
