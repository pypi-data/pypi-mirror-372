from typing import BinaryIO


class MessageIterator():
    """
    A class to iterate over GRIB message in a file-like object.

    Both GRIB1 and GRIB2 standards are supported.

    Attributes:
    -----------
    datareader : BinaryIO
        File object containing the GRIB messages concatenated.
        Can be any object with the basic IO methods .read()
        .seek() and .tell(). In special it can be a
        pyfdb.datareader object.
    max_trailing_bytes : int
        Maximum permitted empty bytes between messages.
    next_message_offset: int
        Offset in bytes of the next available message
    """

    def __init__(self, datareader: BinaryIO, max_trailing_bytes=100):
        """
        Parameters:
        -----------
        datareader : BinaryIO
            File object containing the GRIB messages concatenated.
            Can be any object with the basic IO methods .read()
            .seek() and .tell(). In special it can be a
            pyfdb.datareader object.
        max_trailing_bytes : int, optional
            Maximum permitted empty bytes between messages.
            Default is 100
        """
        self.datareader = datareader
        self.max_trailing_bytes = max_trailing_bytes
        self.next_message_offset = 0

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return the next available GRIB message on ``datareader``

        This is done by first searching next b'GRIB' word which
        indicates the beginning of the GRIB message. Once found,
        ``next_message_offset`` is set.

        Then the total length of the message is found by looking
        in specific offset locations.

        Finally the message is read and returned.

        Returns:
        --------
        bytes
            GRIB message as rar binary stream.
        """
        self._check_message_available()
        total_length = self._read_total_length()
        message = bytes(self.datareader.read(total_length))
        self.next_message_offset = self.datareader.tell()

        return message

    def _check_message_available(self):
        """
        Set ``next_message_offset`` to start of next available message.

        To check for available messages, the first four bytes
        are read starting from ``next_message_offset``.

        This bytes must equal b'GRIB' for a valid messages. If this
        condition is meet the function ends without errors.

        If first four bytes are not b'GRIB' the ``next_message_offset``
        advances one position and the same check is repeated, until
        a valid message is found.

        If process is repeated more than ``max_trailing_bytes`` times
        an exception is raised. This might indicate that GRIB message
        is not correctly formatted and therefore that the iterator
        cannot properly understand it.

        If at some moment there is less than 4 bytes left starting from
        ``next_message_offset``, it means end of file has been reached
        and StopIteration is raised.
        """
        n_trials = 0

        while True:

            # Read first four bytes
            self.datareader.seek(self.next_message_offset)
            grib_init = self.datareader.read(4)

            if len(grib_init) < 4:  # End of byte stream
                raise StopIteration

            elif grib_init != b'GRIB':  # Skip trailing bytes after final '7777'
                self.next_message_offset += 1
                n_trials +=1

                # Abort if too many trials
                if n_trials > self.max_trailing_bytes:
                    raise Exception(
                        "Too many bytes between messages. " \
                        "GRIB file is probably not well formatted."
                        )

            else:  # Break loop when initial 'GRIb' is found
                break


    def _read_total_length(self) -> int:
        """
        Read total length of next available GRIB message.

        This is done by looking in specific offset positions
        in the binary message, depending on the GRIB version.

        For GRIB1 the total length is encoded as a 3 byte integer
        (byteorder='big', unsigned) in the bytes at
        positions 5-7 (first byte=1).

        For GRIB2 the total length is encoded as a 8 byte integer
        (byteorder='big', unsigned) in the bytes at
        positions 9-16 (first byte=1).

        Returns:
        --------
        int
            Total length of next available GRIB message in bytes
        """
        # Ensure offset is on 5th byte of message
        self.datareader.seek(self.next_message_offset + 4)

        # Read total length (assuming GRIB1) and edition number
        total_length = int.from_bytes(
            self.datareader.read(3), byteorder='big', signed=False
            )
        edition_number = int.from_bytes(
            self.datareader.read(1), byteorder='big', signed=False
            )

        # Check edition number and reset offset to beginning
        if edition_number == 1:
            self.datareader.seek(self.datareader.tell() - 8)

        elif edition_number == 2:
            total_length = int.from_bytes(
                self.datareader.read(8), byteorder='big', signed=False
                )
            self.datareader.seek(self.datareader.tell() - 16)

        return total_length
