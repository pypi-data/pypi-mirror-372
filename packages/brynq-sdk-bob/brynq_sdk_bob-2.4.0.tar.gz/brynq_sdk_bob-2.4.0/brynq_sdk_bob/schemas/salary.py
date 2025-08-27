import pandas as pd
import pandera as pa
from pandera import Bool
from pandera.typing import Series, String, Float, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel


class SalarySchema(BrynQPanderaDataFrameModel):
    id: Series[String] = pa.Field(coerce=True, description="Salary ID", alias="id")
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    pay_frequency: Series[String] = pa.Field(coerce=True, nullable=True, description="Pay Frequency", alias="payFrequency") # has a list of possible values , isin=['Monthly']
    creation_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Creation Date", alias="creationDate")
    is_current: Series[Bool] = pa.Field(coerce=True, description="Is Current", alias="isCurrent")
    modification_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Modification Date", alias="modificationDate")
    effective_date: Series[DateTime] = pa.Field(coerce=True, description="Effective Date", alias="effectiveDate")
    end_effective_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="End Effective Date", alias="endEffectiveDate")
    change_reason: Series[str] = pa.Field(coerce=True, nullable=True, description="Change Reason", alias="change.reason")
    pay_period: Series[String] = pa.Field(coerce=True, nullable=True, description="Pay Period", alias="payPeriod")
    base_value: Series[Float] = pa.Field(coerce=True, nullable=True, description="Base Value", alias="base.value") #needs to become base.value?
    base_currency: Series[String] = pa.Field(coerce=True, nullable=True, description="Base Currency", alias="base.currency")
    active_effective_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Active Effective Date", alias="activeEffectiveDate")

    class Config:
        coerce = True
