import pandera as pa
from pandera.typing import Series, DateTime

class FamilyGetSchema(pa.DataFrameModel):
    employee_id: Series[str] = pa.Field(coerce=True, nullable=False)
    first_name: Series[str] = pa.Field(coerce=True, nullable=False)
    last_name: Series[str] = pa.Field(coerce=True, nullable=True)
    prefix: Series[str] = pa.Field(coerce=True, nullable=True)
    type_of_family: Series[str] = pa.Field(coerce=True, nullable=True)
    birth_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True
