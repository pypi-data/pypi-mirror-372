"""
Quickstart: https://developers.google.com/sheets/api/quickstart/python
Python client: https://github.com/googleapis/google-api-python-client
Using service account: https://github.com/googleapis/google-api-python-client/blob/main/docs/oauth-server.md

1. Create Google cloud project
2. Enable necessary API, IAM

"""

import json
import mimetypes
import pathlib

import google.cloud.iam_admin_v1
import google.oauth2.credentials
import google.oauth2.service_account
import google_auth_oauthlib
import googleapiclient.discovery
import googleapiclient.http
import polars as pl


def create_service_account_info(project: str, service_account: str) -> dict:
    """A service account can be built in the Google cloud console."""
    iam_admin_client = google.cloud.iam_admin_v1.IAMClient()
    request = google.cloud.iam_admin_v1.types.CreateServiceAccountKeyRequest()
    request.name = f"projects/{project}/serviceAccounts/{service_account}"
    key = iam_admin_client.create_service_account_key(request=request)
    info = json.loads(key.private_key_data)
    return info


def create_authorized_user_info(user_credentials: dict, scopes: list[str]) -> dict:
    """Authorized user credentials can be downloaded from the Google cloud console."""
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(user_credentials, scopes)
    credentials = flow.run_local_server(port=0)
    info = json.loads(credentials.to_json())
    return info


def get_credentials(
    *,
    service_account_info: dict | None = None,
    authorized_user_info: dict | None = None,
    scopes: list[str],
) -> google.auth.credentials.Credentials:
    if bool(service_account_info) == bool(authorized_user_info):
        raise ValueError(
            "Exactly one of service_account_info and authorized_user_info must be provided."
        )

    if service_account_info:
        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            service_account_info
        )
        credentials = credentials.with_scopes(scopes)
    else:
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
            authorized_user_info, scopes
        )

    if credentials.expired:
        credentials.refresh(google.auth.transport.requests.Request())

    return credentials


def build_spreadsheets_api(credentials: google.auth.credentials.Credentials, version: str = "v4"):
    resource = googleapiclient.discovery.build("sheets", version, credentials=credentials)
    spreadsheets_api = resource.spreadsheets()
    return spreadsheets_api


class Drive:
    def __init__(self, credentials: google.auth.credentials.Credentials, version: str = "v3"):
        self.api = googleapiclient.discovery.build("drive", version, credentials=credentials)

    def upload(
        self,
        filepath: str,
        name: str | None = None,
        mime_type: str | None = None,
        make_public: bool = False,
        parents: list[str] | None = None,
    ) -> str:
        """Upload a file to Drive and return a shareable URL.

        - name: optional override for the file name shown in Drive.
        - mime_type: if not provided, it will be guessed from the file extension.
        - make_public: if True, sets the file permission to anyone-with-link reader.
        - parents: list of folder IDs to upload into.
        """

        path = pathlib.Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        guessed_mime = mime_type or (
            mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        )
        media = googleapiclient.http.MediaFileUpload(
            str(path), mimetype=guessed_mime, resumable=False
        )

        body: dict = {"name": name or path.name}
        if parents:
            body["parents"] = parents

        created = (
            self.api.files()
            .create(body=body, media_body=media, fields="id,webViewLink,webContentLink")
            .execute()
        )

        file_id = created.get("id")
        if not file_id:
            raise RuntimeError("Drive API did not return a file id")

        if make_public:
            # Best-effort: allow anyone with the link to view
            self.api.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader"},
            ).execute()

        # Prefer webViewLink; fallback to deterministic viewer URL
        url = created.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"
        return url


