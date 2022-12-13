import os
from pathlib import Path
import unittest
from project_source.client_module.experiments.benchmark import Benchmark

from project_source.client_module.experiments.experiment import Experiment
from project_source.common.constants import CLIENT_MODULE, CSV_TEMPLATE, EXPERIMENT_DIR, LARGE_CHUNK, PROJECT_SRC, READ_BYTES, RESULTS_DIR

class TestExperiment(unittest.TestCase):
    def test_create_experiment(self):
        experiment = Experiment("EXPERIMENT_TEST")
        bench = Benchmark(LARGE_CHUNK, 100, 100)
        experiment.add_entry(bench)
        self.assertEqual(len(experiment.entries), 1)
        experiment.save_to_csv()

        try:
            found = False
            root_path = Path(os.getcwd()).resolve().parent
            file_path = os.path.join(
                root_path,
                PROJECT_SRC,
                CLIENT_MODULE,
                EXPERIMENT_DIR,
                RESULTS_DIR,
                CSV_TEMPLATE.format("EXPERIMENT_TEST")
            )
            with open(file_path, "r") as f:
                for num, line in enumerate(f, 1):
                    if "2048,100,100" in line:
                        found = True
        
            self.assertTrue(found)

        except OSError:
            self.fail()

    def test_bad_filename(self):
        # an error will appear in the console
        experiment = Experiment("///BAD")
        self.assertIsNotNone(experiment.error)