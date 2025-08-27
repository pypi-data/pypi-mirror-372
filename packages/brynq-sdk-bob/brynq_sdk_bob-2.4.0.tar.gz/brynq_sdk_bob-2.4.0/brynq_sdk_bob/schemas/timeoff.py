import pandera as pa
from pandera.typing import Series, String, Float
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class TimeOffSchema(BrynQPanderaDataFrameModel):
    change_type: Series[String] = pa.Field(coerce=True, description="Change Type", alias="changeType")
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    employee_display_name: Series[String] = pa.Field(coerce=True, description="Employee Display Name", alias="employeeDisplayName")
    employee_email: Series[String] = pa.Field(coerce=True, description="Employee Email", alias="employeeEmail")
    request_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Request ID", alias="requestId")
    policy_type_display_name: Series[String] = pa.Field(coerce=True, description="Policy Type Display Name", alias="policyTypeDisplayName")
    type: Series[String] = pa.Field(coerce=True, description="Type", alias="type")
    start_date: Series[String] = pa.Field(coerce=True, description="Start Date", alias="startDate")
    start_portion: Series[String] = pa.Field(coerce=True, description="Start Portion", alias="startPortion")
    end_date: Series[String] = pa.Field(coerce=True, description="End Date", alias="endDate")
    end_portion: Series[String] = pa.Field(coerce=True, description="End Portion", alias="endPortion")
    day_portion: Series[String] = pa.Field(coerce=True, description="Day Portion", alias="dayPortion")
    date: Series[String] = pa.Field(coerce=True, description="Date", alias="date")
    hours_on_date: Series[Float] = pa.Field(coerce=True, description="Hours on Date", alias="hoursOnDate")
    daily_hours: Series[Float] = pa.Field(coerce=True, description="Daily Hours", alias="dailyHours")
    duration_unit: Series[String] = pa.Field(coerce=True, description="Duration Unit", alias="durationUnit")
    total_duration: Series[Float] = pa.Field(coerce=True, description="Total Duration", alias="totalDuration")
    total_cost: Series[Float] = pa.Field(coerce=True, description="Total Cost", alias="totalCost")
    change_reason: Series[String] = pa.Field(nullable=True, coerce=True, description="Change Reason", alias="changeReason")
    visibility: Series[String] = pa.Field(coerce=True, description="Visibility", alias="visibility")

    class Config:
        coerce = True


class TimeOffBalanceSchema(BrynQPanderaDataFrameModel):
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    policy_type_name: Series[String] = pa.Field(coerce=True, description="Policy Type Name", alias="policyTypeName")
    policy_type_display_name: Series[String] = pa.Field(coerce=True, description="Policy Type Display Name", alias="policyTypeDisplayName")
    balance: Series[Float] = pa.Field(coerce=True, description="Current Balance", alias="balance")
    used: Series[Float] = pa.Field(coerce=True, description="Used Balance", alias="used")
    available: Series[Float] = pa.Field(coerce=True, description="Available Balance", alias="available")
    approved_requests: Series[Float] = pa.Field(coerce=True, description="Approved Requests", alias="approvedRequests")
    pending_requests: Series[Float] = pa.Field(coerce=True, description="Pending Requests", alias="pendingRequests")
    as_of_date: Series[String] = pa.Field(coerce=True, description="As of Date", alias="asOfDate")
    accrual_start_date: Series[String] = pa.Field(nullable=True, coerce=True, description="Accrual Start Date", alias="accrualStartDate")
    expiry_date: Series[String] = pa.Field(nullable=True, coerce=True, description="Expiry Date", alias="expiryDate")
    duration_unit: Series[String] = pa.Field(coerce=True, description="Duration Unit", alias="durationUnit")

    class Config:
        coerce = True
