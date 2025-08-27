from typing import Callable, List, Union

import pyspark.sql
from pyspark.sql import functions as F
from pyspark.sql.column import Column

from .brand_providers import get_brand_master

from ..etl import add_key_column

from ..spark_extensions import (
    SensitiveValue,
    empty_str_to_null,
    get_col,
    mask_id_string,
    pseudonymize,
    xxhash,
)

ALLOWED_PATTERNS_LIST = [
    "sdrn:[^:]+:Listing:search_result:(.*?)",
    "sdrn:[^:]+:listing:search_result:(.*?)",
    "sdrn:[^:]+:Frontpage:(.*?)",
    "sdrn:[^:]+:frontpage:(.*?)",
    "sdrn:[^:]+:element:(?!(http(s)?)|(classifiedad)|(\d+))",
    "sdrn:[^:]+:listing:",
    "sdrn:[^:]+:content:(?!\d+)",
    "sdrn:[^:]+:uielement:",
    "sdrn:[^:]+:UIElement:",
    "sdrn:[^:]+:error:(?!\d+)",
    "sdrn:[^:]+:application:",
    "sdrn:[^:]+:confirmation:(?!\d+)",
    "sdrn:[^:]+:promotion:",
    "sdrn:[^:]+:button:",
    "sdrn:[^:]+:favoriteitem:",
    "sdrn:[^:]+:displayad:",
    "sdrn:[^:]+:externalcontent:",
    "sdrn:[^:]+:RecommendationList:",
    "sdrn:[^:]+:userprofilepage:",
    "sdrn:[^:]+:Form:",
    "sdrn:[^:]+:Page:",
    "sdrn:[^:]+:article:",
    "sdrn:[^:]+:Article:article:",
    "sdrn:[^:]+:SavedList:",
    "sdrn:[^:]+:NotificationContent:",
    "sdrn:[^:]+:Listing:",
    "sdrn:[^:]+:psi:",
    "sdrn:[^:]+:phonecontact:(?!\d+)",
    "sdrn:[^:]+:UserProfilePage:",
    "sdrn:[^:]+:ExternalContent:",
    "sdrn:[^:]+:Error:",
    "sdrn:[^:]+:Confirmation:",
    "sdrn:[^:]+:[^\d:]+$",
    ":element:PartnerBanner",
    "sdrn:[^:]+:premiumfeature:",
    "^external-link[^\d:]+$",
    "sdrn:[^:]+:Engagement:",
    "sdrn:[^:]+:listing:store",
    "sdrn:[^:]+:product:",
    "sdrn:[^:]+:conversation:",
    "sdrn:[^:]+:savedlist:favoritelist:\d+:element:favoritelist:\d+$",
    "sdrn:[^:]+:savedlist:favoritelist:\d+$",
    "sdrn:[^:]+:savedlist:savedlist:",
    "sdrn:[^:]+:searchitem:",
    "sdrn:[^:]+:form:(?!\d+)",
    "sdrn:[^:]+:message:(?!\d+)",
    "sdrn:[^:]+:notification:(?!\d+)",
    "^[A-Za-z0-9]{40}$",
]

ALLOWED_PATTERNS_STR = "|".join([f"({pattern})" for pattern in ALLOWED_PATTERNS_LIST])

SENSITIVE_OBJECT_ID_PATTERNS_LIST = [
    "http(s)?",
    "^\d+$",
    "sdrn:[^:]+:classified:",
    "sdrn:[^:]+:marketplaceitem:",
    "sdrn:[^:]+:ClassifiedAd:classified:",
    "sdrn:[^:]+:ClassifiedAd:",
    "sdrn:[^:]+:classifiedad:(.*?)",
    "sdrn:[^:]+:page:",
    "sdrn:[^:]+:recommendationlist:",
    "sdrn:[^:]+:element:http(s)?",
    "sdrn:[^:]+:element:classifiedad:",
    "sdrn:[^:]+:element:\d+",
    "sdrn:[^:]+:content:\d+",
    "sdrn:[^:]+:error:\d+",
    "sdrn:[^:]+:recommendationitem:",
    "sdrn:[^:]+:confirmation:\d+",
    "sdrn:[^:]+:listingitem:",
    "sdrn:[^:]+:RecommendationItem:",
    "sdrn:[^:]+:ListingItem:",
    "sdrn:[^:]+:phonecontact:\d+",
    "sdrn:[^:]+:notification:\d+",
    "sdrn:[^:]+:\d+:",
    "sdrn:[^:]+:processflow:",
    "sdrn:[^:]+:ProcessFlow:",
    "sdrn:[^:]+:emailcontact:",
    "sdrn:[^:]+:redirecturl:\d+",
    "sdrn:[^:]+:notificationcontent:",
    "sdrn:[^:]+:rating:",
    "sdrn:[^:]+:job:",
    "sdrn:[^:]+:savedlist:favoritelist:\d+:element:classified:\d+$",
    "sdrn:[^:]+:form:\d+",
    "sdrn:[^:]+:message:\d+",
]

