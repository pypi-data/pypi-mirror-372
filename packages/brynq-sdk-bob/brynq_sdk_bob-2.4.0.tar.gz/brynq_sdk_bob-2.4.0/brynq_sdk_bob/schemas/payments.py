import pandera as pa
from pandera.typing import Series, String, Float, DateTime
from typing import Optional
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class VariablePaymentSchema(BrynQPanderaDataFrameModel):
    can_be_deleted: Series[bool] = pa.Field(nullable=True, coerce=True, description="Can Be Deleted", alias="canBeDeleted")
    department_percent: Series[Float] = pa.Field(nullable=True, coerce=True, description="Department Percent", alias="departmentPercent")
    payout_type: Series[String] = pa.Field(coerce=True, description="Payout Type", alias="payoutType")
    num_of_salaries: Optional[Series[pd.Int64Dtype]] = pa.Field(nullable=True, coerce=True, description="Number of Salaries", alias="numOfSalaries")
    end_date: Series[DateTime] = pa.Field(nullable=True, coerce=True, description="End Date", alias="endDate")
    creation_date: Series[DateTime] = pa.Field(coerce=True, description="Creation Date", alias="creationDate")
    percentage_of_annual_salary: Series[Float] = pa.Field(nullable=True, coerce=True, description="Percentage of Annual Salary", alias="percentageOfAnnualSalary")
    individual_percent: Series[Float] = pa.Field(nullable=True, coerce=True, description="Individual Percent", alias="individualPercent")
    variable_type: Series[String] = pa.Field(nullable=True, coerce=True, description="Variable Type", alias="variableType")
    is_current: Series[bool] = pa.Field(nullable=True, coerce=True, description="Is Current", alias="isCurrent")
    modification_date: Series[DateTime] = pa.Field(nullable=True, coerce=True, description="Modification Date", alias="modificationDate")
    company_percent: Series[Float] = pa.Field(nullable=True, coerce=True, description="Company Percent", alias="companyPercent")
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="ID", alias="id")
    end_effective_date: Series[DateTime] = pa.Field(nullable=True, coerce=True, description="End Effective Date", alias="endEffectiveDate")
    payment_period: Series[String] = pa.Field(coerce=True, description="Payment Period", alias="paymentPeriod")
    effective_date: Series[DateTime] = pa.Field(coerce=True, description="Effective Date", alias="effectiveDate")
    amount_value: Series[Float] = pa.Field(coerce=True, description="Amount Value", alias="amount.value")
    amount_currency: Series[String] = pa.Field(coerce=True, description="Amount Currency", alias="amount.currency")
    change_reason: Series[String] = pa.Field(nullable=True, coerce=True, description="Change Reason", alias="change.reason")
    change_changed_by: Series[String] = pa.Field(nullable=True, coerce=True, description="Change Changed By", alias="change.changedBy")
    change_changed_by_id: Series[pd.Int64Dtype] = pa.Field(nullable=True, coerce=True, description="Change Changed By ID", alias="change.changedById")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employee ID", alias="employee_id") #set manually
    class Config:
        coerce = True

class ActualPaymentsSchema(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Payment ID", alias="id")
    pay_date: Series[DateTime] = pa.Field(coerce=True, description="Pay Date", alias="payDate")
    pay_type: Series[String] = pa.Field(coerce=True, description="Pay Type", alias="payType")
    amount_value: Series[Float] = pa.Field(coerce=True, description="Amount Value", alias="amount.value")
    amount_currency: Series[String] = pa.Field(coerce=True, description="Amount Currency", alias="amount.currency")
    change_reason: Series[String] = pa.Field(nullable=True, coerce=True, description="Change Reason", alias="change.reason")
    change_changed_by: Series[String] = pa.Field(nullable=True, coerce=True, description="Change Changed By", alias="change.changedBy")
    change_changed_by_id: Series[String] = pa.Field(nullable=True, coerce=True, description="Change Changed By ID", alias="change.changedById")

    class Config:
        coerce = True
