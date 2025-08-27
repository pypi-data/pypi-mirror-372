from datetime import datetime, timezone, timedelta
import pandas as pd
from brynq_sdk_functions import Functions
from .schemas.timeoff import TimeOffSchema, TimeOffBalanceSchema
import warnings


class TimeOff:
    def __init__(self, bob):
        self.bob = bob
        self.schema = TimeOffSchema
        self.balance_schema = TimeOffBalanceSchema

    def get(self, since: datetime = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get time off requests

        Args:
            since (datetime, optional): The start date of the time off requests max 6 months ago. Defaults to 6 months ago if not provided.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple of (valid_timeoff, invalid_timeoff) as pandas DataFrames
        """
        max_lookback = timedelta(days=int((365 / 2) - 1))
        now_utc = datetime.now(timezone.utc)
        six_months_ago = now_utc - max_lookback
        #if since is provided, use it and cap to 6 months max
        if since is not None:
            if since.tzinfo is None:
                since = since.replace(tzinfo=timezone.utc)
            if since < six_months_ago:
                warnings.warn("The 'since' date is more than 6 months ago. Limiting to 6 months ago due to API restrictions.")
                since = six_months_ago
        #if no since is provided, use 6 months ago
        else:
            since = six_months_ago

        since = since.replace(tzinfo=timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        resp = self.bob.session.get(url=f"{self.bob.base_url}timeoff/requests/changes",
                                    params={'since': since},
                                    timeout=self.bob.timeout)
        resp.raise_for_status()
        data = resp.json()['changes']
        # data = self.bob.get_paginated_result(request)
        df = pd.json_normalize(
            data,
            record_path='changes',
            meta=['employeeId']
        )
        valid_timeoff, invalid_timeoff = Functions.validate_data(df=df, schema=self.schema, debug=True)

        return valid_timeoff, invalid_timeoff

    def get_balance(self, employee_id: str, policy_type: str = None, as_of_date: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get time off balance for a specific employee

        Args:
            employee_id (str): The ID of the employee
            policy_type (str, optional): The policy type to filter by. Defaults to None.
            as_of_date (str, optional): The date to get balance as of (YYYY-MM-DD format). Defaults to None.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple of (valid_balance, invalid_balance) as pandas DataFrames
        """
        params = {}
        if policy_type:
            params['policyType'] = policy_type
        if as_of_date:
            params['asOfDate'] = as_of_date

        resp = self.bob.session.get(
            url=f"{self.bob.base_url}timeoff/employees/{employee_id}/balance",
            params=params,
            timeout=self.bob.timeout
        )
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data)

        valid_balance, invalid_balance = Functions.validate_data(df=df, schema=self.balance_schema, debug=True)

        return valid_balance, invalid_balance
