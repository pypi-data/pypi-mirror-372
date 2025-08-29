import json
import requests
import re
import random
import math
from typing import Any, Callable, Dict, Tuple, List, Union
from typeguard import typechecked
from clyp.ErrorHandling import ClypRuntimeError


@typechecked
class Response:
    """
    A wrapper class for HTTP responses.
    """

    def __init__(self, content: str) -> None:
        """
        Initialize the Response object.

        :param content: The content of the HTTP response as a string.
        """
        self._content: str = content

    def json(self) -> Dict[str, Any]:
        """
        Convert the JSON response content to a Python dictionary.

        :return: Parsed JSON content as a dictionary.
        :raises RuntimeError: If JSON decoding fails.
        """
        try:
            return json.loads(self._content)
        except json.JSONDecodeError as e:
            raise ClypRuntimeError(f"Failed to decode JSON: {e}") from e

    def content(self) -> str:
        """
        Get the raw content of the response.

        :return: The raw content as a string.
        """
        return self._content

    def text(self) -> str:
        """
        Get the response content as text.

        :return: The content as a string.
        """
        return str(self._content)


@typechecked
def fetch(url: str, timeout: int = 10) -> Response:
    """
    Fetch the content from a given URL.

    :param url: The URL to fetch.
    :param timeout: Timeout for the request in seconds (default is 10).
    :return: A Response object containing the fetched content.
    :raises RuntimeError: If the request fails.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return Response(response.text)
    except requests.RequestException as e:
        raise ClypRuntimeError(f"Failed to fetch {url}: {e}") from e


@typechecked
def is_empty(value: Any) -> bool:
    """
    Check if a value is empty.

    :param value: The value to check.
    :return: True if the value is empty, False otherwise.
    """
    if value is None:
        return True
    if isinstance(value, (str, list, dict, set, tuple)):
        return len(value) == 0
    return False


@typechecked
def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.

    :param text: The input string to slugify.
    :return: A slugified version of the input string.
    """
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9-]", "", text)
    text = re.sub(
        r"-+", "-", text
    )  # Replace multiple consecutive dashes with a single dash
    return text.strip("-")  # Remove leading and trailing dashes


@typechecked
def toString(value: Any) -> str:
    """
    Converts a value to its string representation.
    """
    return str(value)


@typechecked
def read_file(file_path: str, *args: Any, **kwargs: Any) -> str:
    """
    Read the content of a file.

    :param file_path: The path to the file.
    :return: The content of the file as a string.
    :raises RuntimeError: If the file cannot be read.
    """
    try:
        with open(file_path, *args, **kwargs) as file:
            return file.read()
    except IOError as e:
        raise ClypRuntimeError(f"Failed to read file {file_path}: {e}") from e


@typechecked
def write_file(file_path: str, content: str, *args: Any, **kwargs: Any) -> None:
    """
    Write content to a file.

    :param file_path: The path to the file.
    :param content: The content to write to the file.
    :raises RuntimeError: If the file cannot be written.
    """
    try:
        with open(file_path, "w", *args, **kwargs) as file:
            file.write(content)
    except IOError as e:
        raise ClypRuntimeError(f"Failed to write to file {file_path}: {e}") from e


@typechecked
def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator to cache the results of a function based on its arguments.

    :param func: The function to be memoized.
    :return: A wrapper function that caches results.
    """
    cache: Dict[Tuple[Any, ...], Any] = {}

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


@typechecked
def time_it(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator to measure the execution time of a function.

    :param func: The function to be timed.
    :return: A wrapper function that prints the execution time.
    """
    import time

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result

    return wrapper


