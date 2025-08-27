import pandera as pa
from pandera.typing import Series
import pandas as pd
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class CustomTableSchema(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Custom Table ID", alias="id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, description="Employee ID", alias="employeeId")

    class Config:
        coerce = True
