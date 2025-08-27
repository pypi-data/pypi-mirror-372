import pandera as pa
from pandera.typing import Series, DateTime

class DateBaseSchema(pa.DataFrameModel):
    start_date: Series[DateTime] = pa.Field(coerce=True, nullable=False)
    end_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True
