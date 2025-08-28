# type: ignore
from unittest.mock import patch

from ibex_non_ca_helpers.macros import get_macro_values


@patch("ibex_non_ca_helpers.macros.os.environ.get", return_value={})
def test_get_macro_values_returns_dict_with_macros_in(environ):
    pass


@patch("ibex_non_ca_helpers.macros.os.environ")
def test_get_macro_values_returns_empty_dict_if_no_macros(environ):
    expected_key_1 = "key1"
    expected_key_2 = "key2"
    expected_value_1 = "value1"
    expected_value_2 = "value2"
    environ.get.return_value = '{"key1": "value1", "key2": "value2"}'
    assert get_macro_values() == {
        expected_key_1: expected_value_1,
        expected_key_2: expected_value_2,
    }
