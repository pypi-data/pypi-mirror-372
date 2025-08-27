import pandera as pa
from pandera.typing import Series, Int64,  Object, String, DateTime


class PayslipUploadSchema(pa.DataFrameModel):
    payslip_id: Series[str] = pa.Field(coerce=True, nullable=False)
    filename: Series[str] = pa.Field(coerce=True, nullable=False)
    subject: Series[str] = pa.Field(coerce=True, nullable=False)
    attachment_filepath: Series[str] = pa.Field(coerce=True, nullable=False)

class PayslipGetSchema(pa.DataFrameModel):
    employee_id: Series[str] = pa.Field(coerce=True, nullable=True)
    dossier_id: Series[str] = pa.Field(coerce=True, nullable=False)
    dossier_type_id: Series[str] = pa.Field(coerce=True, nullable=False)
    employee: Series[str] = pa.Field(coerce=True, nullable=True)
    employer_number: Series[str] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True

class PayslipMetaInfoSchema(pa.DataFrameModel):
    """Schema for document metainfo data from AFAS"""
    dossier_type_id: Series[Int64] = pa.Field(coerce=True)
    dossier_type: Series[String] = pa.Field(coerce=True)
    dossier_id: Series[str] = pa.Field(coerce=True, nullable=False)
    attachment_id: Series[Int64] = pa.Field(coerce=True)
    attachment_code: Series[String] = pa.Field(coerce=True)
    filename: Series[String] = pa.Field(coerce=True)
    subject: Series[String] = pa.Field(coerce=True)
    entry_date: Series[DateTime] = pa.Field(coerce=True)
    display_date: Series[DateTime] = pa.Field(coerce=True)
    uploaded_by: Series[String] = pa.Field(coerce=True)
    explanation: Series[Object] = pa.Field(coerce=True, nullable=True)
    source_of_file: Series[Int64] = pa.Field(coerce=True)
    description: Series[String] = pa.Field(coerce=True)
    technical_type: Series[String] = pa.Field(coerce=True)
    organisation_name: Series[Object] = pa.Field(coerce=True, nullable=True)
    organisation_email: Series[Object] = pa.Field(coerce=True, nullable=True)
    customer_name: Series[Object] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True