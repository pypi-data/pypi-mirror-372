from contextlib import contextmanager
import re
from typing import Union, Callable, Optional, Tuple, List
from py4j.protocol import Py4JJavaError
from pyspark.sql import functions as F, SparkSession
from pyspark.sql.column import Column
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.session import SparkSession
from pyspark.sql.types import StructType, ArrayType


QUERY_PARAMS_WHITELIST = [
    "ad_name",
    "adset_id",
    "adset_name",
    "alertType",
    "aur_so",
    "aur_me",
    "aur_ca",
    "aur_x",
    "authorOrSource",
    "bff",
    "blocketse",
    "campaign_id",
    "campaign_name",
    "cb",
    "cbl1",
    "cbl2",
    "ccca",
    "ccce",
    "ccco",
    "cchb",
    "ccmp",
    "ccsc",
    "ccsd",
    "ccsu",
    "cctr",
    "cf",
    "cg",
    "channel",
    "ck",
    "csz",
    "cxcb",
    "cxcg",
    "cxcn",
    "cxcr",
    "cxcs",
    "cxcu",
    "cxcw",
    "cxcy",
    "cxdw",
    "cxpf",
    "cxpt",
    "dcb",
    "diet",
    "f",
    "fbclid",
    "filter",
    "finnMail",
    "free",
    "fu",
    "gb",
    "gclid",
    "itm_campaign",
    "itm_content",
    "itm_medium",
    "itm_source",
    "ks",
    "kwsn",
    "lid",
    "mainIngredient",
    "maxKcal",
    "me",
    "mealType",
    "minRating",
    "mkt_tok",
    "ms",
    "mye",
    "mys",
    "name",
    "ov",
    "p",
    "page",
    "pe",
    "pinnedEntry",
    "placement",
    "plo",
    "previousAnswer",
    "previousQuestion",
    "ps",
    "pw",
    "pwsig",
    "q",
    "sh",
    "site_source_name",
    "soeg",
    "sort",
    "sortOrder",
    "source",
    "st",
    "theme",
    "typeOfDish",
    "utm_campaign",
    "utm_content",
    "utm_id",
    "utm_medium",
    "utm_source",
    "utm_term",
    "utrustning_dragkrok",
    "videoId",
]


def get_spark_setting_value(spark: SparkSession, name: str) -> Optional[str]:
    """
    Return the value of a spark setting if it's set, otherwise None.
    """
    try:
        value = spark.conf.get(name)
    except Py4JJavaError as e:
        if str(e.java_exception).startswith("java.util.NoSuchElementException"):
            value = None
        else:
            raise e
    return value


@contextmanager
def tmp_spark_setting(spark: SparkSession, name: str, value: str) -> None:
    """
    A context manager that temporarily changes a spark setting.
    """
    prev_setting_value = get_spark_setting_value(spark, name)
    try:
        spark.conf.set(name, value)
        yield
    finally:
        if prev_setting_value is not None:
            spark.conf.set(name, prev_setting_value)
        else:
            spark.conf.unset(name)


def get_col(col: Union[Column, str]) -> Column:
    """
    Return a Column of `col`, which is a column name or a Column instance.
    """
    return col if isinstance(col, Column) else F.col(col)


def get_missing_fields(defined_schema: StructType, inferred_schema: StructType) -> List[str]:
    """
    Compares two PySpark schemas and returns a list of missing fields in the defined schema.

    Args:
        defined_schema (StructType): The PySpark schema to compare against.
        inferred_schema (StructType): The PySpark schema to compare with.

    Returns:
        List[str]: A list of missing fields in the defined schema.
    """
    missing_list = []

    def check_missing_fields(defined_schema: StructType, inferred_schema: StructType, prefix: str = ''):
        for field in inferred_schema.fields:
            field_name = prefix + field.name
            if field.name not in [f.name for f in defined_schema.fields]:
                missing_list.append(field_name)
            elif isinstance(field.dataType, StructType):
                # recursively check for missing fields in nested StructType
                check_missing_fields(defined_schema[field.name].dataType, field.dataType, field_name + '.')
            elif isinstance(field.dataType, ArrayType) and isinstance(field.dataType.elementType, StructType):
                # recursively check for missing fields in nested StructType inside ArrayType
                check_missing_fields(defined_schema[field.name].dataType.elementType, field.dataType.elementType, field_name + '.')

    check_missing_fields(defined_schema, inferred_schema)
    return missing_list


def get_upsert_dict(df: DataFrame, exclude_list: List[str] = [], updates_alias: str = "updates") -> dict:
    """
    Returns a dictionary with all columns to be included in an upsert. 
    """

    return {col: f"{updates_alias}.{col}" for col in df.columns if col not in exclude_list}


