import itertools

from . import dimension_keys
from .brand_providers import get_included_provider_ids
from ..aws.common import get_default_session
from ..aws.s3 import get_common_prefix, get_latest_path, join_path, list_objects, split_uri
from ..etl import add_key_column
from ..misc import to_datetime

BASE_BEHAVIOURAL_URI = "s3://schibsted-analytics-cdw-data-import/pulse/traffic/yellow/pulse-simple/version=1/"


def add_device_key(df):
    """
    Create device key
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_DEVICE.name,
        key_columns=dimension_keys.D_DEVICE.columns,
        output_int64=dimension_keys.D_DEVICE.output_int64,
        replace_nulls_with=dimension_keys.D_DEVICE.replace_nulls_with
    )


def add_category_key(df):
    """
    Create category key
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_CATEGORY.name,
        key_columns=dimension_keys.D_CATEGORY.columns,
        output_int64=dimension_keys.D_CATEGORY.output_int64,
        replace_nulls_with=dimension_keys.D_CATEGORY.replace_nulls_with
    )


def add_provider_key(df):
    """
    Create provider key
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_PROVIDER.name,
        key_columns=dimension_keys.D_PROVIDER.columns,
        output_int64=dimension_keys.D_PROVIDER.output_int64,
        replace_nulls_with=dimension_keys.D_PROVIDER.replace_nulls_with
    )


def add_provider_url_key(df):
    """
    Create provider url key
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_PROVIDER_URL.name,
        key_columns=dimension_keys.D_PROVIDER_URL.columns,
        output_int64=dimension_keys.D_PROVIDER_URL.output_int64,
        replace_nulls_with=dimension_keys.D_PROVIDER_URL.replace_nulls_with
    )


def add_brand_key(df):
    """
    Create brand key
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_BRAND.name,
        key_columns=dimension_keys.D_BRAND.columns,
        output_int64=dimension_keys.D_BRAND.output_int64,
        replace_nulls_with=dimension_keys.D_BRAND.replace_nulls_with
    )


def add_object_url_key(df):
    """
    Creates the object url parameter key.
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_OBJECT_URL.name,
        key_columns=dimension_keys.D_OBJECT_URL.columns,
        output_int64=dimension_keys.D_OBJECT_URL.output_int64,
        replace_nulls_with=dimension_keys.D_OBJECT_URL.replace_nulls_with
    )


def add_session_key(df):
    """
    Creates the session key.
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_SESSION.name,
        key_columns=dimension_keys.D_SESSION.columns,
        output_int64=dimension_keys.D_SESSION.output_int64,
        replace_nulls_with=dimension_keys.D_SESSION.replace_nulls_with
    )


def add_visitor_key(df):
    """
    Creates the visitor key.
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_VISITOR.name,
        key_columns=dimension_keys.D_VISITOR.columns,
        output_int64=dimension_keys.D_VISITOR.output_int64,
        replace_nulls_with=dimension_keys.D_VISITOR.replace_nulls_with
    )


