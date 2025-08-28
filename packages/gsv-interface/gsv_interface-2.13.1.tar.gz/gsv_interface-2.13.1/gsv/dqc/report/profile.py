from dataclasses import dataclass


@dataclass
class Profile:
    name: str
    __split_key: str = None

    def __post_init__(self):
        self.summary_lines = []

    def add_summary_line(self, line):
        self.summary_lines.append(line)

    def order_summary_lines(self):
        self.summary_lines.sort(key=lambda x: x.process_id)

    def set_split_key(self, split_key):
        self.__split_key = split_key

    @property
    def failed_lines(self):
        return list(filter(lambda x: x.status=="ERROR", self.summary_lines))

    @property
    def split_key(self):
        return self.__split_key

    @property
    def status(self):
        if any([line.status == "ERROR" for line in self.summary_lines]):
            return "ERROR"
        elif any([line.status == "WARNING" for line in self.summary_lines]):
            return "WARNING"
        else:
            return "INFO"
    
    @property
    def used_cores(self):
        return max(self.summary_lines, key=lambda x: x.process_id).process_id