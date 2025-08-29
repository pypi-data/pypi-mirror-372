import pytest
import requests
from unittest.mock import patch, mock_open, MagicMock
import subprocess
from clyp.stdlib import (
    Response,
    fetch,
    is_empty,
    slugify,
    read_file,
    write_file,
    memoize,
    time_it,
    is_prime,
    to_roman_numerals,
    toString,
    chance,
    duration,
    retry_with_cooldown,
    throttle,
    flatten,
    chunk,
    benchmark,
    cache,
    trace,
    ping,
    random_choice_weighted,
)
from clyp.ErrorHandling import ClypRuntimeError


# Tests for Response class
def test_response_json_success():
    response = Response('{"key": "value"}')
    assert response.json() == {"key": "value"}


def test_response_json_failure():
    response = Response("not a json")
    with pytest.raises(ClypRuntimeError, match="Failed to decode JSON"):
        response.json()


def test_response_content():
    response = Response("some content")
    assert response.content() == "some content"


def test_response_text():
    response = Response("some text")
    assert response.text() == "some text"


# Tests for fetch function
@patch("clyp.stdlib.requests.get")
def test_fetch_success(mock_get):
    mock_response = MagicMock()
    mock_response.text = "Success"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    response = fetch("http://example.com")
    assert isinstance(response, Response)
    assert response.content() == "Success"
    mock_get.assert_called_once_with("http://example.com", timeout=10)


@patch("clyp.stdlib.requests.get")
def test_fetch_failure(mock_get):
    mock_get.side_effect = requests.RequestException("Failed to connect")
    with pytest.raises(ClypRuntimeError, match="Failed to fetch http://example.com"):
        fetch("http://example.com")


# Tests for is_empty function
@pytest.mark.parametrize(
    "value, expected",
    [
        (None, True),
        ("", True),
        ([], True),
        ({}, True),
        (set(), True),
        ((), True),
        ("not empty", False),
        ([1, 2], False),
        ({"a": 1}, False),
        ({1, 2}, False),
        ((1,), False),
        (0, False),
        (False, False),
    ],
)
def test_is_empty(value, expected):
    assert is_empty(value) == expected


# Tests for slugify function
@pytest.mark.parametrize(
    "text, expected",
    [
        ("  Hello World  ", "hello-world"),
        ("!@#$Foo Bar123", "foo-bar123"),
        ("---multiple---dashes---", "multiple-dashes"),
    ],
)
def test_slugify(text, expected):
    assert slugify(text) == expected


# Tests for read_file function
@patch("builtins.open", new_callable=mock_open, read_data="file content")
def test_read_file_success(mock_file):
    content = read_file("any/path")
    assert content == "file content"
    mock_file.assert_called_once_with("any/path")


@patch("builtins.open", side_effect=IOError("File not found"))
def test_read_file_failure(mock_file):
    with pytest.raises(ClypRuntimeError, match="Failed to read file any/path"):
        read_file("any/path")


# Tests for write_file function
@patch("builtins.open", new_callable=mock_open)
def test_write_file_success(mock_file):
    write_file("any/path", "new content")
    mock_file.assert_called_once_with("any/path", "w")
    mock_file().write.assert_called_once_with("new content")


@patch("builtins.open", side_effect=IOError("Permission denied"))
def test_write_file_failure(mock_file):
    with pytest.raises(ClypRuntimeError, match="Failed to write to file any/path"):
        write_file("any/path", "content")


# Tests for memoize decorator
def test_memoize():
    mock_func = MagicMock(return_value=42)
    mock_func.__name__ = "mock_func"
    memoized_func = memoize(mock_func)

    # Call twice with same args
    assert memoized_func(1, 2) == 42
    assert memoized_func(1, 2) == 42
    mock_func.assert_called_once_with(1, 2)

    # Call with different args
    mock_func.return_value = 100
    assert memoized_func(3, 4) == 100
    assert mock_func.call_count == 2


# Tests for time_it decorator
def test_time_it(capsys):
    @time_it
    def sample_func():
        return "done"

    assert sample_func() == "done"
    captured = capsys.readouterr()
    assert "sample_func took" in captured.out
    assert "seconds" in captured.out


