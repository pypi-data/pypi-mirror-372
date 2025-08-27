from dataclasses import dataclass


@dataclass
class DimensionKey:
    name: str
    columns: list
    output_int64: bool
    replace_nulls_with: str


D_BRAND_KEY_NAME = "brand_key"

D_PROVIDER = DimensionKey(
    name="provider_key",
    columns=[
        "p_client",
        "provider_product_type",
        "provider_product",
        "tracker_type",
        "provider_product_tag",
        "provider_platform_name"
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_URL = DimensionKey(
    name="url_key",
    columns=[
        "url",
    ],
    output_int64=False,
    replace_nulls_with=""
)

D_PROVIDER_URL = DimensionKey(
    name="provider_url_key",
    columns=[
        "provider_url",
    ],
    output_int64=D_URL.output_int64,
    replace_nulls_with=D_URL.replace_nulls_with
)

D_CATEGORY = DimensionKey(
    name="category_key",
    columns=[
        "object_category",
        "p_client",
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_DEVICE = DimensionKey(
    name="device_key",
    columns=[
        "pulse_device_type",
        "device_user_agent",
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_OBJECT_URL = DimensionKey(
    name="object_url_key",
    columns=[
        "object_url",
    ],
    output_int64=D_URL.output_int64,
    replace_nulls_with=D_URL.replace_nulls_with
)

D_SESSION = DimensionKey(
    name="session_key",
    columns=[
        "session_id",
        "session_start_time",
    ],
    output_int64=False,
    replace_nulls_with=""
)

D_VISITOR = DimensionKey(
    name="visitor_key",
    columns=[
        "provider_id",
        "environment_key",
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_VISIT = DimensionKey(
    name="visit_key",
    columns=[
        "session_id",
        "provider_id",
        "environment_key",
        "session_start_time",
    ],
    output_int64=False,
    replace_nulls_with=""
)

D_CONTENT_OBJECT = DimensionKey(
    name="content_object_key",
    columns=[
        "p_client",
        "numeric_object_id",
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_RECOMMENDATION = DimensionKey(
    name="recommendation_key",
    columns=[
        "recommendation_id",
        "recommendation_id_key",
        "recommendation_source",
        "recommendation_type",
        "recommendation_list_name"
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_CONSENT = DimensionKey(
    name="consent_key",
    columns=[
        "consent_source",
        "advertising_opt_in",
        "analytics_opt_in",
        "marketing_opt_in",
        "personalization_opt_in"
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_TARGET = DimensionKey(
    name="target_key",
    columns=[
        "target_id_key",
        "target_in_reply_to_id_key",
        "target_related_to_id_key",
        "target_fields",
        "paid_promotion_types",
        "paid_promotions",
        "target_id_key",
        "target_type",
        "target_name"
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_INTENT = DimensionKey(
    name="intent_key",
    columns=[
        "intent",
        "name"
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_OBJECT_NAME = DimensionKey(
    name="object_name_key",
    columns=[
        "object_name",
        "object_type"
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_IDENTITY = DimensionKey(
    name="identity_key",
    columns=[
        "user_id",
        "environment_key",
        "visitor_key",
        "session_key",
        "visit_key",
        "brand_key"
    ],
    output_int64=False,
    replace_nulls_with=""
)

D_PROVIDER_COMPONENT = DimensionKey(
    name="provider_component_key",
    columns=[
        "provider_component"
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_VERTICAL = DimensionKey(
    name="vertical_key",
    columns=[
        "vertical_name",
        "vertical_sub_vertical"
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_VERTICAL_V3 = DimensionKey(
    name="vertical_key",
    columns=[
        "vertical_name",
        "vertical_type",
        "vertical_sub_vertical"
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_VIEWPORT = DimensionKey(
    name="viewport_key",
    columns=[
        "screen_height",
        "screen_width",
        "viewport_height",
        "viewport_width"
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_ORIGIN_URL = DimensionKey(
    name="origin_url_key",
    columns=[
        "origin_url",
    ],
    output_int64=False,
    replace_nulls_with=""
)

D_SPT_CUSTOM = DimensionKey(
    name="spt_custom_key",
    columns=[
        "article_id",
        "article_viewed_percentage",
        "device",
        "permalink",
        "lix",
        "referrer",
        "site",
        "url",
        "word_count",
        "is_navigation",
        "finance_company",
        "insurance_company",
        "current_iteration",
        "model_text",
        "recommendation_ads_count",
        "search_ads_count",
        "show_more_click_number",
        "total_iterations",
        "contact_type",
        "is_voice_control",
    ],
    output_int64=False,
    replace_nulls_with=""
)

D_CONSENT_FILTER = DimensionKey(
    name="consent_filter_key",
    columns=[
        "consents_to_analytics",
        "consents_to_marketing",
        "consents_to_advertising",
        "consents_to_personalization",
        "consents_to_all_purposes",
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_SEARCH_PHRASE = DimensionKey(
    name="search_phrase_key",
    columns=[
        "search_phrase",
        "brand_key",
    ],
    output_int64=True,
    replace_nulls_with=""
)

D_TARGET_URL = DimensionKey(
    name="target_url_key",
    columns=[
        "target_url",
    ],
    output_int64=False,
    replace_nulls_with=""
)

D_EXPERIMENTS = DimensionKey(
    name="target_url_key",
    columns=[
        "brand_key",
        "experiment_id",
        "experiment_name",
        "experiment_platform",
        "experiment_variant",
        "experiment_atid",
        
    ],
    output_int64=False,
    replace_nulls_with=""
)
