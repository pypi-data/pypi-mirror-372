import gspread

from .aws.secrets_manager import get_secret


class GoogleSpreadsheet:
    def __init__(
            self,
            url: str,
            service_account: str = None

    ):
        self.url = url
        self.service_account = service_account

    @property
    def service_account_dict(self) -> dict: 
        if self.service_account is None:
            service_account_dict = get_secret("gcp_service_account/cdw_bot")
        else:
            service_account_dict = self.service_account

        return service_account_dict

    @property
    def client(self) -> gspread.client.Client:
        return gspread.service_account_from_dict(self.service_account_dict)

    @property
    def spreadsheet(self) -> gspread.spreadsheet.Spreadsheet:
        return self.client.open_by_url(self.url)


class GoogleSpreadsheetSheet:
    def __init__(
            self,
            spreadsheet: GoogleSpreadsheet,
            name: str,
            data_range_start: str,  # start of non-header range
            data_range_end: str  # end of non-header range
    ):
        self.spreadsheet = spreadsheet
        self.name = name
        self.data_range_start = data_range_start
        self.data_range_end = data_range_end
        self.data_range = f"{data_range_start}:{data_range_end}"

    @property
    def sheet(self) -> gspread.worksheet.Worksheet:
        return self.spreadsheet.spreadsheet.worksheet(self.name)

    def read_data_range(self) -> list:
        return self.sheet.get_values(self.data_range)

    def clear_data_range(self):
        self.spreadsheet.spreadsheet.values_clear(f"'{self.name}'!{self.data_range}")
