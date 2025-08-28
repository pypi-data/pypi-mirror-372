from typing import BinaryIO


class StreamMessageIterator():
    """
    Docstrings

    A class to iterate over GRIB message in a file-like object.

    Both GRIB1 and GRIB2 standards are supported.

    The reading is done in a streaming approcah in which byets
    are only read forward, without moving the file handle offset with
    .seek()..

    Attributes:
    -----------
    datareader : BinaryIO
        File object containing the GRIB messages concatenated.
        Can be any object with the basic IO methods .read()
        and .tell(). The .seek() method is not used. In special,
        it can be a pyfdb.datareader object.
    max_trailing_bytes : int
        Maximum permitted empty bytes between messages.
    """

    def __init__(self, datareader: BinaryIO, max_trailing_bytes=100):
        """
        Docstrings
        """
        self.datareader = datareader
        self.max_trailing_bytes = max_trailing_bytes

    def __iter__(self):
        return self

    def __next__(self):
        self._check_message_available()
        message = self._read_message_after_grib_header()
        return message

    def _check_message_available(self):
        """
        Docstrings
        """
        n_trials = 0
        grib_header = self.datareader.read(4)

        while True:

            if len(grib_header) < 4:  # End of byte stream
                raise StopIteration

            elif grib_header != b'GRIB':  # Skip trailing bytes after final '7777'
                grib_header = grib_header[1:] + self.datareader.read(1)
                n_trials +=1

                # Abort if too many trials
                if n_trials > self.max_trailing_bytes:
                    raise Exception(
                        "Too many bytes between messages. " \
                        "GRIB file is probably not well formatted."
                        )

            else:  # Break loop when initial 'GRIB' is found
                break

    def _read_total_length(self) -> int:
        """
        Docstrings
        """
        # Get edition number from 8th byte
        edition_number = int.from_bytes(
            self.grib_first_16_bytes[7:8], byteorder='big', signed=False
            )

        # Check edition number and reset offset to beginning
        if edition_number == 1:
            total_length = int.from_bytes(
                self.grib_first_16_bytes[4:7], byteorder='big', signed=False
                )

        elif edition_number == 2:
            total_length = int.from_bytes(
                self.grib_first_16_bytes[8:16], byteorder='big', signed=False
                )

        return total_length

    def _read_message_after_grib_header(self):
        self.grib_first_16_bytes = b'GRIB' + self.datareader.read(12)
        total_length = self._read_total_length()
        message = self.grib_first_16_bytes + self.datareader.read(total_length - 16)
        return message
