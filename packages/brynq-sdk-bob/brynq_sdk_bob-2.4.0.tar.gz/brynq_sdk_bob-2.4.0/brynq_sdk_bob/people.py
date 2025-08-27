import pandas as pd
from brynq_sdk_functions import Functions
from .bank import Bank
from .employment import Employment
from .salaries import Salaries
from .schemas.people import PeopleSchema
from .work import Work
from .custom_tables import CustomTables


class People:
    def __init__(self, bob):
        self.bob = bob
        self.salaries = Salaries(bob)
        self.employment = Employment(bob)
        self.bank = Bank(bob)
        self.work = Work(bob)
        self.custom_tables = CustomTables(bob)
        self.schema = PeopleSchema
        self.field_name_in_body, self.field_name_in_response, self.endpoint_to_response = self._init_fields()

    def get(self, additional_fields: list[str] = [], field_selection: list[str] = []) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get people from Bob

        Args:
            additional_fields (list[str]): Additional fields to get (not defined in the schema)
            field_selection (list[str]): Fields to get (defined in the schema), if not provided, all fields are returned
        """
        #resp = self.bob.session.get(url=f"{self.bob.base_url}profiles", timeout=self.bob.timeout)
        body_fields = list(set(self.field_name_in_body + additional_fields))
        response_fields = list(set(self.field_name_in_response + additional_fields))

        if field_selection:
            body_fields = [field for field in body_fields if field in field_selection]
            response_fields = [self.endpoint_to_response.get(field) for field in field_selection if field in self.endpoint_to_response]

        # Bob sucks with default fields so you need to do a search call to retrieve additional fields.
        resp_additional_fields = self.bob.session.post(url=f"{self.bob.base_url}people/search",
                                                       json={
                                                           "fields": body_fields,
                                                           "filters": []
                                                       },
                                                       timeout=self.bob.timeout)
        json_response = resp_additional_fields.json()
        df = pd.json_normalize(resp_additional_fields.json()['employees'])
        df = df[[col for col in response_fields if col in df.columns]]
        # Get the valid column names from PeopleSchema
        valid_people, invalid_people = Functions.validate_data(df=df, schema=PeopleSchema, debug=True)
        return valid_people, invalid_people


    def _init_fields(self) -> tuple[list[str], list[str], dict[str, str]]:
        resp_fields = self.bob.session.get(
            url=f"{self.bob.base_url}company/people/fields",
            timeout=self.bob.timeout,
            headers=self.bob.headers
        )
        fields = resp_fields.json()
        field_name_in_body = [field.get('id') for field in fields]
        field_name_in_response = [field['jsonPath'] for field in fields]
        endpoint_to_response = {field['id']: field['jsonPath'] for field in fields}
        return field_name_in_body, field_name_in_response, endpoint_to_response

    def _get_employee_id_to_person_id_mapping(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        employee_id_in_company = "work.employeeIdInCompany"
        person_id = "root.id"

        body_fields = [employee_id_in_company, person_id]
        response_fields = [self.endpoint_to_response.get(field) for field in body_fields if field in self.endpoint_to_response]

        resp_additional_fields = self.bob.session.post(url=f"{self.bob.base_url}people/search",
                                                       json={
                                                           "fields": body_fields,
                                                           "filters": []
                                                       },
                                                       timeout=self.bob.timeout)
        df = pd.json_normalize(resp_additional_fields.json()['employees'])
        df = df[[col for col in response_fields if col in df.columns]]
        # Get the valid column names from PeopleSchema
        valid_people, invalid_people = Functions.validate_data(df=df, schema=PeopleSchema, debug=True)
        return valid_people, invalid_people
