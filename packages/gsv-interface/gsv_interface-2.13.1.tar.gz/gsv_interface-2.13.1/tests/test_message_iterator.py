import pytest

from gsv.iterator import MessageIterator, StreamMessageIterator


def test_message_iterator(grib_file_small):
    """
    Test MessageIterator with a GRIB file
    containing 10 messages. Test that all
    messages are correctly retrieved by
    checking the header and tail of each
    message. Test that after the last messages
    a StopIteration is raised.
    """
    iterator = MessageIterator(grib_file_small)
    N_MESSAGES = 10

    # Check messages are correctly retrieved
    for _ in range(N_MESSAGES):
        msg = next(iterator)
        assert msg[:4] == b'GRIB'  # Check GRIB header
        assert msg[-4:] == b'7777'  # Check GRIB tail

    # Test iteration ends after last message
    with pytest.raises(StopIteration):
        next(iterator)

def test_stream_message_iterator(grib_file_small):
    """
    Docstrings
    """
    iterator = StreamMessageIterator(grib_file_small)
    N_MESSAGES = 10

    # Check messages are correctly retrieved
    for _ in range(N_MESSAGES):
        msg = next(iterator)
        assert msg[:4] == b'GRIB'  # Check GRIB header
        assert msg[-4:] == b'7777'  # Check GRIB tail

    # Test iteration ends after last message
    with pytest.raises(StopIteration):
        next(iterator)


def test_message_iterator_grib2(grib2_file):
    """
    Docstrings
    """
    iterator = MessageIterator(grib2_file)

    # Check messages are correctly retrieved
    for msg in iterator:
        assert msg[:4] == b'GRIB'  # Check GRIB header
        assert msg[-4:] == b'7777'  # Check GRIB tail

    # Test iteration ends after last message
    with pytest.raises(StopIteration):
        next(iterator)

def test_stream_message_iterator_grib2(grib2_file):
    """
    Docstrings
    """
    iterator = StreamMessageIterator(grib2_file)

    # Check messages are correctly retrieved
    for msg in iterator:
        assert msg[:4] == b'GRIB'  # Check GRIB header
        assert msg[-4:] == b'7777'  # Check GRIB tail

    # Test iteration ends after last message
    with pytest.raises(StopIteration):
        next(iterator)


def test_skip_trailling(grib_file_trailling):
    """
    Docstrings
    """
    iterator = MessageIterator(grib_file_trailling)

    # Check messages are correctly retrieved
    msg = next(iterator)
    assert msg[:4] == b'GRIB'  # Check GRIB header
    assert msg[-4:] == b'7777'  # Check GRIB tail

    # Test four bytes are correctly skipped
    offset = iterator.next_message_offset
    iterator._check_message_available()
    assert iterator.next_message_offset == offset + 4
    msg = next(iterator)

    # Test gaps bigger than 100 raise an exception
    # Test iteration ends after last message
    with pytest.raises(Exception):
        iterator._check_message_available()

def test_skip_trailling_stream(grib_file_trailling):
    """
    Docstrings
    """
    iterator = StreamMessageIterator(grib_file_trailling)

    # Check messages are correctly retrieved
    msg = next(iterator)
    assert msg[:4] == b'GRIB'  # Check GRIB header
    assert msg[-4:] == b'7777'  # Check GRIB tail

    # Test four bytes are correctly skipped
    # Resulting offset should be 8 places further
    # 4 for skipped bytes and 4 for b'GRIB' bytes
    offset = iterator.datareader.tell()
    iterator._check_message_available()
    assert iterator.datareader.tell() == offset + 8
    iterator._read_message_after_grib_header()

    # Test gaps bigger than 100 raise an exception
    # Test iteration ends after last message
    with pytest.raises(Exception):
        iterator._check_message_available()