@typechecked
def is_prime(n: int) -> bool:
    """
    Check if a number is prime.

    :param n: The number to check.
    :return: True if the number is prime, False otherwise.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


@typechecked
def to_roman_numerals(num: int) -> str:
    """
    Convert an integer to a Roman numeral.

    :param num: The integer to convert.
    :return: The Roman numeral representation of the integer.
    :raises ClypRuntimeError: If the number is out of range (1-3999).
    """
    if not (1 <= num <= 3999):
        raise ClypRuntimeError("Number must be between 1 and 3999")

    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]

    roman_numeral = ""
    for i in range(len(val)):
        while num >= val[i]:
            roman_numeral += syms[i]
            num -= val[i]

    return roman_numeral


@typechecked
def chance(percentage: Any) -> bool:
    """
    Determine if an event occurs based on a given percentage chance.

    :param percentage: The chance of the event occurring (0-100). Can be a float or a string like '25%'.
    :return: True if the event occurs, False otherwise.
    :raises ValueError: If the percentage is not valid.
    """
    if isinstance(percentage, str):
        if percentage.endswith("%"):
            percentage = percentage[:-1]
        try:
            percentage = float(percentage)
        except ValueError:
            raise ValueError(
                "Invalid percentage format. Must be a number or a string like '25%'."
            )

    if not (0 <= percentage <= 100):
        raise ValueError("Percentage must be between 0 and 100")

    import random

    return random.random() < (percentage / 100)


@typechecked
def duration(seconds: int) -> Callable[[Callable[[], None]], None]:
    """
    Execute a given function repeatedly for a specified duration in seconds.

    :param seconds: The duration in seconds.
    :return: A callable that accepts a function to execute.
    """
    if not isinstance(seconds, int) or seconds < 0:
        raise ValueError("Duration must be a non-negative integer")

    def wrapper(func: Callable[[], None]) -> None:
        import time

        start_time = time.time()
        while time.time() - start_time < seconds:
            func()

    return wrapper


@typechecked
def retry_with_cooldown(
    function: Callable[..., Any],
    retries: int = 3,
    cooldown: int = 1,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Retry a function with a specified number of retries and cooldown period.

    :param function: The function to retry.
    :param retries: Number of retries (default is 3).
    :param cooldown: Cooldown period in seconds between retries (default is 1).
    :param args: Positional arguments to pass to the function.
    :param kwargs: Keyword arguments to pass to the function.
    :return: The result of the function if successful.
    :raises RuntimeError: If all retries fail.
    """
    import time

    if retries < 1:
        raise ValueError("Retries must be at least 1")
    if cooldown < 0:
        raise ValueError("Cooldown must be non-negative")

    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < retries:
                time.sleep(cooldown)
            else:
                raise RuntimeError(
                    f"Function failed after {retries} attempts: {last_exception}"
                ) from last_exception


@typechecked
def throttle(
    function: Callable[..., Any], limit: int = 1, period: int = 1
) -> Callable[..., Any]:
    """
    Throttle a function to limit its execution rate.

    :param function: The function to throttle.
    :param limit: Maximum number of calls allowed in the period (default is 1).
    :param period: Time period in seconds for the limit (default is 1).
    :return: A throttled version of the function.
    """
    import time
    from collections import deque

    if limit < 1:
        raise ValueError("Limit must be at least 1")
    if period <= 0:
        raise ValueError("Period must be greater than 0")

    timestamps = deque()

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        current_time = time.time()
        while timestamps and timestamps[0] < current_time - period:
            timestamps.popleft()

        if len(timestamps) < limit:
            timestamps.append(current_time)
            return function(*args, **kwargs)
        else:
            raise RuntimeError("Function call limit exceeded. Try again later.")

    return wrapper


@typechecked
def flatten(list_of_lists: List[List[Any]]) -> List[Any]:
    """
    Flatten a list of lists into a single list.

    :param list_of_lists: A list containing other lists.
    :return: A flattened list containing all elements.
    """
    return [item for sublist in list_of_lists for item in sublist]


def chunk(items: List[Any], size: int) -> List[List[Any]]:
    """
    Split a list into chunks of a specified size.

    :param items: The list of items to chunk.
    :param size: The size of each chunk.
    :return: A list of chunks.
    """
    if not isinstance(items, list):
        raise ValueError("Items must be a list")
    if not isinstance(size, int) or size <= 0:
        raise ValueError("Size must be a positive integer")

    return [items[i : i + size] for i in range(0, len(items), size)]


def benchmark(func: Callable[[], Any], iterations: int = 1000) -> float:
    """
    Benchmark a function by measuring its execution time over a number of iterations.

    :param func: The function to benchmark.
    :param iterations: The number of iterations to run (default is 1000).
    :return: The average execution time in seconds.
    """
    import time

    if not callable(func):
        raise ValueError("Function must be callable")
    if not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("Iterations must be a positive integer")

    start_time = time.time()
    for _ in range(iterations):
        func()
    end_time = time.time()

    return (end_time - start_time) / iterations


