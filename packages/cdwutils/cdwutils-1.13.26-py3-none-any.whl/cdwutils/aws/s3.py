from io import BytesIO
from typing import List, Optional
import re

from boto3.session import Session

from .common import get_client, get_resource


def split_uri(s3_uri):
    """
    Return a tuple of (bucket, key) by splitting an s3 uri.
    """
    if s3_uri.lower().startswith("s3://"):
        bucket = s3_uri[5:].split("/")[0]
        key = s3_uri[6 + len(bucket):]
        return bucket, key
    else:
        raise ValueError(f"Invalid s3_uri: '{s3_uri}'. Expected 's3://bucket/prefix/key'.")


def download_file(s3_uri, session=None):
    """
    Return bytes of the s3 file.
    """
    s3 = get_client("s3", session)
    bucket, key = split_uri(s3_uri)

    with BytesIO() as buffer:
        s3.download_fileobj(
            Bucket=bucket,
            Key=key,
            Fileobj=buffer
        )
        buffer.flush()
        buffer.seek(0)
        return buffer.read()


def read_text_file(s3_uri, session=None):
    """
    Return str of the s3 file.
    """
    data = download_file(s3_uri, session)
    return data.decode("utf-8")


def delete_objects(s3_prefix_uri, session=None):
    """
    Delete all S3 objects with `s3_prefix_uri` prefix.
    """
    s3 = get_resource("s3", session)
    bucket_name, prefix = split_uri(s3_prefix_uri)
    prefix = prefix.rstrip("/") + "/"
    r = s3.Bucket(bucket_name).objects.filter(Prefix=prefix).delete()
    if r:
        print(f"DELETED {len(list(r[0]['Deleted']))} objects with prefix {s3_prefix_uri}")


def list_objects(bucket_name, prefix=None, session=None):
    """
    Return a list of all S3 objects with `s3_prefix_uri` prefix.
    """
    s3 = get_resource("s3", session)
    bucket = s3.Bucket(bucket_name)
    if prefix is None:
        objects = bucket.objects.all()
    else:
        objects = bucket.objects.filter(Prefix=prefix)
    return list(objects)


def list_common_prefixes(bucket, prefix, session=None):
    """
    Return a list of common prefixes or an empty list if there are none.
    If S3 prefix where a file system folder, then a common prefix would
    be a subfolder inside it.
    """
    s3_client = get_client("s3", session=session)
    paginator = s3_client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(
        Bucket=bucket,
        Prefix=prefix,
        Delimiter="/",
        MaxKeys=1000
    )
    common_prefixes = []
    for page in page_iterator:
        common_prefixes.extend(
            [p["Prefix"] for p in page.get("CommonPrefixes", [])]
         )
    return common_prefixes


def list_all_common_prefixes(bucket, prefix, session=None):
    exhausted_prefixes = []
    prefixes = [prefix,]
    while len(prefixes) > 0:
        current_prefix = prefixes.pop()
        common_prefixes = list_common_prefixes(bucket, current_prefix, session=session)
        if common_prefixes:
            prefixes.extend(common_prefixes)
        else:
            exhausted_prefixes.append(current_prefix)
    return exhausted_prefixes


def latest_prefix(prefixes):
    """
    Assumes each prefix uses hive partitioning and the last partitioning fields is numeric.
    E.g., 'red/pulse/version=5/year=2021/month=2/day=1/hour=18/gen=123/'
    """
    return max(
      prefixes,
      key=lambda p: int(p.rstrip("/").split("/")[-1].split("=")[-1])
    )


def get_latest_path(s3_uri, session):
    """
    Recursively scan a hive partitioning like prefix structure and return the
    path to the latest partition, assuming the data is partitioned by numeric fields.
    """
    bucket, prefix = split_uri(s3_uri)
    r = get_client("s3", session=session).list_objects_v2(
        Bucket=bucket,
        Prefix=prefix,
        Delimiter="/",
        MaxKeys=1000
    )
    prefixes = [d["Prefix"] for d in r.get("CommonPrefixes", [])]
    if len(prefixes) > 0:
        if sum((p == prefix + "/" for p in prefixes)) > 0:
            return get_latest_path(s3_uri + "/", session)
        else:
            return "/".join(["s3:/", bucket, latest_prefix(prefixes)])
    elif len(prefixes) == 0 and r["KeyCount"] > 0:
        return s3_uri
    else:
        raise ValueError(f"Invalid path: {s3_uri}")


