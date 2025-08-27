import pandas as pd
import requests
from .schemas.employment import EmploymentSchema
from brynq_sdk_functions import Functions


class Employment:
    def __init__(self, bob):
        self.bob = bob
        self.schema = EmploymentSchema

    def get(self) -> (pd.DataFrame, pd.DataFrame):
        request = requests.Request(method='GET',
                                   url=f"{self.bob.base_url}bulk/people/employment")
        data = self.bob.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='values',
            meta=['employeeId']
        )
        valid_contracts, invalid_contracts = Functions.validate_data(df=df, schema=self.schema, debug=True)

        return valid_contracts, invalid_contracts
