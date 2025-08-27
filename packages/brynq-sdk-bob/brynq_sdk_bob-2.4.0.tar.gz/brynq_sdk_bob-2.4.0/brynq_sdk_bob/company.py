import pandas as pd


class Company:
    def __init__(self, bob):
        self.bob = bob

    def get_variable_values(self, list_name: str = None) -> dict:
        values = {}

        if list_name is not None:
            resp = self.bob.session.get(url=f"{self.bob.base_url}company/named-lists/{list_name}", timeout=self.bob.timeout)
            resp.raise_for_status()
            data = resp.json()
            values.update({data["name"]: [value['id'] for value in data['values']]})
        else:
            resp = self.bob.session.get(url=f"{self.bob.base_url}company/named-lists", timeout=self.bob.timeout)
            resp.raise_for_status()
            data = resp.json()
            for list_key, list_data in data.items():
                values.update({list_key: [value['id'] for value in list_data['values']]})

        return values
