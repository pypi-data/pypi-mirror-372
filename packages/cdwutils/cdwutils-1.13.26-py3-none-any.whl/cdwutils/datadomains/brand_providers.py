import json

from ..aws.s3 import read_text_file
from ..gsheets import GoogleSpreadsheet, GoogleSpreadsheetSheet


def get_included_provider_ids(
    brand_master_s3_uri="s3://schibsted-analytics-cdw-cicd-prod/travis-builds/cdw-core/master/data/brand_master.json"
):
    brand_master_data = json.loads(read_text_file(brand_master_s3_uri))
    return [r["provider_client_id"] for r in brand_master_data]


def get_brand_master(
    brand_master_s3_uri="s3://schibsted-analytics-cdw-cicd-prod/travis-builds/cdw-core/master/data/brand_master.json"
):
    brand_master_data = json.loads(read_text_file(brand_master_s3_uri))
    return brand_master_data


def get_excluded_provider_ids(
    exclusion_list_s3_uri="s3://schibsted-analytics-cdw-cicd-prod/travis-builds/cdw-core/master/data/provider_exclusion_list.json"
):
    return json.loads(read_text_file(exclusion_list_s3_uri))


BRAND_MASTER_SPREADSHEET = GoogleSpreadsheet(
    "https://docs.google.com/spreadsheets/d/1GAGWKg8dFSIpF6SZGf-WZFHoquXCHa0MkaEsv2ojapA"
)

UNKNOWN_PROVIDERS_SHEET = GoogleSpreadsheetSheet(
    spreadsheet=BRAND_MASTER_SPREADSHEET,
    name="Unknown list",
    data_range_start="A2",
    data_range_end="A"
)

BRAND_PROVIDERS_SHEET = GoogleSpreadsheetSheet(
    spreadsheet=BRAND_MASTER_SPREADSHEET,
    name="data",
    data_range_start="A2",
    data_range_end="T"
)