def empty_str_to_null(col: Union[Column, str], trim_spaces: bool = False) -> Column:
    original_col = get_col(col)
    if trim_spaces:
        transformed_col = F.trim(original_col)
    else:
        transformed_col = original_col

    return F.when(transformed_col == F.lit(""), None).otherwise(original_col)


def extract_uuid(col: Union[Column, str], str_prefix: str) -> Column:
    """
    Extract the UUID value from `col` that has a `str_prefix`.
    """
    c = get_col(col)
    uuid_pattern = "([0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12})"
    return F.regexp_extract(c, f"(?i)^{str_prefix}{uuid_pattern}", 1)


def pseudonymize(col: Union[Column, str], key: Union[str, "SensitiveValue"] = None, hash_func: Callable = F.sha1) -> Column:
    """
    Hash `col` concatenated with `key` (defaults to '') using `hash_func` (defaults to SHA-1).
    """
    c = get_col(col)

    if key is None:
        hashkey = F.lit("")
    elif isinstance(key, SensitiveValue):
        hashkey = F.lit(key.unmasked)
    elif isinstance(key, str):
        hashkey = F.lit(key)
    else:
        raise ValueError(f"{type(key)} is not supported for `key` argument.")

    hcol = F.when(c.isNull() | (F.trim(c) == F.lit("")), None).otherwise(F.concat(c, hashkey))
    return hash_func(hcol)


def xxhash(col):
    """
    Apply xxhash64() spark function to column values, but for null or empty string values
    return null instead of a hashed value.
    """
    c = get_col(col)
    return F.when(c.isNull() | (F.trim(c) == F.lit("")), None).otherwise(F.xxhash64(c))


def empty_array_to_null(col_name: str) -> Column:
    c = get_col(col_name)
    return F.when(F.expr(f"size({col_name})") == 0, None).otherwise(c)


def regexp_replace_groups(col: Union[str, Column], *pattern_replacement_pairs: Tuple[str, str]):
    """
    Run regexp_replace on a `col` with multiple `pattern_replacement_pairs`.

    Example:
    >>> regexp_replace_groups(item, ("[A-Z]", "A"), ("[a-z]", "a"), ("\d", "0"))
    """
    col = get_col(col)
    for pattern, replacement in pattern_replacement_pairs:
        col = F.regexp_replace(col, pattern, replacement)
    return col


def mask_id_string(item: Column) -> Column:
    """
    Mask strings that look like IDs. For strings that contain no digits, return them as is.
    For numberic strings and UUIDs replace all alphanumeric chars with zeroes. For strings
    that contain a mix of letters, numbers, and symbos replace letters with a/A (preserving
    case) and digits with zeroes, while keeping any other characters unchanged.
    """
    return F.when(
        # no numbers -> not an id
        item.rlike(r"^[^\d]*$"),
        item
    ).when(
        # only numbers -> for sure an ID
        item.rlike(r"^\d+$"),
        F.regexp_replace(item, r"\d", "0")
    ).when(
        # uuid -> id, mask
        item.rlike(r"^[0-9A-Za-z]{8}-([0-9A-Za-z]{4}-){3}[0-9A-Za-z]{12}$"),
        "00000000-0000-0000-0000-000000000000"
    ).otherwise(
        # a mix of letters, numbers, symbos -> mask all letters and digits to be safe
        regexp_replace_groups(item, ("[A-Z]", "A"), ("[a-z]", "a"), ("\d", "0"))
    )


def parse_timestamp_string(col: Column) -> Column:
    """
    Convert a timestamp string into a timestamp data type. 12 and 24 hour variants
    are supported. In gerenal the yyyy-mm-ddTHH:mm:ss with a time zone id is expected (ISO 8601).
    Fractions of a second are optional.
    """
    c = get_col(col)

    return F.when(
      c.startswith('+'), None
    ).when(
        ~c.rlike("[AEFPaefp][mM]"),  # 24-hour format
        F.to_timestamp(c, "yyyy-MM-dd'T'H[H]:mm:ss[.SSSSSSSSS]VV")
    ).otherwise(                     # 12-hour am/pm format
        F.to_timestamp(F.translate(c, "EFef", "PApa"), "yyyy-MM-dd'T'h[h]:mm:ss[.SSSSSSSSS][ a]VV[ a]")
    )


