import pandera as pa
from pandera.typing import Series

class ContactBaseSchema(pa.DataFrameModel):
    mail_work: Series[str] = pa.Field(coerce=True, nullable=True)
    mail_private: Series[str] = pa.Field(coerce=True, nullable=True)
    mobile_work: Series[str] = pa.Field(coerce=True, nullable=True)
    mobile_private: Series[str] = pa.Field(coerce=True, nullable=True)
    phone_work: Series[str] = pa.Field(coerce=True, nullable=True)
    phone_private: Series[str] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True