@typechecked
def cache(
    ttl: Union[int, str, float],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Cache the result of a function for a specified time-to-live (TTL).

    :param ttl: Time-to-live in seconds (can be an int, float, or string like '5s').
    :return: A decorator that caches the function's result.
    """
    import time
    from functools import wraps

    if isinstance(ttl, str):
        units = {
            "s": 1,
            "sec": 1,
            "secs": 1,
            "seconds": 1,
            "m": 60,
            "min": 60,
            "mins": 60,
            "minutes": 60,
            "h": 3600,
            "hr": 3600,
            "hrs": 3600,
            "hours": 3600,
            "d": 86400,
            "day": 86400,
            "days": 86400,
            "w": 604800,
            "wk": 604800,
            "wks": 604800,
            "weeks": 604800,
            "y": 31536000,
            "yr": 31536000,
            "yrs": 31536000,
            "years": 31536000,
        }
        match = re.match(r"^(\d+(?:\.\d+)?)\s*(\w+)$", ttl.strip())
        if match:
            value, unit = match.groups()
            if unit in units:
                ttl = float(value) * units[unit]
            else:
                raise ValueError(f"Unsupported time unit: {unit}")
        else:
            raise ValueError("TTL must be a number followed by a valid time unit")

    if not isinstance(ttl, (int, float)) or ttl <= 0:
        raise ValueError("TTL must be a positive number")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache_data: Dict[Tuple[Any, ...], Tuple[Any, float]] = {}

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, frozenset(kwargs.items()))
            current_time = time.time()
            if key in cache_data:
                value, timestamp = cache_data[key]
                if current_time - timestamp < ttl:
                    return value
            value = func(*args, **kwargs)
            cache_data[key] = (value, current_time)
            return value

        return wrapper

    return decorator


@typechecked
def trace(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator to trace the execution of a function, printing its arguments and return value.

    :param func: The function to trace.
    :return: A wrapper function that prints the trace information.
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result}")
        return result

    return wrapper


@typechecked
def ping(host: str, timeout: int = 1) -> Union[float, bool]:
    """
    Ping a host to check if it is reachable.

    :param host: The hostname or IP address to ping.
    :param timeout: Timeout for the ping in seconds (default is 1).
    :return: True if the host is reachable, False otherwise.
    :raises RuntimeError: If the ping command fails.
    """
    import subprocess

    try:
        output = subprocess.check_output(
            ["ping", "-c", "1", "-W", str(timeout), host],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        match = re.search(r"time=(\d+\.\d+) ms", output)
        if match:
            return float(match.group(1))
        return False
    except subprocess.CalledProcessError as e:
        raise ClypRuntimeError(f"Ping failed for {host}: {e.output}") from e


@typechecked
def random_choice_weighted(choices: List[Tuple[Any, float]]) -> Any:
    """
    Randomly select an item from a list of choices with associated weights.

    :param choices: A list of tuples where each tuple contains an item and its weight.
    :return: A randomly selected item based on the weights.
    :raises ValueError: If the total weight is zero or negative.
    """
    import random

    if not choices:
        raise ValueError("Choices list cannot be empty")

    total_weight = sum(weight for _, weight in choices)
    if total_weight <= 0:
        raise ValueError("Total weight must be positive")

    rand_val = random.uniform(0, total_weight)
    cumulative_weight = 0.0
    for item, weight in choices:
        cumulative_weight += weight
        if rand_val < cumulative_weight:
            return item

    return None


@typechecked
def debug(value: Any, label: str = "") -> Any:
    """
    Debug utility that prints value with optional label and returns the value.
    
    :param value: Value to debug
    :param label: Optional label for the debug output
    :return: The original value unchanged
    """
    import inspect
    import pprint
    
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    line_number = frame.f_lineno
    
    prefix = f"[DEBUG {filename}:{line_number}]"
    if label:
        prefix += f" {label}:"
    
    if isinstance(value, (dict, list, tuple, set)):
        print(f"{prefix}")
        pprint.pprint(value, width=120, depth=10)
    else:
        print(f"{prefix} {repr(value)}")
    
    return value


@typechecked
def profile(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to profile function execution time and memory usage.
    
    :param func: Function to profile
    :return: Wrapped function with profiling
    """
    import time
    import tracemalloc
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Start memory tracing
        tracemalloc.start()
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            execution_time = end_time - start_time
            print(f"[PROFILE] {func.__name__}:")
            print(f"  Execution time: {execution_time:.4f}s")
            print(f"  Memory usage: {current / 1024 / 1024:.2f} MB")
            print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")
        
        return result
    
    return wrapper


@typechecked
def json_parse(json_str: str) -> Union[Dict[str, Any], List[Any], str, int, float, bool, None]:
    """
    Parse JSON string to Python object with enhanced error reporting.
    
    :param json_str: JSON string to parse
    :return: Parsed JSON object
    :raises ClypRuntimeError: If JSON parsing fails
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ClypRuntimeError(
            f"[V200] JSON parsing failed: {e}\n"
            f"💡 Tip: Check for missing quotes, trailing commas, or malformed structure\n"
            f"💡 Position: line {e.lineno}, column {e.colno}\n"
            f"💡 Context: {json_str[max(0, e.pos-20):e.pos+20]}"
        )


@typechecked
def json_stringify(obj: Any, pretty: bool = False) -> str:
    """
    Convert Python object to JSON string.
    
    :param obj: Object to convert to JSON
    :param pretty: Whether to format with indentation
    :return: JSON string
    """
    try:
        if pretty:
            return json.dumps(obj, indent=2, ensure_ascii=False, default=str)
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError) as e:
        raise ClypRuntimeError(f"[V201] Failed to serialize to JSON: {e}")


@typechecked
def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with dict2 values taking precedence.
    
    :param dict1: First dictionary
    :param dict2: Second dictionary (takes precedence)
    :return: Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


@typechecked
def get_nested(obj: Union[Dict[str, Any], None], path: str, default: Any = None) -> Any:
    """
    Get nested value from dictionary using dot notation.
    
    :param obj: Dictionary to search
    :param path: Dot-separated path (e.g., "user.profile.name")
    :param default: Default value if path not found
    :return: Value at path or default
    """
    keys = path.split('.')
    current = obj
    
    try:
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    except (KeyError, TypeError):
        return default


@typechecked
def set_nested(obj: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
    """
    Set nested value in dictionary using dot notation.
    
    :param obj: Dictionary to modify
    :param path: Dot-separated path (e.g., "user.profile.name")
    :param value: Value to set
    :return: Modified dictionary
    """
    keys = path.split('.')
    current = obj
    
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return obj


@typechecked
def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """
    Clamp value between min and max bounds.
    
    :param value: Value to clamp
    :param min_val: Minimum value
    :param max_val: Maximum value
    :return: Clamped value
    """
    return max(min_val, min(value, max_val))


@typechecked
def lerp(start: Union[int, float], end: Union[int, float], t: float) -> float:
    """
    Linear interpolation between two values.
    
    :param start: Start value
    :param end: End value  
    :param t: Interpolation factor (0.0 to 1.0)
    :return: Interpolated value
    """
    return start + t * (end - start)


@typechecked
def unique(items: List[Any]) -> List[Any]:
    """
    Get unique items from list while preserving order.
    
    :param items: List of items
    :return: List with unique items
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


@typechecked
def group_by(items: List[Any], key_func: Callable[[Any], Any]) -> Dict[Any, List[Any]]:
    """
    Group list items by key function result.
    
    :param items: List of items to group
    :param key_func: Function to extract grouping key
    :return: Dictionary of grouped items
    """
    groups = {}
    for item in items:
        key = key_func(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups


@typechecked
def partition(items: List[Any], predicate: Callable[[Any], bool]) -> Tuple[List[Any], List[Any]]:
    """
    Partition list into two lists based on predicate.
    
    :param items: List of items to partition
    :param predicate: Function to test items
    :return: Tuple of (items matching predicate, items not matching)
    """
    true_items = []
    false_items = []
    
    for item in items:
        if predicate(item):
            true_items.append(item)
        else:
            false_items.append(item)
    
    return true_items, false_items


@typechecked
def zip_dict(keys: List[Any], values: List[Any]) -> Dict[Any, Any]:
    """
    Create dictionary from two lists of keys and values.
    
    :param keys: List of keys
    :param values: List of values
    :return: Dictionary mapping keys to values
    """
    return dict(zip(keys, values))


@typechecked
def pick(obj: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Create new dictionary with only specified keys.
    
    :param obj: Source dictionary
    :param keys: Keys to pick
    :return: New dictionary with picked keys
    """
    return {key: obj[key] for key in keys if key in obj}


@typechecked
def omit(obj: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Create new dictionary excluding specified keys.
    
    :param obj: Source dictionary
    :param keys: Keys to omit
    :return: New dictionary without omitted keys
    """
    return {key: value for key, value in obj.items() if key not in keys}


@typechecked
def format_bytes(size: Union[int, float]) -> str:
    """
    Format byte size as human readable string.
    
    :param size: Size in bytes
    :return: Formatted string (e.g., "1.5 MB")
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    if size == 0:
        return "0 B"
    
    import math
    unit_index = min(int(math.log(abs(size), 1024)), len(units) - 1)
    formatted_size = size / (1024 ** unit_index)
    
    if formatted_size.is_integer():
        return f"{int(formatted_size)} {units[unit_index]}"
    else:
        return f"{formatted_size:.1f} {units[unit_index]}"


@typechecked  
def format_duration(seconds: Union[int, float]) -> str:
    """
    Format duration in seconds as human readable string.
    
    :param seconds: Duration in seconds
    :return: Formatted string (e.g., "2h 30m 15s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds:.0f}s"
        return f"{minutes}m"
    
    hours = int(minutes // 60)
    remaining_minutes = minutes % 60
    
    parts = [f"{hours}h"]
    if remaining_minutes > 0:
        parts.append(f"{remaining_minutes}m")
    if remaining_seconds > 0:
        parts.append(f"{remaining_seconds:.0f}s")
    
    return " ".join(parts)


@typechecked  
def async_map(func: Callable[[Any], Any], items: List[Any]) -> List[Any]:
    """
    Apply a function to all items in a list asynchronously (simulated).
    
    :param func: Function to apply
    :param items: List of items to process
    :return: List of results
    """
    import asyncio
    
    async def async_apply():
        tasks = [asyncio.create_task(asyncio.coroutine(lambda: func(item))()) for item in items]
        return await asyncio.gather(*tasks)
    
    try:
        return asyncio.run(async_apply())
    except Exception:
        # Fallback to synchronous processing
        return [func(item) for item in items]


@typechecked
def pipe(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Create a pipeline of functions where output of one becomes input of next.
    
    :param functions: Functions to chain together
    :return: Composed function
    """
    def pipeline(value: Any) -> Any:
        result = value
        for func in functions:
            result = func(result)
        return result
    return pipeline


@typechecked
def compose(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Compose functions from right to left (mathematical composition).
    
    :param functions: Functions to compose
    :return: Composed function
    """
    def composition(value: Any) -> Any:
        result = value
        for func in reversed(functions):
            result = func(result)
        return result
    return composition


@typechecked
def curry(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Convert a function to accept arguments one at a time.
    
    :param func: Function to curry
    :return: Curried function
    """
    def curried(*args: Any, **kwargs: Any) -> Any:
        import inspect
        sig = inspect.signature(func)
        param_count = len([p for p in sig.parameters.values() if p.default == p.empty])
        
        if len(args) + len(kwargs) >= param_count:
            return func(*args, **kwargs)
        else:
            def partial(*more_args: Any, **more_kwargs: Any) -> Any:
                return curried(*(args + more_args), **{**kwargs, **more_kwargs})
            return partial
    return curried


@typechecked
def memoize_with_ttl(ttl_seconds: int = 300) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Memoize function results with time-to-live expiration.
    
    :param ttl_seconds: Time to live for cached results in seconds
    :return: Decorator function
    """
    import time
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache: Dict[str, Tuple[Any, float]] = {}
        
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"{args}_{kwargs}"
            current_time = time.time()
            
            if key in cache:
                value, timestamp = cache[key]
                if current_time - timestamp < ttl_seconds:
                    return value
                else:
                    del cache[key]
            
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result
        
        return wrapper
    return decorator


@typechecked
def tap(func: Callable[[Any], None]) -> Callable[[Any], Any]:
    """
    Apply a side effect function and return the original value (useful for debugging).
    
    :param func: Side effect function to apply
    :return: Function that applies side effect but returns original value
    """
    def tapper(value: Any) -> Any:
        func(value)
        return value
    return tapper


@typechecked
def when(condition: Callable[[Any], bool], action: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Conditionally apply a function based on a predicate.
    
    :param condition: Predicate function
    :param action: Function to apply if condition is true
    :return: Function that conditionally applies action
    """
    def conditional(value: Any) -> Any:
        if condition(value):
            return action(value)
        return value
    return conditional


@typechecked
def unless(condition: Callable[[Any], bool], action: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Apply a function unless a condition is true.
    
    :param condition: Predicate function
    :param action: Function to apply if condition is false
    :return: Function that conditionally applies action
    """
    def conditional(value: Any) -> Any:
        if not condition(value):
            return action(value)
        return value
    return conditional


@typechecked
def safe_get(obj: Union[Dict[str, Any], List[Any]], key: Union[str, int], default: Any = None) -> Any:
    """
    Safely get a value from a dictionary or list without raising exceptions.
    
    :param obj: Dictionary or list to get value from
    :param key: Key or index to access
    :param default: Default value if key doesn't exist
    :return: Value or default
    """
    try:
        return obj[key]
    except (KeyError, IndexError, TypeError):
        return default


@typechecked
def safe_call(func: Callable[..., Any], *args: Any, default: Any = None, **kwargs: Any) -> Any:
    """
    Safely call a function, returning a default value if it raises an exception.
    
    :param func: Function to call
    :param args: Positional arguments
    :param default: Default value if function raises exception
    :param kwargs: Keyword arguments
    :return: Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception:
        return default


@typechecked
def chain(*iterables: List[Any]) -> List[Any]:
    """
    Chain multiple iterables into a single list.
    
    :param iterables: Iterables to chain
    :return: Flattened list
    """
    result = []
    for iterable in iterables:
        result.extend(iterable)
    return result


@typechecked
def take(n: int, iterable: List[Any]) -> List[Any]:
    """
    Take the first n elements from an iterable.
    
    :param n: Number of elements to take
    :param iterable: Source iterable
    :return: List of first n elements
    """
    return list(iterable[:n])


@typechecked
def drop(n: int, iterable: List[Any]) -> List[Any]:
    """
    Drop the first n elements from an iterable.
    
    :param n: Number of elements to drop
    :param iterable: Source iterable
    :return: List without first n elements
    """
    return list(iterable[n:])


@typechecked
def take_while(predicate: Callable[[Any], bool], iterable: List[Any]) -> List[Any]:
    """
    Take elements from an iterable while predicate is true.
    
    :param predicate: Function that returns True to continue taking
    :param iterable: Source iterable
    :return: List of elements taken while predicate was true
    """
    result = []
    for item in iterable:
        if predicate(item):
            result.append(item)
        else:
            break
    return result


@typechecked
def drop_while(predicate: Callable[[Any], bool], iterable: List[Any]) -> List[Any]:
    """
    Drop elements from an iterable while predicate is true.
    
    :param predicate: Function that returns True to continue dropping
    :param iterable: Source iterable
    :return: List of remaining elements after dropping
    """
    result = []
    dropping = True
    for item in iterable:
        if dropping and predicate(item):
            continue
        dropping = False
        result.append(item)
    return result


@typechecked
def find_index(predicate: Callable[[Any], bool], iterable: List[Any]) -> int:
    """
    Find the index of the first element that satisfies the predicate.
    
    :param predicate: Function that returns True for matching element
    :param iterable: Source iterable
    :return: Index of first matching element, -1 if not found
    """
    for i, item in enumerate(iterable):
        if predicate(item):
            return i
    return -1


@typechecked
def count_by(predicate: Callable[[Any], bool], iterable: List[Any]) -> int:
    """
    Count elements that satisfy a predicate.
    
    :param predicate: Function that returns True for elements to count
    :param iterable: Source iterable
    :return: Count of matching elements
    """
    return sum(1 for item in iterable if predicate(item))
