from __future__ import annotations

import csv
from pathlib import Path


def analyze_log(path: Path) -> dict[str, object]:
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    if not rows:
        return {"log": path.name}
    first_ts = float(rows[0]["timestamp"])
    last_ts = float(rows[-1]["timestamp"])
    send_rows = [r for r in rows if r["direction"] == "send" and r["event"] == "pdu"]
    recv_rows = [r for r in rows if r["direction"] == "recv" and r["event"] == "pdu"]
    data_bytes = sum(int(r["bytes"] or 0) for r in recv_rows if r["status"] == "OK")
    duration = max(last_ts - first_ts, 0.000001)
    return {
        "log": path.name,
        "host_id": rows[0].get("host_id", ""),
        "peer_id": rows[0].get("peer_id", ""),
        "session_id": rows[0].get("session_id", ""),
        "total_rows": len(rows),
        "send_count": len(send_rows),
        "new_send_count": sum(1 for r in send_rows if r["status"] == "New"),
        "retransmit_count": sum(1 for r in send_rows if r["status"] == "TO"),
        "timeout_count": sum(1 for r in rows if r["event"] == "timeout"),
        "recv_count": len(recv_rows),
        "ok_count": sum(1 for r in recv_rows if r["status"] == "OK"),
        "data_error_count": sum(1 for r in recv_rows if r["status"] == "DataErr"),
        "order_error_count": sum(1 for r in recv_rows if r["status"] == "NoErr"),
        "duration_s": f"{duration:.6f}",
        "bytes_ok": data_bytes,
        "throughput_kib_s": f"{data_bytes / 1024.0 / duration:.2f}",
        "retransmit_rate": f"{(sum(1 for r in send_rows if r['status'] == 'TO') / max(len(send_rows), 1)):.4f}",
    }


def analyze_dir(log_dir: Path, output_dir: Path) -> list[dict[str, object]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries = [analyze_log(path) for path in sorted(log_dir.glob("*.csv"))]
    if not summaries:
        return []
    fields = list(summaries[0].keys())
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summaries)
    write_markdown_table(summaries, output_dir / "summary.md")
    write_svg_bar(summaries, output_dir / "throughput.svg", "throughput_kib_s", "Throughput (KiB/s)")
    write_svg_bar(summaries, output_dir / "retransmit.svg", "retransmit_count", "Retransmitted PDU count")
    return summaries


def write_markdown_table(rows: list[dict[str, object]], path: Path) -> None:
    fields = ["log", "send_count", "retransmit_count", "timeout_count", "data_error_count", "order_error_count", "duration_s", "throughput_kib_s"]
    lines = ["|" + "|".join(fields) + "|", "|" + "|".join(["---"] * len(fields)) + "|"]
    for row in rows:
        lines.append("|" + "|".join(str(row.get(f, "")) for f in fields) + "|")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg_bar(rows: list[dict[str, object]], path: Path, field: str, title: str) -> None:
    width = 900
    left = 230
    right = 70
    top = 28
    row_gap = 46
    bar_h = 18
    height = max(120, top * 2 + row_gap * len(rows))
    values = [float(row.get(field, 0) or 0) for row in rows]
    max_value = max(values) if values else 1.0
    max_value = max(max_value, 1.0)
    plot_w = width - left - right
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>',
        '  text { font-family: Arial, sans-serif; fill: #111; }',
        '  .label { font-size: 13px; }',
        '  .value { font-size: 12px; fill: #333; }',
        '  .guide { stroke: #e6e9ef; stroke-width: 1; }',
        '  .bar { fill: #2f80ed; rx: 5; }',
        '</style>',
    ]
    for i, (row, value) in enumerate(zip(rows, values)):
        y = top + i * row_gap
        bar_w = int(plot_w * value / max_value)
        label = str(row.get("log", ""))[:36]
        parts.append(f'<text x="20" y="{y + 15}" class="label">{label}</text>')
        parts.append(f'<line x1="{left}" y1="{y + bar_h / 2:g}" x2="{left + plot_w}" y2="{y + bar_h / 2:g}" class="guide"/>')
        if bar_w > 0:
            parts.append(f'<rect x="{left}" y="{y}" width="{bar_w}" height="{bar_h}" class="bar"/>')
            value_x = min(left + bar_w + 10, width - 45)
        else:
            value_x = left + 8
        parts.append(f'<text x="{value_x}" y="{y + 14}" class="value">{value:g}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")
