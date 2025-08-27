import pandas as pd
import requests
from brynq_sdk_functions import Functions
from .schemas.salary import SalarySchema


class Salaries:
    def __init__(self, bob):
        self.bob = bob
        self.schema = SalarySchema

    def get(self) -> (pd.DataFrame, pd.DataFrame):
        request = requests.Request(method='GET',
                                   url=f"{self.bob.base_url}bulk/people/salaries",
                                   params={"limit": 100})
        data = self.bob.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='values',
            meta=['employeeId']
        )
        valid_salaries, invalid_salaries = Functions.validate_data(df=df, schema=SalarySchema, debug=True)

        return valid_salaries, invalid_salaries