def join_path(*path_part):
    segments = []
    for i, p in enumerate(path_part):
        if i == 0:
            segments.append(p.rstrip("/ "))
        elif i < len(path_part) - 1:
            segments.append(p.strip("/ "))
        else:
            segments.append(p.lstrip("/ "))
    return "/".join(segments)


def get_partition_value_from_path(partition_field_name: str, path: str) -> Optional[str]:
    """
    Return the value of a partitioning column `partition_field_name` in a path that follows the Hive
    partitioning scheme (path/col1=value/col2=value/). If `partition_field_name` is not found return None.

    Example:
    >>> get_partition_value_from_path("p_client", "s3://bucket/behavioural/proc/p_client=finn")
    'finn'
    >>> get_partition_value_from_path("p_client", "s3://bucket/behavioural/proc/p_client=finn/")
    'finn'
    >>> get_partition_value_from_path("p_client", "s3://bucket/behavioural/proc/")
    None
    """
    match = re.search(f"/{partition_field_name}=([^/]*)", path)
    if match:
        return match.group(1)
    else:
        return None


def get_partition_values_from_paths(partition_field_name: str, paths: List[str]) -> List[str]:
    """
    Return a list of values of a partitioning column `field_name` extracted from the `paths`.
    Each path is expected to follow the Hive partitioning scheme (path/col1=value/col2=value/).

    Example:
    >>> get_partition_values_from_paths("p_client", ["s3://bucket/prefix/p_client=finn", "s3://bucket/prefix/p_client=vg"])
    ['finn', 'vg']
    >>> get_partition_values_from_paths("p_client", ["s3://bucket/prefix/",])
    []
    """
    values = {get_partition_value_from_path(partition_field_name, p) for p in paths}
    values.discard(None)
    return list(values)


def get_partition_values(
    partition_column: str,
    bucket_name: str,
    prefix: Optional[str] = None,
    session: Optional[Session] = None,
) -> List[str]:
    """
    :param partition_column: Name of column to extract values for
    :param bucket_name: Name of bucket to get the object paths from
    :param prefix: Optional prefix to specify where to scan in the bucket
    :param session: Optional session to use for scanning the bucket
    :return: Distinct list of column values found in path_list
    """

    bucket_objects = list_objects(
        bucket_name=bucket_name,
        prefix=prefix,
        session=session,
    )

    return get_partition_values_from_paths(
        partition_field_name=partition_column,
        paths=[item.key for item in bucket_objects]
    )


def prefix_exists(bucket_name: str, prefix: str, session: Optional[Session] = None) -> bool:
    """
    Check if an S3 prefix exists.
    """
    s3 = get_resource("s3", session=session)
    bucket = s3.Bucket(bucket_name)
    objects = bucket.objects.filter(Prefix=prefix, MaxKeys=1)
    return len(list(objects.limit(1))) == 1


def truncate_uri_by_delim_count(uri: str, delim_count: int, delim: str = "/") -> str:
    """

    :param uri: uri to truncate
    :param delim_count: number of delimiters to truncate from the right
    :param delim: delimiter used in the path
    """
    if uri.lower().startswith("s3://"):
        return uri.rsplit(delim, delim_count)[0]
    else:
        raise ValueError(f"Invalid uri: '{uri}'. Expected 's3://bucket/prefix/key'.")


def make_uris_directory_level_equal(uris: List[str]) -> List[str]:
    """
    Takes a list of s3 uris and truncates them to make the directory level equal
    :param uris: List of paths to scan
    :return: List of equal level paths

    Example:
    >>> make_uris_directory_level_equal(["s3://bucket1/directory1/file1", "s3://bucket2/directory2/"]
    ['s3://bucket1/directory1/', 's3://bucket2/directory2/']
    """
    trimmed_uris = [uri.rstrip("/") for uri in uris]

    uris_list = [[uri, uri.count("/")] for uri in trimmed_uris]

    lowest_level = min(list(zip(*uris_list))[1])

    return [truncate_uri_by_delim_count(uri, length - lowest_level) + "/" for uri, length in uris_list]


def get_common_prefix(prefixes: List[str]) -> str:
    """
    Returns the 'common denominator' of the paths.
    The function will throw an error if there is no common path found
    """
    trimmed_prefixes = set(make_uris_directory_level_equal(prefixes))

    while len(trimmed_prefixes) > 1:
        previous_val = trimmed_prefixes
        trimmed_prefixes = set(truncate_uri_by_delim_count(path, 1) for path in trimmed_prefixes)
        if trimmed_prefixes == previous_val:
            raise RuntimeError(f"No common path found. Current values are {trimmed_prefixes}")

    return trimmed_prefixes.pop()
