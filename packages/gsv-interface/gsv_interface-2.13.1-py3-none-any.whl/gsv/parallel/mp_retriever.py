import concurrent.futures
from typing import Dict, Optional, Union

import xarray as xr

from gsv.logger import get_logger
from gsv.retriever import GSVRetriever
from gsv.requests.parser import parse_request
from gsv.requests.utils import count_combinations, subsample_request


def get_retriever(logging_level, engine, check_messages_in_fdb, definitions, report_valid_time, apply_fixer, use_stream_iterator, output_type, output_filename):
    global f

    if output_type.lower() != "xarray":
        raise NotImplementedError(
            f"Unsupported output type {output_type} for GSVMPRetriever. "
            f"Only 'xarray' type is supported."
        )

    def f(request):
        gsv = GSVRetriever(logging_level=logging_level, engine=engine)
        gsv.request_data(
            request=request,
            check_messages_in_fdb=check_messages_in_fdb,
            definitions=definitions,
            report_valid_time=report_valid_time,
            apply_fixer=apply_fixer,
            use_stream_iterator=use_stream_iterator,
            output_type="xarray",
            output_filename=None
        )
        return gsv.ds
    return f


class GSVMPRetriever:

    ALLOWED_PARALLEL_KEYS = {"param", "date", "time", "step", "levelist", "month", "year"}
    DEFAULT_CORES = 4

    def __init__(self, logging_level="INFO", engine="fdb", n_proc=None):
        """
        Constructor for GSVMPRetriever class.

        Arguments
        ---------
        logging_level : str
            Set level for log messages. Options are: DEBUG, INFO,
            WARNING, ERROR and CRITICAL. Default is INFO.
        engine: str
            Set engine for data retrieval. Supported options are
            'fdb' and 'polytope'. Default is 'fdb'.
        n_proc : int or None
            Number of processors requested by user. If not set, it will use
            the number defined at class variable DEFAULT_CORES.
        """
        self.logger = get_logger(
            logger_name=__name__, logging_level=logging_level
        )
        self.engine = GSVRetriever.get_engine(engine)
        self.request = None
        self.decoder = None
        self.datareader = None
        self.area = None
        self.ds = None
        self.n_proc = n_proc or self.DEFAULT_CORES

    @classmethod
    def get_parallel_key(cls, request):
        key_length = {k: count_combinations(request, [k]) for k in request if k in cls.ALLOWED_PARALLEL_KEYS}
        parallel_key = max(key_length, key=key_length.get)
        return parallel_key

    def get_partial_requests(self):
        requests = [subsample_request(self.request, self.parallel_key, self.n_proc, i) for i in range(self.n_proc)]
        # Filter requests with 0 expected data
        # TODO: use fancier filter syntax
        requests = [request for request in requests if count_combinations(request, GSVRetriever.MARS_KEYS) >= 1]  # Filter 
        return requests

    @staticmethod
    def merge_results(partial_results, parallel_key):
        # Filter only datasets with answer
        # filter
        if parallel_key in {'time', 'date', 'year', 'month', 'step'}:
            ds = xr.concat(partial_results, dim="time").sortby("time")
        elif parallel_key == "levelist":
            ds = xr.concat(partial_results, dim="level").sortby("level")
        elif parallel_key == "param":
            ds = xr.merge(partial_results)
        return ds

    def request_data(
        self,
        request: Union[Dict, str],
        check_messages_in_fdb=False,
        definitions=None,
        report_valid_time=False,
        apply_fixer=False,
        use_stream_iterator=False,
        output_type="xarray",
        output_filename="gsv_data.grb"
        ) -> Optional[xr.Dataset]:
        # Get retrieving function
        retrieving_fn = get_retriever(
            logging_level="DEBUG",
            engine=self.engine.NAME,
            check_messages_in_fdb=check_messages_in_fdb,
            definitions=definitions,
            report_valid_time=report_valid_time,
            apply_fixer=apply_fixer,
            use_stream_iterator=use_stream_iterator,
            output_type=output_type,
            output_filename=output_filename
        )

        # Check and process request
        self.request = parse_request(
            request, check_and_process=True, definitions=definitions)
        self.logger.debug(f"Checked and processed request: {self.request}")

        # Get parallelization key
        self.parallel_key = self.get_parallel_key(self.request)
        print(self.parallel_key)

        # Get list of requests
        requests = self.get_partial_requests()
        print(requests)

        # Get partial results
        with concurrent.futures.ProcessPoolExecutor(self.n_proc) as executor:
            futures = executor.map(retrieving_fn, requests)
        partial_results = list(futures)

        # Merge partial results
        self.ds = self.merge_results(partial_results, self.parallel_key)

        return self.ds