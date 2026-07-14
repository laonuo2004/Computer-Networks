from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools import performance_suite


class PerformanceStatisticsTests(unittest.TestCase):
    def test_percentile_interpolates_sorted_values(self) -> None:
        percentile = getattr(performance_suite, "percentile", None)
        self.assertIsNotNone(percentile)
        self.assertAlmostEqual(3.0, percentile([1.0, 2.0, 3.0, 4.0, 5.0], 50))
        self.assertAlmostEqual(4.8, percentile([1.0, 2.0, 3.0, 4.0, 5.0], 95))

    def test_summary_uses_median_across_repetitions(self) -> None:
        result_type = getattr(performance_suite, "RunResult", None)
        summarize = getattr(performance_suite, "summarize", None)
        self.assertIsNotNone(result_type)
        self.assertIsNotNone(summarize)
        rows = [
            result_type(4, repetition, 500, 40, 1.0, throughput, 10.0, 9.0, 15.0, 500, 0)
            for repetition, throughput in enumerate((100.0, 300.0, 200.0), 1)
        ]
        summary = summarize(rows)
        self.assertEqual(1, len(summary))
        self.assertEqual(4, summary[0].workers)
        self.assertEqual(200.0, summary[0].throughput)
        self.assertEqual(0, summary[0].errors)

    def test_svg_writer_creates_valid_svg(self) -> None:
        summary_type = getattr(performance_suite, "SummaryResult", None)
        writer = getattr(performance_suite, "write_svg", None)
        self.assertIsNotNone(summary_type)
        self.assertIsNotNone(writer)
        rows = [
            summary_type(1, 100.0, 10.0, 9.0, 15.0, 0),
            summary_type(4, 240.0, 5.0, 4.0, 8.0, 0),
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "chart.svg"
            writer(path, rows, metric="throughput", title="Throughput", y_label="requests/s")
            content = path.read_text(encoding="utf-8")
        self.assertIn("<svg", content)
        self.assertIn("Throughput", content)
        self.assertIn(">1<", content)
        self.assertIn(">4<", content)


if __name__ == "__main__":
    unittest.main()
