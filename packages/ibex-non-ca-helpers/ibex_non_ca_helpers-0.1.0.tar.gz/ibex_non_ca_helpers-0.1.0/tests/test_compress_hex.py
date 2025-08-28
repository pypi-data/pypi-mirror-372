# type: ignore

import pytest

from ibex_non_ca_helpers.compress_hex import (
    compress_and_hex,
    dehex_and_decompress,
    dehex_and_decompress_waveform,
    dehex_decompress_and_dejson,
)


def test_can_dehex_and_decompress():
    expected = b"test123"
    hexed_and_compressed = b"789c2b492d2e31343206000aca0257"
    result = dehex_and_decompress(hexed_and_compressed)
    assert result == expected


def test_can_hex_and_compress():
    to_compress_and_hex = "test123"
    expected = b"789c2b492d2e31343206000aca0257"
    result = compress_and_hex(to_compress_and_hex)
    assert result == expected


def test_non_bytes_given_to_dehex_and_decompress_raises_assertionerror():
    with pytest.raises(AssertionError):
        dehex_and_decompress("test")


def test_non_string_given_to_compress_and_hex_raises_assertionerror():
    with pytest.raises(AssertionError):
        compress_and_hex(b"test")


def test_non_list_given_to_dehex_and_decompress_waveform_raises_assertionerror():
    with pytest.raises(AssertionError):
        dehex_and_decompress_waveform("test")


def test_dehex_and_decompress_waveform_with_ok_waveform_returns_expected():
    test = [
        55,
        56,
        57,
        99,
        56,
        98,
        53,
        54,
        52,
        97,
        99,
        99,
        99,
        57,
        52,
        99,
        52,
        101,
        53,
        53,
        100,
        50,
        53,
        49,
        53,
        48,
        52,
        97,
        99,
        98,
        99,
        57,
        50,
        99,
        50,
        56,
        52,
        56,
        50,
        100,
        48,
        50,
        51,
        49,
        57,
        51,
        102,
        50,
        57,
        51,
        52,
        48,
        53,
        52,
        55,
        49,
        52,
        57,
        53,
        49,
        98,
        99,
        49,
        49,
        56,
        99,
        54,
        49,
        48,
        56,
        54,
        53,
        56,
        48,
        97,
        56,
        100,
        99,
        102,
        99,
        49,
        50,
        49,
        48,
        53,
        53,
        54,
        48,
        48,
        97,
        50,
        54,
        56,
        100,
        57,
        53,
        54,
        50,
        48,
        49,
        101,
        49,
        99,
        53,
        49,
        51,
        54,
        52,
    ]

    res = dehex_and_decompress_waveform(test)

    assert res == b'["alice", "flipper", "bob", "str_2", "str_1", "str", "mot", "p5", "p3"]'


def test_dehex_decompress_dejson():
    expected = {"key1": "value1", "key2": "value2"}
    assert (
        dehex_decompress_and_dejson(
            b"789cab56ca4ead3454b252502a4bcc294d3554d251008918c1458c946a01c39b0a9b"
        )
        == expected
    )
