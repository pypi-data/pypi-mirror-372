import pandas as pd
import pandera as pa
from pandera.typing import Series, DateTime
from .employee import EmployeeBaseSchema


class BaseTimetableSchema(EmployeeBaseSchema):
    startdate: Series[DateTime] = pa.Field(coerce=True, nullable=False)
    weekly_hours: Series[float] = pa.Field(coerce=True, nullable=False)
    parttime_percentage: Series[float] = pa.Field(coerce=True, nullable=False)

    class Config:
        coerce = True
        strict = False


class TimetableUpdateSchema(BaseTimetableSchema):
    # Optional Fields
    changing_work_pattern: Series[bool] = pa.Field(coerce=True, nullable=True)
    days_per_week: Series[float] = pa.Field(coerce=True, nullable=True)
    fte: Series[float] = pa.Field(coerce=True, nullable=True)
    employment_number: Series[str] = pa.Field(coerce=True, nullable=True)
    type_of_schedule: Series[str] = pa.Field(coerce=True, nullable=True)
