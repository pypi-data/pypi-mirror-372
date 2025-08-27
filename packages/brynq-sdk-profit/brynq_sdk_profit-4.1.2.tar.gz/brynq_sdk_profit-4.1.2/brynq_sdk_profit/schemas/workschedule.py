import pandera as pa
from pandera.typing import Series, DateTime

class WorkscheduleComponentSchema(pa.DataFrameModel):
    startdate_workcycle: Series[DateTime] = pa.Field(coerce=True, nullable=False)
    workcycle: Series[str] = pa.Field(coerce=True, nullable=False)
    start_week: Series[int] = pa.Field(coerce=True, nullable=False)
    index_number: Series[int] = pa.Field(coerce=True, nullable=False)
