from datetime import datetime
import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.named_lists import NamedListSchema


class NamedLists:
    def __init__(self, bob):
        self.bob = bob
        self.schema = NamedListSchema

    def get(self) -> (pd.DataFrame, pd.DataFrame):
        """
        Get custom table data for an employee

        Args:
            list_name: The list name

        Returns:
            A tuple of (valid_data, invalid_data) as pandas DataFrames
        """
        url = f"{self.bob.base_url}company/named-lists/"
        resp = self.bob.session.get(url=url)
        resp.raise_for_status()
        data = resp.json()

        df = pd.DataFrame([
            {**item, "type": key}
            for key, group in data.items()
            for item in group["values"]
        ])

        # Normalize the nested JSON response
        # df = pd.DataFrame(data.get('values'))
        valid_data, invalid_data = Functions.validate_data(df=df, schema=NamedListSchema, debug=True)

        return valid_data, invalid_data
