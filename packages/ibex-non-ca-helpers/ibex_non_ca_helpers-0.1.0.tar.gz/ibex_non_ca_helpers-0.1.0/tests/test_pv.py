# type: ignore
import pytest

from ibex_non_ca_helpers.pv import waveform_to_string


def check_waveform(input_value, expected_value):
    assert expected_value in waveform_to_string(input_value)


def create_waveform_from_list(input_list) -> str:
    if len(input_list) != 0 and isinstance(input_list[0], str):
        return "".join(input_list)
    return "".join([chr(i) for i in input_list])


def test_GIVEN_short_list_of_strings_WHEN_waveform_converted_to_string_THEN_result_contains_a_string_of_strings():
    # Arrange
    test_waveform = ["hello", "world"]

    expected_value = create_waveform_from_list(test_waveform)

    # Act

    # Assert
    check_waveform(test_waveform, expected_value)


def test_GIVEN_long_list_of_strings_WHEN_waveform_converted_to_string_THEN_result_contains_a_string_of_strings():
    # Arrange
    test_waveform = ["this", "is", "a", "long", "list", "of", "strings!"]

    expected_value = create_waveform_from_list(test_waveform)

    # Act

    # Assert
    check_waveform(test_waveform, expected_value)


def test_GIVEN_short_list_of_numbers_WHEN_waveform_converted_to_string_THEN_result_contains_string_of_unicode_chars_for_numbers():
    # Arrange
    test_waveform = [1, 2, 3, 4]

    expected_value = create_waveform_from_list(test_waveform)

    # Act

    # Assert
    check_waveform(test_waveform, expected_value)


def test_GIVEN_list_of_numbers_containing_0_WHEN_waveform_converted_to_string_THEN_result_terminates_at_character_before_0():
    # Arrange
    test_waveform = [1, 2, 3, 4, 0, 5, 6, 7, 8, 9]

    expected_value = create_waveform_from_list([1, 2, 3, 4])

    # Act

    # Assert
    check_waveform(test_waveform, expected_value)


def test_GIVEN_long_list_of_numbers_WHEN_waveform_converted_to_string_THEN_result_contains_string_of_unicode_chars_for_numbers():
    # Arrange
    max_unichr = 128
    length = 1000
    test_waveform = [max(i % max_unichr, 1) for i in range(1, length)]

    expected_value = create_waveform_from_list(test_waveform)

    # Act

    # Assert
    check_waveform(test_waveform, expected_value)


def test_GIVEN_negative_integer_in_waveform_WHEN_waveform_converted_to_string_THEN_result_raises_value_error():
    # Arrange
    test_waveform = [-1]

    # Act

    # Assert
    with pytest.raises(ValueError):
        waveform_to_string(test_waveform)