# Tests for is_prime function
@pytest.mark.parametrize(
    "n, expected",
    [
        (2, True),
        (3, True),
        (5, True),
        (7, True),
        (11, True),
        (13, True),
        (1, False),
        (4, False),
        (6, False),
        (8, False),
        (9, False),
        (10, False),
        (0, False),
        (-1, False),
    ],
)
def test_is_prime(n, expected):
    assert is_prime(n) == expected


# Tests for to_roman_numerals function
@pytest.mark.parametrize(
    "num, expected",
    [
        (1, "I"),
        (3, "III"),
        (4, "IV"),
        (9, "IX"),
        (58, "LVIII"),
        (1994, "MCMXCIV"),
        (3999, "MMMCMXCIX"),
    ],
)
def test_to_roman_numerals(num, expected):
    assert to_roman_numerals(num) == expected


def test_to_roman_numerals_out_of_range():
    with pytest.raises(ClypRuntimeError, match="Number must be between 1 and 3999"):
        to_roman_numerals(0)
    with pytest.raises(ClypRuntimeError, match="Number must be between 1 and 3999"):
        to_roman_numerals(4000)


# Tests for toString
@pytest.mark.parametrize(
    "value, expected",
    [
        (123, "123"),
        ([1, 2], "[1, 2]"),
        (None, "None"),
        (True, "True"),
        ({"a": 1}, "{'a': 1}"),
    ],
)
def test_toString(value, expected):
    assert toString(value) == expected


# Tests for chance
@patch("random.random")
def test_chance(mock_random):
    mock_random.return_value = 0.4
    assert chance(50) is True
    assert chance("50%") is True
    mock_random.return_value = 0.6
    assert chance(50) is False
    assert chance(100) is True
    assert chance(0) is False


def test_chance_invalid_input():
    with pytest.raises(ValueError, match="Percentage must be between 0 and 100"):
        chance(-10)
    with pytest.raises(ValueError, match="Percentage must be between 0 and 100"):
        chance(110)
    with pytest.raises(
        ValueError,
        match="Invalid percentage format. Must be a number or a string like '25%'.",
    ):
        chance("abc")


# Tests for duration
@patch("time.time")
def test_duration(mock_time):
    mock_time.side_effect = [0, 1, 2, 3]
    mock_func = MagicMock()

    def func_to_run():
        mock_func()

    runner = duration(3)
    runner(func_to_run)
    assert mock_func.call_count == 2


def test_duration_invalid_input():
    with pytest.raises(ValueError, match="Duration must be a non-negative integer"):
        duration(-1)


# Tests for retry_with_cooldown
@patch("time.sleep")
def test_retry_with_cooldown_success(mock_sleep):
    mock_func = MagicMock(side_effect=[Exception("fail"), "success"])
    result = retry_with_cooldown(mock_func, retries=2, cooldown=1)
    assert result == "success"
    assert mock_func.call_count == 2
    mock_sleep.assert_called_once_with(1)


def test_retry_with_cooldown_failure():
    mock_func = MagicMock(side_effect=Exception("fail"))
    with pytest.raises(RuntimeError, match="Function failed after 3 attempts: fail"):
        retry_with_cooldown(mock_func, retries=3, cooldown=0)
    assert mock_func.call_count == 3


def test_retry_with_cooldown_invalid_input():
    with pytest.raises(ValueError, match="Retries must be at least 1"):
        retry_with_cooldown(lambda: None, retries=0)
    with pytest.raises(ValueError, match="Cooldown must be non-negative"):
        retry_with_cooldown(lambda: None, cooldown=-1)


# Tests for throttle
@patch("time.time")
def test_throttle(mock_time):
    mock_time.side_effect = [0, 0.5, 0.8, 1.1, 1.5, 2.2]
    mock_func = MagicMock()
    throttled_func = throttle(mock_func, limit=2, period=1)

    throttled_func()
    throttled_func()
    with pytest.raises(RuntimeError):
        throttled_func()

    throttled_func()
    with pytest.raises(RuntimeError):
        throttled_func()

    throttled_func()

    assert mock_func.call_count == 4


