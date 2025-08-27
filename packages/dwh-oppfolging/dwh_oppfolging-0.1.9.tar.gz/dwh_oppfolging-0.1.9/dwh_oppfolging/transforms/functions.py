"data transforms"
from typing import Any
from functools import reduce
from datetime import datetime
import hashlib
import json
import re
import pendulum.parser
from pendulum.datetime import DateTime as PendulumDateTime
from typing import Iterable, Mapping


def batch_it(it: Iterable, n: int) -> Iterable:
    """Batch the output of an iterable (for example: a generator with yield only)
        i.e. returning another iterator which yields batches
    
    params:
        - it: an iterator
        - n: batch size integer >= 1
        - container: list or tuple (default: list)

    yields:
        list (or tuple) of iterator's output, of at most size n

    example:
    >>> list(batch_it(range(4), n=3))
    [[0, 1, 2], [3]]
    """
    batch = []
    for x in it:
        batch.append(x)
        if len(batch) >= n:
            yield batch
            batch = []
    if len(batch) > 0:
        yield batch


def find_in_dict(mapping: Mapping, path: list, raise_on_missing: bool = False) -> Any | None:
    """
    recursively searches for value at path in dict
    useful for nested dicts
    returns value if found, None otherwise
    if throw_if_missing is set, will throw KeyError instead

    params:
        - mapping: dict, the dict to search
        - path: a list of keys such that item = data[key1][key2][key3]..
        - raise_on_missing (optional), default: False
            throw if item cannot be found

    returns:
        - the value at the path or None

    raises (if set):
        - KeyError
        - possibly other errors if nested value is not a mapping

    examples:
    >>> find_in_dict({0: {1: 2}}, [0, 1])
    2
    >>> find_in_dict({}, [0, 1, 2], True)
    Traceback (most recent call last):
        ...
    KeyError: 0
    """
    if raise_on_missing:
        return reduce(lambda d,k: d[k], path, mapping)
    else:
        try:
            return reduce(lambda d,k: d.get(k), path, mapping) # type: ignore
        except Exception: # pylint: disable=broad-except
            return None


def flatten_dict(mapping: Mapping, sep: str = "_", flatten_lists: bool = False) -> Mapping[str, Any]:
    """
    recursively flattens dict with specified separator
    optionally flatten lists in it as well
    note: all keys become strings

    example:
    >>> flatten_dict({0: {1: 3}, 'z': [1, 2, 3]}, "_", True)
    {'0_1': 3, 'z_0': 1, 'z_1': 2, 'z_2': 3}
    """
    def flatten(mapping: Mapping, parent_key: str = "") -> Mapping:
        items: list[Any] = []
        for key, value in mapping.items():
            flat_key = str(key) if not parent_key else str(parent_key) + sep + str(key)
            if isinstance(value, Mapping):
                items.extend(flatten(value, flat_key).items())
            elif isinstance(value, list) and flatten_lists:
                for it_key, it_value in enumerate(value):
                    items.extend(flatten({str(it_key):it_value}, flat_key).items())
            else:
                items.append((flat_key, value))
        return dict(items)

    return flatten(mapping)


