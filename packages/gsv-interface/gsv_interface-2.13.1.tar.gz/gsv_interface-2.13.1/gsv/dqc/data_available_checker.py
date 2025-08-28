from gsv import GSVRetriever
from gsv.exceptions import MissingGSVMessageError


class DataAvailableChecker:

    def __init__(self, request, logging_level):
        self.status = 0
        self.request = request
        self.logging_level = logging_level
        self.err_msg = None

    def run(self):
        gsv = GSVRetriever(logging_level=self.logging_level)
        try:
            gsv.check_messages_in_fdb(self.request, process_request=True)
        except MissingGSVMessageError as e:
            self.status = 1
            self.err_msg = str(e)
