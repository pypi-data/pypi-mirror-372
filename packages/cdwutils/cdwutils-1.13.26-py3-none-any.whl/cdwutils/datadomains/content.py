from .brand_providers import get_included_provider_ids
from ..aws.s3 import get_partition_value_from_path, list_objects, split_uri
from ..misc import to_datetime
from ..etl import add_key_column
from . import dimension_keys

BASE_CONTENT_URI = "s3://schibsted-analytics-cdw-data-import/pulse/content/red/version=4/"


def build_path_list(
    partition_date,
    base_uri=BASE_CONTENT_URI,
    providers_to_include=None,
):
    if providers_to_include is None:
        providers_to_include = get_included_provider_ids()

    base_uri = base_uri[:-1] if base_uri.endswith("/") else base_uri

    read_date = to_datetime(partition_date)
    year = read_date.year
    month = read_date.month
    day = read_date.day
    
    source_bucket, source_key = split_uri(base_uri)
    
    prefix = f"{source_key}/year={year}/month={month}/day={day}/"
    
    objects_list = list_objects(bucket_name=source_bucket, prefix=prefix)
    
    path_list = [f"s3://{path.bucket_name}/{path.key}" for path in objects_list if path.key.find(".txt") > 0]
    
    return [path for path in path_list if get_partition_value_from_path("client", path) in providers_to_include]


def add_content_object_key(df):
    """
    Create content_object key column
    """
    return add_key_column(
        df,
        key_name=dimension_keys.D_CONTENT_OBJECT.name,
        key_columns=dimension_keys.D_CONTENT_OBJECT.columns,
        output_int64=dimension_keys.D_CONTENT_OBJECT.output_int64,
        replace_nulls_with=dimension_keys.D_CONTENT_OBJECT.replace_nulls_with
    )