SENSITIVE_PATTERNS_STR = "|".join([f"({pattern})" for pattern in SENSITIVE_OBJECT_ID_PATTERNS_LIST])


def get_marketplace_providers() -> List:
    brand_master = get_brand_master()

    return [
        r["provider_client_id"] for r in brand_master
        if r["business_area"] == "Marketplaces"
    ]


def get_non_marketplace_providers() -> List:
    brand_master = get_brand_master()

    return [
        r["provider_client_id"] for r in brand_master
        if r["business_area"] != "Marketplaces"
    ]


def extract_sdrn_id_meta(col: Union[str, Column]) -> Column:
    """
    Return a struct with metadata for an sdrn identifier:
        * length - total char length of the input field
        * provider - 2nd element in the sdrn
        * pattern - input sdrn with masked ids
    """
    sdrn_id = get_col(col)
    sdrn_id_array = F.split(sdrn_id, ":")

    pattern = F.array_join(F.transform(sdrn_id_array, mask_id_string), ":")

    return F.when(
        sdrn_id.isNotNull(),
        F.struct(
            F.length(sdrn_id).alias("length"),
            sdrn_id_array.getItem(1).alias("provider"),
            pattern.alias("pattern")
        )
    ).otherwise(None)


def proc_id_column(col: Union[str, Column], hashing_key: Union[str, SensitiveValue]) -> Column:
    """
    Pseudonymize the sdrn id column and extract the id metadata.
    """
    c = get_col(col)
    numeric_part_of_id = empty_str_to_null(F.regexp_extract(c, r"\d{2,}", 0))

    return F.when(c.isNull(), None).otherwise(
        F.struct(
            xxhash(pseudonymize(c, key=hashing_key)).alias("id"),
            xxhash(pseudonymize(numeric_part_of_id, key=hashing_key)).alias("numeric_part_of_id"),
            extract_sdrn_id_meta(c).alias("id_meta")
        )
    )


def extract_content_id(object_id_col: Union[str, Column]) -> Column:
    object_id_col = get_col(object_id_col)
    content_id = empty_str_to_null(F.regexp_extract(object_id_col, r"\d{5,}", 0))

    return empty_str_to_null(content_id)


def create_provider_content_id(
        provider_id_col: Union[str, Column],
        content_id_col: Union[str, Column],
        platform_col: Union[str, Column] = None,
        replace_nulls_with_str: str = "",
) -> Column:
    provider_id_col = get_col(provider_id_col)
    content_id_col = get_col(content_id_col)

    if platform_col is None:
        platform_col = F.lit(None)
    else:
        platform_col = get_col(platform_col)

    return F.when(
        provider_id_col.isNull() | content_id_col.isNull(),
        None
    ).when(
        platform_col.isNotNull(),
        F.concat_ws(
            "|",
            F.coalesce(provider_id_col, F.lit(replace_nulls_with_str)),
            F.coalesce(content_id_col, F.lit(replace_nulls_with_str)),
            F.coalesce(platform_col, F.lit(replace_nulls_with_str)),
        )
    ).otherwise(
        F.concat_ws(
            "|",
            F.coalesce(provider_id_col, F.lit(replace_nulls_with_str)),
            F.coalesce(content_id_col, F.lit(replace_nulls_with_str)),
        )
    )


def create_content_object_key(
    object_id: Union[str, Column],
    pseudonymization_key: Union[str, SensitiveValue, None] = None,
    platform: Union[str, Column] = None
) -> Column:

    object_id = get_col(object_id)

    # Denmark sometimes sends internal ID in uuid format,
    # so this function may extract 5+ digits by mistake.
    # This check ensures that it doesn't happen.
    uuid_pattern = "sdrn:[^:]+:[^:]+:[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"

    extracted_content_id = pseudonymize(
        extract_content_id(object_id),
        key=pseudonymization_key
    )

    marketplace_providers = get_marketplace_providers()

    object_provider = F.split(object_id, ":").getItem(1)

    return F.when(
        object_id.rlike(uuid_pattern),
        None
    ).when(
        (object_provider.isin(marketplace_providers)) &
        (object_id.rlike(SENSITIVE_PATTERNS_STR)),
        create_provider_content_id(
            object_provider,
            extracted_content_id,
            platform
        )
    ).otherwise(
        None
    )


def add_content_object_key(
    object_id: Union[str, Column],
    pseudonymization_key: Union[str, SensitiveValue, None] = None,
    col_name: str = "content_object_key",
    platform_col: Union[str, Column] = None
) -> Callable:

    def inner(df):

        temp_col_name = "provider_content_id_temp"

        content_object_key = create_content_object_key(
            object_id=object_id,
            pseudonymization_key=pseudonymization_key,
            platform=platform_col
        )

        df = df.withColumn(
            temp_col_name,
            content_object_key
        )

        return add_key_column(
            df,
            col_name,
            [temp_col_name],
            output_int64=True
        ).drop(
          temp_col_name
        )

    return inner
