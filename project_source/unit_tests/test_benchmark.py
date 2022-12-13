import unittest

from project_source.client_module.experiments.benchmark import Benchmark
from project_source.common.constants import LARGE_CHUNK

class TestBenchmark(unittest.TestCase):
    def test_error(self):
        bench = Benchmark(LARGE_CHUNK, 0, 0)
        self.assertFalse(bench.error_occurred)
        bench.error()
        self.assertTrue(bench.error_occurred)

    def test_to_csv(self):
        bench = Benchmark(LARGE_CHUNK, 123, 321)
        self.assertEqual(
            bench.to_csv_entry(),
            "\n2048,123,321"
        )

    def test_to_str(self):
        bench = Benchmark(LARGE_CHUNK, 123, 321)
        self.assertEqual(
            bench.__str__(),
            "Benchmark -> Chunk Size: 2048, Number of Chunks: 123, Time: 321."
        )