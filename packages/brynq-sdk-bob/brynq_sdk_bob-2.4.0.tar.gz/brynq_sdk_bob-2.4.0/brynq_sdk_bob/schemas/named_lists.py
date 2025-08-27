import pandera as pa
from pandera.typing import Series
from brynq_sdk_functions import BrynQPanderaDataFrameModel

class NamedListSchema(BrynQPanderaDataFrameModel):
    id: Series[str] = pa.Field(coerce=True, description="Named List ID", alias="id")
    value: Series[str] = pa.Field(coerce=True, description="Named List Value", alias="value")
    name: Series[str] = pa.Field(coerce=True, description="Named List Name", alias="name")
    archived: Series[bool] = pa.Field(coerce=True, description="Named List Archived", alias="archived")
    # children: Series[list] = pa.Field(coerce=True)
    type: Series[str] = pa.Field(coerce=True, description="Named List Type", alias="type")

    class Config:
        coerce = True