class Spreadsheets:
    @classmethod
    def create(cls, name: str, credentials: google.auth.credentials.Credentials):
        api = build_spreadsheets_api(credentials)
        spreadsheet = api.create(body={"properties": {"title": name}}).execute()
        spreadsheet = cls(spreadsheet["spreadsheetId"], credentials)
        return spreadsheet

    def __init__(self, spreadsheet_id: str, credentials: google.auth.credentials.Credentials):
        self.id = spreadsheet_id
        self.api = build_spreadsheets_api(credentials)

    def build_range(self, sheet_name: str, start: str = "A1", end: str = "ZZZ") -> str:
        return f"'{sheet_name}'!{start}:{end}"

    def read_sheet(self, sheet_name: str, with_header: bool = True) -> pl.DataFrame | None:
        sheet = (
            self.api.values()
            .get(spreadsheetId=self.id, range=self.build_range(sheet_name))
            .execute()
        )
        if "values" not in sheet:
            return

        n_columns = max(len(row) for row in sheet["values"])
        if with_header:
            columns, *data = sheet["values"]
        else:
            columns = None
            data = sheet["values"]

        data = [(row + [None] * n_columns)[:n_columns] for row in data]
        df = pl.DataFrame(data, columns, orient="row", infer_schema_length=None)
        return df

    def exists(self, sheet_name: str) -> bool:
        try:
            self.read_sheet(sheet_name)
            return True
        except googleapiclient.errors.HttpError:
            return False

    def clear_sheet(self, sheet_name: str):
        self.api.values().clear(
            spreadsheetId=self.id,
            range=self.build_range(sheet_name),
        ).execute()

    def write_sheet(self, sheet_name: str, df: pl.DataFrame):
        if self.exists(sheet_name):
            self.clear_sheet(sheet_name)
        else:
            self.create_sheet(sheet_name)

        df = df.fill_nan("#N/A")
        values = [df.columns] + list(df.iter_rows())
        self.api.values().update(
            spreadsheetId=self.id,
            range=self.build_range(sheet_name),
            valueInputOption="USER_ENTERED",
            body={"values": values},
        ).execute()

    def describe(self) -> pl.DataFrame:
        response = self.api.get(spreadsheetId=self.id).execute()
        df = pl.DataFrame(response["sheets"], strict=False)
        df = df.unnest("properties").unnest("gridProperties")
        return df

    @property
    def title_to_id(self) -> dict:
        return dict(self.describe()[["title", "sheetId"]].iter_rows())

    def to_sheet_id(self, sheet: int | str) -> int:
        return sheet if isinstance(sheet, int) else self.title_to_id[sheet]

    def _batch_update(self, *requests: dict) -> dict:
        response = self.api.batchUpdate(
            spreadsheetId=self.id, body={"requests": requests}
        ).execute()
        return response

    def create_sheet(self, name: str) -> str:
        request = {"addSheet": {"properties": {"title": name}}}
        sheet = self._batch_update(request)
        sheet_id = sheet["replies"][0]["addSheet"]["properties"]["sheetId"]
        return sheet_id

    def delete_sheet(self, sheet: int | str):
        request = {"deleteSheet": {"sheetId": self.to_sheet_id(sheet)}}
        self._batch_update(request)

    def copy_sheet(self, sheet: int | str) -> int:
        sheet = (
            self.api.sheets()
            .copyTo(
                spreadsheetId=self.id,
                sheetId=self.to_sheet_id(sheet),
                body=dict(destinationSpreadsheetId=self.id),
            )
            .execute()
        )
        sheet_id = sheet["sheetId"]
        return sheet_id

    def rename_sheet(self, sheet: int | str, name: str):
        request = {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": self.to_sheet_id(sheet),
                    "title": name,
                },
                "fields": "title",
            }
        }
        self._batch_update(request)

    def copy_and_write(
        self, copy_from: str, copy_to: str, df: pl.DataFrame, overwrite: bool = False
    ):
        sheet_id = self.copy_sheet(copy_from)
        if overwrite and copy_to in self.describe()["title"]:
            self.delete_sheet(copy_to)

        self.rename_sheet(sheet_id, copy_to)
        self.write_sheet(copy_to, df)


def get_google_sheets_credentials_scopes():
    return ["https://www.googleapis.com/auth/spreadsheets"]


def get_google_drive_credentials_scopes():
    return ["https://www.googleapis.com/auth/drive.file"]


def build_spreadsheets(spreadsheet_id: str, service_account_info: str) -> Spreadsheets:
    service_account_info = json.loads(service_account_info)
    credentials = get_credentials(
        service_account_info=service_account_info,
        scopes=get_google_sheets_credentials_scopes(),
    )
    spreadsheets = Spreadsheets(spreadsheet_id=spreadsheet_id, credentials=credentials)
    return spreadsheets


def build_drive(authorized_user_info: str) -> Drive:
    authorized_user_info = json.loads(authorized_user_info)
    credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
        authorized_user_info, scopes=get_google_drive_credentials_scopes()
    )
    if credentials.expired:
        if credentials.refresh_token:
            credentials.refresh(google.auth.transport.requests.Request())
        else:
            raise ValueError("Credentials are expired and have no refresh token.")

    drive = Drive(credentials=credentials)
    return drive


def run_interactive_user_credentials_flow(client_secrets_path: str, scopes: list[str]):
    """
    The client_secrets can be downloaded from the Google cloud console.
    The resulting credentials can be saved as authorized_user_info via creds.to_json().
    """
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_path, scopes
    )
    credentials = flow.run_local_server(port=0)
    return credentials
