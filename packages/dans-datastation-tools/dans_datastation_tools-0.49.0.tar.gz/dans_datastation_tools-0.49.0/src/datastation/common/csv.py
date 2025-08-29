import csv
import logging
import sys


class CsvReport:
    """A simple, self-closing wrapper around csv.DictWriter to make it easier to use."""

    def __init__(self, filename, headers):
        self.filename = filename
        self.headers = headers
        self.csv_file = sys.stdout if filename == '-' else open(filename, 'w')
        self.csv_writer = csv.DictWriter(self.csv_file, headers, lineterminator='\n')
        self.csv_writer.writeheader()

    def write(self, row):
        logging.debug(f"Writing row: {row}")
        self.csv_writer.writerow(row)

    def close(self):
        if self.filename != '-':
            self.csv_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class CsvInput:
    """A simple, self-closing wrapper around csv.DictReader to make it easier to use."""

    def __init__(self, filename, delimiter=','):
        self.filename = filename
        self.csv_file = sys.stdin if filename == '-' else open(filename, 'r')
        self.csv_reader = csv.DictReader(self.csv_file, delimiter=delimiter)

    def __iter__(self):
        return self.csv_reader.__iter__()

    def close(self):
        if self.filename != '-':
            self.csv_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
