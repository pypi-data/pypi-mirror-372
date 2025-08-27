import asyncio
from typing import Dict
from unittest.mock import mock_open


def future_with_result(result):
    future = asyncio.Future()
    future.set_result(result)
    return future


def future_with_exception(exception):
    future = asyncio.Future()
    future.set_exception(exception)
    return future


def create_mock_open(filename_to_data_map: Dict[str, str]):
    return lambda *args, **kwargs: mock_open(read_data=filename_to_data_map[args[0]])(
        *args, **kwargs
    )


class MockConfig:
    def get(key):
        if key == "region":
            return "us-west-2"


def compare_tag_list(actual, expected, key_name: str = "Key"):
    assert len(actual) == len(expected)
    sorted_actual = sorted(actual, key=lambda x: x[key_name])
    sorted_expected = sorted(expected, key=lambda x: x[key_name])
    pairs = zip(sorted_actual, sorted_expected)
    for x, y in pairs:
        assert x == y