def add_visit_key(df):
    """
    Creates the visit key.
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_VISIT.name,
        key_columns=dimension_keys.D_VISIT.columns,
        output_int64=dimension_keys.D_VISIT.output_int64,
        replace_nulls_with=dimension_keys.D_VISIT.replace_nulls_with
    )


def add_url_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_URL.name,
        key_columns=dimension_keys.D_URL.columns,
        output_int64=dimension_keys.D_URL.output_int64,
        replace_nulls_with=dimension_keys.D_URL.replace_nulls_with
    )


def add_recommendation_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_RECOMMENDATION.name,
        key_columns=dimension_keys.D_RECOMMENDATION.columns,
        output_int64=dimension_keys.D_RECOMMENDATION.output_int64,
        replace_nulls_with=dimension_keys.D_RECOMMENDATION.replace_nulls_with
    )


def add_consent_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_CONSENT.name,
        key_columns=dimension_keys.D_CONSENT.columns,
        output_int64=dimension_keys.D_CONSENT.output_int64,
        replace_nulls_with=dimension_keys.D_CONSENT.replace_nulls_with
    )


def add_target_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_TARGET.name,
        key_columns=dimension_keys.D_TARGET.columns,
        output_int64=dimension_keys.D_TARGET.output_int64,
        replace_nulls_with=dimension_keys.D_TARGET.replace_nulls_with
    )


def add_intent_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_INTENT.name,
        key_columns=dimension_keys.D_INTENT.columns,
        output_int64=dimension_keys.D_INTENT.output_int64,
        replace_nulls_with=dimension_keys.D_INTENT.replace_nulls_with
    )


def add_object_name_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_OBJECT_NAME.name,
        key_columns=dimension_keys.D_OBJECT_NAME.columns,
        output_int64=dimension_keys.D_OBJECT_NAME.output_int64,
        replace_nulls_with=dimension_keys.D_OBJECT_NAME.replace_nulls_with
    )


def add_identity_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_IDENTITY.name,
        key_columns=dimension_keys.D_IDENTITY.columns,
        output_int64=dimension_keys.D_IDENTITY.output_int64,
        replace_nulls_with=dimension_keys.D_IDENTITY.replace_nulls_with
    )


def add_provider_component_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_PROVIDER_COMPONENT.name,
        key_columns=dimension_keys.D_PROVIDER_COMPONENT.columns,
        output_int64=dimension_keys.D_PROVIDER_COMPONENT.output_int64,
        replace_nulls_with=dimension_keys.D_PROVIDER_COMPONENT.replace_nulls_with
    )


def add_vertical_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_VERTICAL.name,
        key_columns=dimension_keys.D_VERTICAL.columns,
        output_int64=dimension_keys.D_VERTICAL.output_int64,
        replace_nulls_with=dimension_keys.D_VERTICAL.replace_nulls_with
    )


def add_vertical_v3_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_VERTICAL_V3.name,
        key_columns=dimension_keys.D_VERTICAL_V3.columns,
        output_int64=dimension_keys.D_VERTICAL_V3.output_int64,
        replace_nulls_with=dimension_keys.D_VERTICAL_V3.replace_nulls_with
    )


def add_viewport_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_VIEWPORT.name,
        key_columns=dimension_keys.D_VIEWPORT.columns,
        output_int64=dimension_keys.D_VIEWPORT.output_int64,
        replace_nulls_with=dimension_keys.D_VIEWPORT.replace_nulls_with
    )


def add_origin_url_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_ORIGIN_URL.name,
        key_columns=dimension_keys.D_ORIGIN_URL.columns,
        output_int64=dimension_keys.D_ORIGIN_URL.output_int64,
        replace_nulls_with=dimension_keys.D_ORIGIN_URL.replace_nulls_with
    )


def add_spt_custom_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_SPT_CUSTOM.name,
        key_columns=dimension_keys.D_SPT_CUSTOM.columns,
        output_int64=dimension_keys.D_SPT_CUSTOM.output_int64,
        replace_nulls_with=dimension_keys.D_SPT_CUSTOM.replace_nulls_with
    )

def add_consent_filter_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_CONSENT_FILTER.name,
        key_columns=dimension_keys.D_CONSENT_FILTER.columns,
        output_int64=dimension_keys.D_CONSENT_FILTER.output_int64,
        replace_nulls_with=dimension_keys.D_CONSENT_FILTER.replace_nulls_with
    )

def add_search_phrase_key(df):
    return add_key_column(
        df,
        key_name=dimension_keys.D_SEARCH_PHRASE.name,
        key_columns=dimension_keys.D_SEARCH_PHRASE.columns,
        output_int64=dimension_keys.D_SEARCH_PHRASE.output_int64,
        replace_nulls_with=dimension_keys.D_SEARCH_PHRASE.replace_nulls_with
    )

def add_target_url_key(df):
    """
    Creates the object url parameter key.
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_TARGET_URL.name,
        key_columns=dimension_keys.D_TARGET_URL.columns,
        output_int64=dimension_keys.D_TARGET_URL.output_int64,
        replace_nulls_with=dimension_keys.D_TARGET_URL.replace_nulls_with
    )

def add_experiments_key(df):
    """
    Creates the object url parameter key.
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_EXPERIMENTS.name,
        key_columns=dimension_keys.D_EXPERIMENTS.columns,
        output_int64=dimension_keys.D_EXPERIMENTS.output_int64,
        replace_nulls_with=dimension_keys.D_EXPERIMENTS.replace_nulls_with
    )


def build_path_list(
        partition_date,
        base_uri=BASE_BEHAVIOURAL_URI,
        providers_to_include=None,
        session=None,
        partition_hour=None,
) -> list:
    if providers_to_include is None:
        providers_to_include = get_included_provider_ids()

    s = get_default_session(session)

    read_date = to_datetime(partition_date)
    base_uri = join_path(
        base_uri,
        f"year={read_date.year}",
        f"month={read_date.month}",
        f"day={read_date.day}",
    )

    # generate a list of all existing s3 prefixes for the hour(s) provided
    s3_prefixes = []
    if partition_hour:
        s3_prefixes.append(
            get_latest_path(join_path(base_uri, f"hour={int(partition_hour)}"), s)
        )
    else:
        for hour in range(24):
            try:
                path = get_latest_path(join_path(base_uri, f"hour={int(hour)}"), s)
            except ValueError:
                pass
            else:
                s3_prefixes.append(path)

    # Combine each s3 hour prefix with each provider to include
    prefixes_product = list(itertools.product(s3_prefixes, providers_to_include))

    # convert the result of the product operation into prefixes
    unfiltered_prefix_list = [f"{prefix}client={client}/" for prefix, client in prefixes_product]

    # find the common bucket and common prefix across all generated prefixes
    common_bucket, common_prefix = split_uri(get_common_prefix(s3_prefixes))

    # list all objects under the common bucket and prefix
    bucket_objects = list_objects(common_bucket, common_prefix)

    # generate the full uri for each object in the bucket
    object_uris = [f"s3://{ob.bucket_name}/{ob.key}" for ob in bucket_objects]

    # cross-check the prefixes with the actual object uris to only keep the valid ones
    filtered_prefix_list = list(
        {prefix for object_uri in object_uris for prefix in unfiltered_prefix_list if object_uri.startswith(prefix)}
    )

    return filtered_prefix_list