def string_to_naive_norwegian_datetime(
    string: str,
    fmt: str | None = None
) -> datetime:
    """
    Parses string to pendulum datetime, then converts to Norwegian timezone
    (adjusting and adding utc offset, then appending tzinfo) and finally strips the timezone.

    params:
        - string: the string representing some date and time
        - (optional) fmt: an explicit date and time formatting string using pendulumn tokens to parse with
            note: some timezones and tokens may fail, this is an open issue in pendulum.
    returns:
        - pendulum datetime

    example: adjust from incoming timestamp assumed to be at 0 hours, +00:00 UTC
    >>> string_to_naive_norwegian_datetime("2022-05-05").isoformat()
    '2022-05-05T02:00:00'

    example: adjust from incoming timestamp at +00:00 UTC
    >>> string_to_naive_norwegian_datetime("1900-01-01T00:00:00+00:00").isoformat()
    '1900-01-01T01:00:00'

    example: adjust from incoming timezone where day changes, +00:00 UTC
    >>> string_to_naive_norwegian_datetime("1900-01-01T23:00:00+00:00").isoformat()
    '1900-01-02T00:00:00'

    example: adjust from incoming timezone where year changes, +00:00 UTC
    >>> string_to_naive_norwegian_datetime("1900-12-31T23:00:00+00:00").isoformat()
    '1901-01-01T00:00:00'

    example: adjust from incoming timezone where year changes, +00:00 UTC
    (this breaks with pendulum < 3.0.0)
    >>> string_to_naive_norwegian_datetime("1899-12-31T23:00:00+00:00").isoformat()
    '1900-01-01T00:00:00'

    example: specifying the optional format
    >>> string_to_naive_norwegian_datetime("Mon Jan 22 04:21:09 CET 2024", "ddd MMM DD HH:mm:ss z YYYY").isoformat()
    '2024-01-22T04:21:09'

    example: the underlying implementation, pendulum, doesnt support CEST
    >>> pendulum.from_format("Mon Mar 31 04:27:05 CEST 2025", "ddd MMM DD HH:mm:ss z YYYY")
    Traceback (most recent call last):
        ...
    ValueError: Invalid date

    ...but will treat CET (UTC+1) as CEST (UTC+2) if DST is active, so it can be replaced
    >>> pendulum.from_format("Mon Mar 31 04:27:05 CET 2025", "ddd MMM DD HH:mm:ss z YYYY").is_dst()
    True

    >>> pendulum.from_format("Mon Mar 30 04:27:05 CET 2025", "ddd MMM DD HH:mm:ss z YYYY").is_dst()
    False

    ...so the function replaces CEST with CET
    >>> cest, cet = "Mon Mar 30 04:27:05 CEST 2025", "Mon Mar 30 04:27:05 CET 2025"
    >>> fmt = "ddd MMM DD HH:mm:ss z YYYY"
    >>> string_to_naive_norwegian_datetime(cest, fmt) == string_to_naive_norwegian_datetime(cet, fmt)
    True
    """
    # TODO consider switching to dateutil.parser.parse to handle CEST and such.
    string = string.replace("CEST", "CET")
    pdl_dt = pendulum.parser.parse(string) if not fmt else pendulum.from_format(string, fmt)
    assert isinstance(pdl_dt, PendulumDateTime)
    pdl_dt = pdl_dt.in_timezone("Europe/Oslo")
    pdl_dt = pdl_dt.naive()
    return pdl_dt


def string_to_naive_utc0_datetime(
    string: str
) -> datetime:
    """
    Parses string to pendulum datetime, then converts to UTC timezone
    (adjusting and adding utc offset, then appending tzinfo) and finally strips the timezone.
    Converts string to naive pendulum datetime, stripping any timezone info

    examples:
    >>> string_to_naive_utc0_datetime("2022-05-05T05:05:05+01:00").isoformat()
    '2022-05-05T04:05:05'
    >>> string_to_naive_utc0_datetime("2022-05-05").isoformat()
    '2022-05-05T00:00:00'
    >>> string_to_naive_utc0_datetime("1900-01-01").isoformat()
    '1900-01-01T00:00:00'
    """
    pdl_dt = pendulum.parser.parse(string)
    assert isinstance(pdl_dt, PendulumDateTime)
    pdl_dt = pdl_dt.in_timezone("UTC")
    pdl_dt = pdl_dt.naive()
    return pdl_dt


