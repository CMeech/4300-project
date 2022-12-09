import logging
import os
from pathlib import Path
from project_source.client_module.experiments.benchmark import Benchmark
from project_source.common.constants import (
    CLIENT_MODULE,
    CSV_HEADER,
    CSV_TEMPLATE,
    EXPERIMENT_DIR,
    PROJECT_SRC,
    RESULTS_DIR,
    WRITE_TEXT
)
from project_source.common.messages import (
    EXPERIMENT_ERROR,
    EXPERIMENT_SAVE_ERROR,
    EXPERIMENT_SAVED
)


class Experiment():
    def __init__(self, name: str):
        self.name: str = name
        self.entries = []
        self.error: Exception = None

        # open the file writer
        try:
            root_path = Path(os.getcwd()).resolve().parent
            file_path = os.path.join(
                root_path,
                PROJECT_SRC,
                CLIENT_MODULE,
                EXPERIMENT_DIR,
                RESULTS_DIR,
                CSV_TEMPLATE.format(self.name)
            )
            self.file_writer = open(file_path, WRITE_TEXT)
        except OSError as ose:
            print(EXPERIMENT_ERROR)
            logging.error(ose)
            self.error = ose
            self.file_writer = None
        except Exception as e:
            print(EXPERIMENT_ERROR)
            logging.error(e)
            self.error = e
            self.file_writer = None


    def add_entry(self, entry: Benchmark):
        self.entries.append(entry)


    def save_to_csv(self):
        if self.error == None:
            try:
                self.file_writer.write(CSV_HEADER)
                for entry in self.entries:
                    self.file_writer.write(entry.to_csv_entry())
                print(EXPERIMENT_SAVED)
            except Exception as e:
                print(EXPERIMENT_SAVE_ERROR)
                logging.error(e)
            finally:
                self.file_writer.close()