def redact_param(array_element):
    redaction_value = "__redacted__"

    key_value = F.split(array_element, "=", 2)
    param_name = key_value.getItem(0)

    return F.when(
        param_name.isin(QUERY_PARAMS_WHITELIST), array_element
    ).otherwise(
        F.concat(param_name, F.lit("=" + redaction_value))
    )


def redact_query_string(col):
    c = get_col(col)

    params_array = F.array_remove(F.split(c, "&"), "")

    redacted_params_array = F.transform(params_array, redact_param)

    return F.array_join(redacted_params_array, "&")


def redact_email(col, redaction_value="__redacted_email__"):
    """
    Replace a string that matches a basic format of an email with
    """
    c = get_col(col)

    email_pattern = r"[\w+\-%.]+(@|%40)[\w-.]+\.[A-Za-z]{2,63}"

    return F.regexp_replace(c, email_pattern, redaction_value)
  

def redact_ids(col, redaction_value="__redacted_id__"):
    """
    Replace a string that matches the format of an id
    """
    
    c = get_col(col)
    
    # Matches 'id-6_or_more_digit_number' OR '6_or_more_digit_number'
    ad_id_pattern = r"id-\d{6,}|\d{6,}"
    
    return F.regexp_replace(c, ad_id_pattern, redaction_value)
  
  
def redact_url(col):
    """
    Redact url query params that aren't in the params whitelist and values that
    look like emails in the url path.
    """
    c = get_col(col)
  
    url_base_and_fragment = F.split(c, "((?<!\/)#(?!\/))", 2) # Look for a # that is not part of the path (e.g: NOT /#/)
    url_fragment = url_base_and_fragment.getItem(1) # null if no fragment
    url_base_and_query = F.split(url_base_and_fragment.getItem(0), r"\?", 2)
    url_base = url_base_and_query.getItem(0)
    url_query = url_base_and_query.getItem(1) # null if no query

    redacted_url_base = redact_email(url_base)
    redacted_url_base = redact_ids(redacted_url_base)
    redacted_query = redact_query_string(url_query)

    url_with_redacted_query = F.when(
        url_query.isNotNull(), F.concat_ws("?", redacted_url_base, redacted_query)
    ).otherwise(
        redacted_url_base
    )

    return F.when(
        url_fragment.isNull(), url_with_redacted_query
    ).otherwise(
        F.concat_ws("#", url_with_redacted_query, url_fragment)
    )


class SensitiveValue:
    prefix = "sensitive"
    quote_open = "<<"
    quote_close = ">>"

    def __init__(
        self, value: str,
        skip_match_check: bool = False,
        spark : Optional[SparkSession] = None
    ) -> None:
        if not isinstance(value, str):
            raise ValueError(f"Only string `value` is supported but passed {type(value)}")

        self.length = len(value)
        self.redacted = self.wrap_value(value)
        self.spark = spark if spark is not None else SparkSession.getActiveSession()
        self.check_redaction_conf(skip_match_check)

    def wrap_value(self, value: str):
        return "".join((self.prefix, self.quote_open, value, self.quote_close,))

    @property
    def raw_value_start_pos(self):
        """
        Return 0-based starting position index of the raw value in the redacted string.
        """
        return len(self.prefix) + len(self.quote_open)

    @property
    def redaction_pattern(self):
        """
        Return expected reduction regex pattern.
        """
        return self.wrap_value(".*?")

    def check_redaction_conf(self, skip_match_check: bool = False) -> None:
        """
        Check if Spark redaction config is set as expected and raise RuntimeError
        if not, because it may lead to leaking the sensitive value.
        """
        conf_name = "spark.sql.redaction.string.regex"
        conf_value = get_spark_setting_value(self.spark, conf_name)

        if conf_value != self.redaction_pattern:
            raise RuntimeError(
                f"The value of {conf_name} `{conf_value}`"
                + f" does not match expected value `{self.redaction_pattern}`"
            )

        if not skip_match_check:
            m = re.match(conf_value, self.redacted)
            if m is None:
                raise RuntimeError("The redaction regex doesn't match the sensitive string.")
            elif m[0] != self.redacted:
                raise RuntimeError("The redaction regex doesn't fully match the sensitive string.")

    @property
    def unmasked(self) -> Column:
        """
        Return the sensitive value as a pyspark Column. The transformations including
        the random offset are designed to make spark not print the literal string value
        in the logs. Instead it will print the masked value in a chain of transformations.
        """
        redacted_val_col = F.lit(self.redacted)
        start_offset = F.floor(F.lit(self.raw_value_start_pos + 1) + F.rand(42)).astype("int")
        return redacted_val_col.substr(start_offset, F.lit(self.length))

    def __repr__(self) -> str:
        return "*********(redacted)"