def epoch_to_naive_utc0_datetime(
    epoch: int | float
) -> datetime:
    """
    Parses integer/float to pendulum datetime, representing seconds since unix epoch, and strips the default UTC timezone.
    When converting from milliseconds, divide by 1000 first.

    example: forgetting to divide by 1000
    >>> import sys, pytest
    >>> if sys.platform.startswith('win'):
    ...     pytest.skip("windows unsupported")
    >>> epoch_to_naive_utc0_datetime(1706000773111)
    Traceback (most recent call last):
        ...
    ValueError: year 56031 is out of range

    example: remembering to do it
    >>> epoch_to_naive_utc0_datetime(1706000773111 / 1000).isoformat()
    '2024-01-23T09:06:13.111000'
    """
    pdl_dt = pendulum.from_timestamp(epoch) # default timezone UTC
    assert isinstance(pdl_dt, PendulumDateTime)
    pdl_dt = pdl_dt.naive()
    return pdl_dt


def datetime_to_naive_norwegian_datetime(dt: datetime) -> datetime:
    """converts datetime to naive norwegian datetime

    example:
    >>> datetime_to_naive_norwegian_datetime(datetime.fromisoformat("2022-05-05T05:05:05+01:00")).isoformat()
    '2022-05-05T06:05:05'
    """
    return string_to_naive_norwegian_datetime(dt.isoformat())


def naive_norwegian_datetime_to_naive_utc0_datetime(dt: datetime) -> datetime:
    """converts a naive norwegian datetime to a naive utc0 datetime

    example:
    >>> naive_norwegian_datetime_to_naive_utc0_datetime(datetime.fromisoformat("2023-08-29T21:16:48")).isoformat()
    '2023-08-29T19:16:48'
    """
    assert dt.tzinfo is None
    pdl_dt = PendulumDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
    pdl_dt = pdl_dt.in_timezone("Europe/Oslo").in_timezone("UTC").naive()
    return pdl_dt


def string_to_code(string: str) -> str:
    """converts a string to a code string conforming to dwh standard

    examples:
    >>> string_to_code("/&$  ØrkEn Rotte# *;-")
    'ORKEN_ROTTE'
    >>> string_to_code(" ??? ")
    'UKJENT'
    """
    code = string.upper().replace("Æ", "A").replace("Ø", "O").replace("Å", "AA")
    code = "_".join(
        word
        for word in re.findall(
            r"(\w*)",
            code,
        )
        if word
    )
    code = "UKJENT" if code == "" else code
    return code


def string_to_json(string: str) -> Any:
    """returns json object from string

    example:
    >>> string_to_json('{"x": 1}')
    {'x': 1}
    """
    return json.loads(string)


def json_to_string(data: Any) -> str:
    """returns json-serialized object (string)

    example:
    >>> json_to_string({"x": 1})
    '{"x": 1}'
    """
    return json.dumps(data, ensure_ascii=False)


def bytes_to_string(data: bytes) -> str:
    """returns the utf-8 decoded string

    example:
    >>> bytes_to_string(b'hello world')
    'hello world'
    """
    string = data.decode("utf-8")
    return string


def string_to_bytes(string: str) -> bytes:
    """returns the utf-8 encoded string as bytes

    example:
    >>> string_to_bytes('Hello, world!')
    b'Hello, world!'
    """
    data = string.encode("utf-8")
    return data


def json_bytes_to_string(data: bytes) -> str:
    """Returns json serialized object (string)

    example:
    >>> json_bytes_to_string(b'{"x": 35}')
    '{"x": 35}'
    """
    string = json.dumps(json.loads(data), ensure_ascii=False)
    return string


def bytes_to_sha256_hash(data: bytes) -> str:
    """Returns the sha256 hash of the bytes as a hex-numerical string

    example:
    >>> bytes_to_sha256_hash(b'Hello, world!')
    '315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3'
    """
    sha = hashlib.sha256(data).hexdigest()
    return sha


def string_to_sha256_hash(string: str) -> str:
    """Returns the sha256 hash of the utf-8 encoded string as a hex-numerical string

    example:
    >>> string_to_sha256_hash("Hello, world!")
    '315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3'
    """
    sha = hashlib.sha256(string_to_bytes(string)).hexdigest()
    return sha
