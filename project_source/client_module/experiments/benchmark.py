from project_source.common.messages import BENCHMARK


class Benchmark():
    def __init__(self, chunk_size, num_chunks, measured_time):
        self.chunk_size = chunk_size
        self.num_chunks = num_chunks
        # in seconds
        self.measured_time = measured_time
        self.error = False

    def error(self):
        self.error = True

    def to_csv_entry(self):
        return f"\n{self.chunk_size},{self.num_chunks},{self.measured_time}"

    def __str__(self):
        return BENCHMARK.format(self.chunk_size, self.num_chunks, self.measured_time)

    