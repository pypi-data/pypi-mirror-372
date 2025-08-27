from datetime import datetime
from io import BytesIO

import pandas as pd
from brynq_sdk_functions import Functions


class CustomDocuments:
    def __init__(self, bob):
        self.bob = bob
        # self.headers_upload = self.bob.headers.copy()
        # self.headers_upload['Content-Type'] = 'multipart/form-data'
        # self.headers_upload['Accept'] = 'application/json'

    def get(self, person_id: datetime) -> pd.DataFrame:
        resp = self.bob.session.get(url=f"{self.bob.base_url}docs/people/{person_id}", timeout=self.bob.timeout)
        resp.raise_for_status()
        data = resp.json()['documents']
        df = pd.DataFrame(data)
        # data = self.bob.get_paginated_result(request)
        # df = pd.json_normalize(
        #     data,
        #     record_path='changes',
        #     meta=['employeeId']
        # )
        df = self.bob.rename_camel_columns_to_snake_case(df)
        # valid_documents, invalid_documents = Functions.validate_data(df=df, schema=DocumentsSchema, debug=True)

        return df

    def get_folders(self) -> dict:
        resp = self.bob.session.get(url=f"{self.bob.base_url}docs/folders/metadata", timeout=self.bob.timeout)
        resp.raise_for_status()
        data = resp.json()

        return data

    def create(self,
               person_id: datetime,
               folder_id: str,
               file_name: str,
               file_object: BytesIO):
        files = {"file": (file_name, file_object, "application/pdf")}
        resp = self.bob.session.post(url=f"{self.bob.base_url}docs/people/{person_id}/folders/{folder_id}/upload",
                                     files=files,
                                     timeout=self.bob.timeout)
        resp.raise_for_status()
