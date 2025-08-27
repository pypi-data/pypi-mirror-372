import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .schemas.work import WorkSchema


class Work:
    def __init__(self, bob):
        self.bob = bob
        self.schema = WorkSchema

    def get(self) ->(pd.DataFrame, pd.DataFrame):
        request = requests.Request(method='GET',
                                   url=f"{self.bob.base_url}bulk/people/work")
        data = self.bob.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='values',
            meta=['employeeId']
        )
        valid_work, invalid_work = Functions.validate_data(df=df, schema=self.schema, debug=True)

        return valid_work, invalid_work
