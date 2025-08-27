import pandas as pd
from typing import Optional, List
from brynq_sdk_functions import Functions
from .schemas.payments import VariablePaymentSchema, ActualPaymentsSchema


class Payments:
    def __init__(self, bob):
        self.bob = bob
        self.schema = VariablePaymentSchema

    def get(self, person_id: str) -> (pd.DataFrame, pd.DataFrame):
        resp = self.bob.session.get(url=f"{self.bob.base_url}people/{person_id}/variable", timeout=self.bob.timeout)
        resp.raise_for_status()
        data = resp.json()
        df = pd.json_normalize(
            data,
            record_path='values'
        )
        df['employee_id'] = person_id
        valid_payments, invalid_payments = Functions.validate_data(df=df, schema=self.schema, debug=True)

        return valid_payments, invalid_payments

    def get_actual_payments(
        self,
        limit: int = 200,
        employee_ids: Optional[List[str]] = None,
        pay_date_from: Optional[str] = None,
        pay_date_to: Optional[str] = None
    ) -> (pd.DataFrame, pd.DataFrame):
        """
        Search for actual payments with optional employee and pay date filters.
        This method auto-paginates until all results are fetched.

        See Bob API: https://apidocs.hibob.com/reference/post_people-actual-payments-search
        See Pagination: https://apidocs.hibob.com/docs/pagination

        Args:
            limit (int): Number of records per page (default: 50, max: 200).
            employee_ids (Optional[List[str]]): Filter by employee IDs.
            pay_date_from (Optional[str]): Inclusive start date filter (YYYY-MM-DD).
            pay_date_to (Optional[str]): Inclusive end date filter (YYYY-MM-DD).

        Returns:
            tuple: (valid_payments DataFrame, invalid_payments DataFrame)
        """
        base_payload = {
            "pagination": {
                "limit": limit
            }
        }

        filters = []
        if employee_ids:
            filters.append({
                "fieldPath": "employeeId",
                "operator": "equals",
                "values": employee_ids
            })
        if pay_date_from:
            filters.append({
                "fieldPath": "payDate",
                "operator": "greaterThanOrEquals",
                "value": pay_date_from
            })
        if pay_date_to:
            filters.append({
                "fieldPath": "payDate",
                "operator": "lessThanOrEquals",
                "value": pay_date_to
            })

        if filters:
            base_payload["filters"] = filters

        all_results = []
        next_cursor = None

        while True:
            payload = dict(base_payload)
            payload["pagination"] = dict(base_payload["pagination"])
            if next_cursor:
                payload["pagination"]["cursor"] = next_cursor

            resp = self.bob.session.post(
                url=f"{self.bob.base_url}people/actual-payments/search",
                json=payload,
                timeout=self.bob.timeout
            )
            resp.raise_for_status()
            data = resp.json()

            page_results = data.get('results') or []
            if page_results:
                all_results.extend(page_results)

            next_cursor = (data.get('response_metadata') or {}).get('next_cursor')
            if not next_cursor:
                break

        if not all_results:
            empty_df = pd.DataFrame()
            return empty_df, empty_df

        df = pd.json_normalize(all_results)

        valid_payments, invalid_payments = Functions.validate_data(
            df=df,
            schema=ActualPaymentsSchema,
            debug=True
        )

        return valid_payments, invalid_payments
