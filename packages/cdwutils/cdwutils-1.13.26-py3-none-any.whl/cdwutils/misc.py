import datetime as dt
import json
import random
import string
from typing import Any, Callable, Collection, Container, Iterable, List, Tuple, Union


class OnlyOnceList(list):
    """
    OnlyOnceList is a subclass of list that stores a cache of items that have been added
    and raises a ValueError if an object that's in the cache is appended. The cache persists
    through the lifetime of the class instance and isn't affected by methods like clear()
    or remove().
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_items = set(self)
        if len(self.cached_items) < len(self):
            raise ValueError(f"OnlyOnceList was initialized with duplicate items.")

    def append(self, obj):
        if obj in self.cached_items:
            raise ValueError(f"{obj} has already been added")
        else:
            self.cached_items.add(obj)
            super().append(obj)


def parse_json_lines(raw_data: str, skip_errors: bool = False):
    """
    Parse a str representation of a JSON lines file and return a list of dict.
    """
    lines = [r for r in raw_data.strip().split("\n")]
    rows = []
    for ln in lines:
        try:
            record = json.loads(ln)
        except json.JSONDecodeError as e:
            print(f"Could not decode line: {ln}")
            if skip_errors:
                continue
            else:
                raise e
        else:
            rows.append(record)
    return rows


def to_datetime(d, str_format="%Y-%m-%d") -> dt.datetime:
    """
    Return a datetime object by converting provided `d` if possible.
    Supports datetime.date or str in ISO format.
    """
    if isinstance(d, dt.datetime):
        return d
    elif isinstance(d, dt.date):
        return dt.datetime(d.year, d.month, d.day)
    elif isinstance(d, str):
        return dt.datetime.strptime(d, str_format)
    else:
        raise ValueError(f"Unsupported input: {d} of type {type(d)}")


def days_in_date_range(d1, d2) -> int:
    """
    Return the number of days between date `d1` and `d2` inclusive.
    """
    d1, d2 = to_datetime(d1), to_datetime(d2)
    return abs((d2 - d1)).days + 1


def get_str_format_fields(s: str) -> set:
    """
    Return a set of format field names found in the string `s`. If format strings are found
    returns an empty set. Note, that if the string has unnamed format fields the set will
    contain and empty string.

    >>> get_str_format_fields("abc_{var}")
    {'var'}
    >>> get_str_format_fields("abc_{var1}_{var2}")
    {'var1', 'var2'}
    >>> get_str_format_fields("abc")
    set()
    >>> get_str_format_fields("abc")
    set()
    >>> get_str_format_fields("abc_{{escaped_var}}")
    set()
    """
    parsed_iter = string.Formatter().parse(s)
    fields = set()
    for (literal_text, field_name, format_spec, conversion) in parsed_iter:
        if field_name is not None:
            fields.add(field_name)
    return fields


def split_on_condition(
        iterable: Iterable,
        condition: Callable[[Any], bool],
        item_adder: Callable[[Container, Any], None] = lambda lst, val: lst.append(val),
        out_type: type = None
) -> Tuple[Collection, Collection]:
    """
    Splits `iterable` on `condition` and returns a tuple of two iterables of the same type
    or two collections of the type `out_type`.

    Parameters:
    iterable: Iterable
        an iterable to split based on condition (note: to split a dict pass dict.items())
    condition: Callable
        a function that runs on each item of `iterable` and retuns a bool used to split
        the itmes into the True and False groups.
    item_adder: Callable
        a function of 2 args that adds an item to the output collections by mutating the first arg
    out_type: type
        type of the output collections

    >>> split_on_condition([1, 2, 3, 4, 5], condition=lambda val: val % 2 == 0)
    ([2, 4], [1, 3, 5])
    >>> split_on_condition({"a": 1, "b": 2,}.items(), condition=lambda kv: kv[1] % 2 == 0, out_type=list)
    ([('b', 2)], [('a', 1)])
    """
    iter_type = type(iterable)
    cond_true = out_type() if out_type is not None else iter_type()
    cond_false = out_type() if out_type is not None else iter_type()
    for item in iterable:
        if condition(item):
            item_adder(cond_true, item)
        else:
            item_adder(cond_false, item)
    return cond_true, cond_false


def split_dict_on_condition(d: dict, condition: Callable[[Any], bool]) -> Tuple[dict, dict]:
    """
    Splits dict `d` on `condition` function and returns a tuple of two dicts.
    """

    def adder(d, key_val_tuple):
        key, val = key_val_tuple
        d[key] = val

    return split_on_condition(d.items(), condition, adder, out_type=dict)


def render_value_literal(value, data_type="string"):
    data_type = data_type.lower()
    if data_type == "string":
        return f"'{value}'"
    elif data_type in {"number", "bigint", "int", "long", "float", "double"}:
        return f"{value}"
    elif data_type == "date":
        return f"DATE '{value}'"
    elif data_type == "timestamp":
        return f"TIMESTAMP '{value}'"
    elif data_type in {"bool", "boolean"}:
        return "TRUE" if value else "FALSE"


def value_not_equal_condition(
        columns: List[str],
        destination_alias: str = "destination",
        updates_alias: str = "updates"
):
    condition_parts = []
    for name in columns:
        expr = f"{destination_alias}.{name} != {updates_alias}.{name}"
        condition_parts.append(expr)
    return " OR ".join(condition_parts)


def random_hex():
    return "{:X}".format(random.randint(1000, 1000000000))


def yesterday(base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
              string_format: str = "%Y-%m-%d") -> dt.date:
    """
    Return yesterday's date by default, or one day back relative to the input `base_date`
    Note: `string_format` is only used if the input `base_date` is a string
    """

    return to_datetime(base_date, string_format).date() - dt.timedelta(days=1)


def yesterday_str(
        base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
        output_string_format: str = "%Y-%m-%d",
        input_string_format: str = "%Y-%m-%d",
) -> str:
    return yesterday(base_date, input_string_format).strftime(output_string_format)


def today() -> dt.date:
    return dt.date.today()


def tomorrow(
        base_date: Union[dt.datetime, dt.date, str] = today(),
        string_format: str = "%Y-%m-%d"
) -> dt.date:
    return to_datetime(base_date, string_format).date() + dt.timedelta(days=1)


def today_str(fmt="%Y-%m-%d") -> str:
    return today().strftime(fmt)


def is_end_of_month(
        base_date: Union[dt.datetime, dt.date, str] = today(),
        string_format: str = "%Y-%m-%d"
) -> bool:
    return tomorrow(base_date, string_format).month != to_datetime(base_date, string_format).month


def is_start_of_month(
        base_date: Union[dt.datetime, dt.date, str] = today(),
        string_format: str = "%Y-%m-%d"
) -> bool:
    return yesterday(base_date, string_format).month != to_datetime(base_date, string_format).month


def previous_month_end(
        base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
        string_format: str = "%Y-%m-%d",
        *,
        safe=False,
) -> dt.date:
    """
    Return last day of previous month by default, or last day of the month relative to the input 'base date'
    """

    if safe and is_end_of_month(base_date, string_format):
        month_end = to_datetime(base_date).date()
    else:
        month_end = to_datetime(base_date, string_format).date().replace(day=1) - dt.timedelta(days=1)

    return month_end


def previous_month_start(
        base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
        string_format: str = "%Y-%m-%d",
        *,
        safe=False
) -> dt.date:
    """
        Return previous month start date
    """
    if safe and is_start_of_month(base_date, string_format):
        month_start = to_datetime(base_date).date()
    else:
        month_start = previous_month_end(base_date, string_format, safe=safe).replace(day=1)

    return month_start


def date_sub_days(
        days,
        base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
        string_format: str = "%Y-%m-%d",

) -> dt.date:
    """
     Return a date days before the current date by default, or days before date relative to the input 'base date'
    """
    return to_datetime(base_date, string_format).date() - dt.timedelta(days=days)


def previous_week_start(
        base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
        input_string_format: str = "%Y-%m-%d",
) -> dt.date:
    """
    Return previous week start date related to base date
    """
    week_ago = date_sub_days(7, base_date, input_string_format)
    return week_ago - dt.timedelta(week_ago.weekday())


def sunday_safe_week_start(
        base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
        input_string_format: str = "%Y-%m-%d",
) -> dt.date:
    """
    Return current week start date if base date is sunday otherwise return previous week start date related to base date
    """
    if is_sunday(base_date):
        return current_week_start(base_date)
    else:
        return previous_week_start(base_date, input_string_format)


def previous_week_end(
        base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
        input_string_format: str = "%Y-%m-%d",
) -> dt.date:
    return previous_week_start(base_date, input_string_format) + dt.timedelta(6)


def sunday_safe_week_end(
        base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
        input_string_format: str = "%Y-%m-%d",
) -> dt.date:
    return sunday_safe_week_start(base_date, input_string_format) + dt.timedelta(6)


def is_sunday(
        base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
        string_format: str = "%Y-%m-%d"):
    return to_datetime(base_date, string_format).date().weekday() == 6


def current_week_start(
        base_date: Union[dt.datetime, dt.date, str] = dt.date.today(),
        string_format: str = "%Y-%m-%d"
):
    return to_datetime(base_date, string_format).date() - dt.timedelta(
        to_datetime(base_date, string_format).date().weekday())


def to_bool(value: Any) -> bool:
    """
    Convert a value (expected str) to bool.

    >>> to_bool("true")
    True
    >>> to_bool("false")
    False
    >>> to_bool("No   ")
    False
    """
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        str_value = value.strip().lower()
        if str_value in {"true", "yes"}:
            return True
        elif str_value in {"false", "no"}:
            return False
        else:
            raise ValueError(f"Invalid boolean value: {str_value}")
    else:
        raise ValueError(f"Unsupported value type: {type(value)}")