def test_throttle_invalid_input():
    with pytest.raises(ValueError, match="Limit must be at least 1"):
        throttle(lambda: None, limit=0)
    with pytest.raises(ValueError, match="Period must be greater than 0"):
        throttle(lambda: None, period=0)


# Tests for flatten
def test_flatten():
    assert flatten([[1, 2], [3, 4], [5]]) == [1, 2, 3, 4, 5]
    assert flatten([[], [1], [], [2, 3]]) == [1, 2, 3]
    assert flatten([]) == []


# Tests for chunk
def test_chunk():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunk([1, 2, 3], 1) == [[1], [2], [3]]
    assert chunk([1, 2, 3], 3) == [[1, 2, 3]]
    assert chunk([], 2) == []


def test_chunk_invalid_input():
    with pytest.raises(ValueError, match="Size must be a positive integer"):
        chunk([1, 2, 3], 0)
    with pytest.raises(ValueError, match="Items must be a list"):
        chunk("not a list", 2)


# Tests for benchmark
@patch("time.time", side_effect=[0, 1])
def test_benchmark(mock_time):
    result = benchmark(lambda: None, iterations=100)
    assert result == 1 / 100


def test_benchmark_invalid_input():
    with pytest.raises(ValueError, match="Function must be callable"):
        benchmark("not a function")
    with pytest.raises(ValueError, match="Iterations must be a positive integer"):
        benchmark(lambda: None, iterations=0)


# Tests for cache
@patch("time.time", side_effect=[0, 1, 2.1])
def test_cache(mock_time):
    mock_func = MagicMock(return_value=42)

    @cache(ttl=2)
    def cached_func():
        return mock_func()

    assert cached_func() == 42  # time=0, call
    assert cached_func() == 42  # time=1, from cache
    assert cached_func() == 42  # time=2.1, expired, call
    assert mock_func.call_count == 2


@patch("time.time", side_effect=[0, 1, 2])
def test_cache_with_str_ttl(mock_time):
    mock_func = MagicMock(return_value=1)

    @cache(ttl="1.5s")
    def cached_func():
        return mock_func()

    cached_func()  # time=0
    cached_func()  # time=1
    cached_func()  # time=2, expired
    assert mock_func.call_count == 2


def test_cache_invalid_input():
    with pytest.raises(ValueError, match="TTL must be a positive number"):
        cache(ttl=0)
    with pytest.raises(
        ValueError, match="TTL must be a number followed by a valid time unit"
    ):
        cache(ttl="abc")
    with pytest.raises(ValueError, match="Unsupported time unit: yearz"):
        cache(ttl="1 yearz")


# Tests for trace
def test_trace(capsys):
    @trace
    def sample_func(a, b=None):
        return "result"

    sample_func(1, b=2)
    captured = capsys.readouterr()
    assert "Calling sample_func with args: (1,), kwargs: {'b': 2}" in captured.out
    assert "sample_func returned: result" in captured.out


# Tests for ping
@patch("subprocess.check_output", return_value="time=12.345 ms")
def test_ping_success(mock_check_output):
    assert ping("example.com") == 12.345
    mock_check_output.assert_called_once()


@patch(
    "subprocess.check_output",
    side_effect=subprocess.CalledProcessError(1, "cmd", output="error"),
)
def test_ping_failure(mock_check_output):
    with pytest.raises(ClypRuntimeError, match="Ping failed for example.com: error"):
        ping("example.com")


# Tests for random_choice_weighted
def test_random_choice_weighted():
    choices = [("a", 10), ("b", 0)]
    assert random_choice_weighted(choices) == "a"


@patch("random.uniform")
def test_random_choice_weighted_mocked(mock_uniform):
    choices = [("a", 8), ("b", 4)]
    mock_uniform.return_value = 5
    assert random_choice_weighted(choices) == "a"
    mock_uniform.return_value = 10
    assert random_choice_weighted(choices) == "b"


def test_random_choice_weighted_invalid_input():
    with pytest.raises(ValueError, match="Choices list cannot be empty"):
        random_choice_weighted([])
    with pytest.raises(ValueError, match="Total weight must be positive"):
        random_choice_weighted([("a", 0)])
