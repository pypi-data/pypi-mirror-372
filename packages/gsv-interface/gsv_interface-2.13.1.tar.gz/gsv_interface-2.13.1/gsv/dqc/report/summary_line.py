from dataclasses import dataclass
import json
import re


@dataclass
class SummaryLine:
    msg: str

    def __post_init__(self):
        self.err_messages = []
        self.failed_checker = []

    @property
    def profile(self):
        search = re.search(r'\/([\w-]+.yaml)', self.msg)
        return search.group(1) if search else None

    @property
    def split_key(self):
        search = re.search(r'split key:\s(\w+)\)', self.msg)
        return search.group(1) if search else None

    @property
    def request(self):
        search = re.search(r'Request: (\{.+\})', self.msg)
        return search.group(1) if search else None

    @property
    def main_key_values(self):
        if self.request is None:
            return None
        json_str = self.request.replace("'", '"')
        request = json.loads(json_str)
        return str(request[self.split_key])
        search = re.search(rf"'{self.split_key}':\s(.+)[,\}}]", self.request)
        return search.group(1).split(',')[0] if search else None

    @property
    def fstatus(self):
        return self.msg.split(':')[0]

    @property
    def status(self):
        search = re.search(r'(INFO|WARNING|ERROR)', self.fstatus)
        return search.group(1) if search else None

    @property
    def process_id(self):
        return int(self.msg.split('/')[0].split('-')[-1])

    @property
    def max_cores(self):
        return int(self.msg.split('/')[1].split(':')[0])