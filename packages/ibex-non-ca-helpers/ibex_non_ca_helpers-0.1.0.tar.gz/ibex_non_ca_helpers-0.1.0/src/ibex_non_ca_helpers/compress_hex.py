import binascii
import json
import zlib
from typing import Any, List

from ibex_non_ca_helpers.pv import waveform_to_string


def compress_and_hex(value: str) -> bytes:
    """Compresses the inputted string and encodes it as hex.

    Args:
        value (str): The string to be compressed
    Returns:
        bytes : A compressed and hexed version of the inputted string
    """
    assert type(value) is str, (
        "Non-str argument passed to compress_and_hex, maybe Python 2/3 compatibility issue\n"
        "Argument was type {} with value {}".format(value.__class__.__name__, value)
    )
    compr = zlib.compress(bytes(value, "utf-8"))
    return binascii.hexlify(compr)


def dehex_and_decompress(value: bytes) -> bytes:
    """Decompresses the inputted string, assuming it is in hex encoding.

    Args:
        value (bytes): The string to be decompressed, encoded in hex

    Returns:
        bytes : A decompressed version of the inputted string
    """
    assert type(value) is bytes, (
        "Non-bytes argument passed to dehex_and_decompress, maybe Python 2/3 compatibility issue\n"
        "Argument was type {} with value {}".format(value.__class__.__name__, value)
    )
    return zlib.decompress(binascii.unhexlify(value))


def dehex_and_decompress_waveform(value: List[int]) -> bytes:
    """Decompresses the inputted waveform,
     assuming it is an array of integers representing characters (null terminated).

    Args:
        value (list[int]): The string to be decompressed

    Returns:
        bytes : A decompressed version of the inputted string
    """
    assert type(value) is list, (
        "Non-list argument passed to dehex_and_decompress_waveform\n"
        "Argument was type {} with value {}".format(value.__class__.__name__, value)
    )

    unicode_rep = waveform_to_string(value)
    bytes_rep = unicode_rep.encode("ascii")
    return dehex_and_decompress(bytes_rep)


def dehex_decompress_and_dejson(value: bytes) -> Any:  # noqa: ANN401
    """
    Convert string from zipped hexed json to a python representation
    :param value: value to convert
    :return: python representation of json
    """
    return json.loads(dehex_and_decompress(value))
