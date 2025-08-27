import pandas as pd
import pandera as pa
from pandera import Bool
from pandera.typing import Series, String, Float, DateTime
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class EmploymentSchema(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employment ID", alias="id")
    employee_id: Series[String] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")
    active_effective_date: Series[DateTime] = pa.Field(coerce=True, description="Active Effective Date", alias="activeEffectiveDate")
    contract: Series[String] = pa.Field(coerce=True, nullable=True, description="Contract", alias="contract") # has a list of possible values
    creation_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Creation Date", alias="creationDate")
    effective_date: Series[DateTime] = pa.Field(coerce=True, description="Effective Date", alias="effectiveDate")
    end_effective_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="End Effective Date", alias="endEffectiveDate")
    fte: Series[Float] = pa.Field(coerce=True, description="FTE", alias="fte")
    is_current: Series[Bool] = pa.Field(coerce=True, description="Is Current", alias="isCurrent")
    modification_date: Series[DateTime] = pa.Field(coerce=True, nullable=True, description="Modification Date", alias="modificationDate")
    salary_pay_type: Series[String] = pa.Field(coerce=True, nullable=True, description="Salary Pay Type", alias="salaryPayType")
    weekly_hours: Series[Float] = pa.Field(coerce=True, nullable=True, description="Weekly Hours", alias="weeklyHours")
    # weekly_hours_sort_factor: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False)
    actual_working_pattern_working_pattern_type: Series[pa.String] = pa.Field(nullable=True, description="Actual Working Pattern Working Pattern Type", alias="actualWorkingPattern.workingPatternType")
    actual_working_pattern_days_sunday: Series[Float] = pa.Field(nullable=True, description="Actual Working Pattern Days Sunday", alias="actualWorkingPattern.days.sunday")
    actual_working_pattern_days_tuesday: Series[Float] = pa.Field(nullable=True, description="Actual Working Pattern Days Tuesday", alias="actualWorkingPattern.days.tuesday")
    actual_working_pattern_days_wednesday: Series[Float] = pa.Field(nullable=True, description="Actual Working Pattern Days Wednesday", alias="actualWorkingPattern.days.wednesday")
    actual_working_pattern_days_monday: Series[Float] = pa.Field(nullable=True, description="Actual Working Pattern Days Monday", alias="actualWorkingPattern.days.monday")
    actual_working_pattern_days_friday: Series[Float] = pa.Field(nullable=True, description="Actual Working Pattern Days Friday", alias="actualWorkingPattern.days.friday")
    actual_working_pattern_days_thursday: Series[Float] = pa.Field(nullable=True, description="Actual Working Pattern Days Thursday", alias="actualWorkingPattern.days.thursday")
    actual_working_pattern_days_saturday: Series[Float] = pa.Field(nullable=True, description="Actual Working Pattern Days Saturday", alias="actualWorkingPattern.days.saturday")

    class Config:
        coerce = True
