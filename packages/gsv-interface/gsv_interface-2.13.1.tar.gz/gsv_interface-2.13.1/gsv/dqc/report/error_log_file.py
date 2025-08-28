from pathlib import Path
import re
import subprocess
import tempfile


class ErrorLogFile:

    SUMMARY_NAME = "dqc.sum"
    ERRORS_NAME = "dqc.err"
    temp_dir = tempfile.TemporaryDirectory()
    dqc_utils = Path(__file__).parent / "dqcutils.sh"

    def __init__(self, log_file):
        self.log_file = log_file
        self._summary = ""
        self._errors = ""
        self._error_lines = []
        self.generate_summary_tempfile(f"{self.temp_dir.name}/{self.SUMMARY_NAME}")
        self.generate_errors_tempfile(f"{self.temp_dir.name}/{self.ERRORS_NAME}")
        self.read_summary()
        self.read_errors()
        self.read_error_lines()

        # Capture fail due to time limit


    @property
    def content(self):
        with open(self.log_file, 'r') as f:
            return f.read() 

    def read_summary(self):
        with open(f"{self.temp_dir.name}/{self.SUMMARY_NAME}", 'r') as f:
            self._summary = f.read()
    
    def read_errors(self):
        with open(f"{self.temp_dir.name}/{self.ERRORS_NAME}", 'r') as f:
            self._errors = f.read()

    def read_error_lines(self):
        with open(f"{self.temp_dir.name}/{self.ERRORS_NAME}", 'r') as f:
            self._error_lines = list(f.readlines())

    @property
    def is_fail_due_to_wallclock(self):
        with open(self.log_file, 'r') as f:
            last_line = f.readlines()[-1]

        if re.search(r"DUE TO TIME LIMIT", last_line):
            return True
        else:
            return False

    @property
    def summary(self):
        return self._summary

    @property
    def errors(self):
        return self._errors
    
    @property
    def error_lines(self):
        return self._error_lines

    def generate_summary_tempfile(self, tempfile):
        with open(tempfile, 'w') as f:
            p = subprocess.Popen(["bash", "-c", f". {self.dqc_utils}; dqc-summary {self.log_file}"], stdout=f)
            p.wait()  # Otherwise file is read before anything is written to it

    def generate_errors_tempfile(self, tempfile):
        with open(tempfile, 'w') as f:
            p = subprocess.Popen(["bash", "-c", f". {self.dqc_utils}; dqc-errors {self.log_file}"], stdout=f)
            p.wait()  # Otherwise file is read before anything is written to it
