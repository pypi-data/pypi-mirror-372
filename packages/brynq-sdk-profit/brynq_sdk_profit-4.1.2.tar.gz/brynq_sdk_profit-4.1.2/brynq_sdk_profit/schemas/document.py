import pandera as pa
from pandera.typing import Series, String, DateTime

class DocumentSchema(pa.DataFrameModel):
    """Schema for handling document-related operations in DataFrame format.
    
    This schema validates and processes document metadata including file information,
    employee associations, and document attributes. It ensures proper structure for
    document management operations within the system.
    """
    dossier_id: Series[String] = pa.Field(coerce=True)
    attachment_code: Series[String] = pa.Field(coerce=True)
    filename: Series[String] = pa.Field(coerce=True)
    subject: Series[String] = pa.Field(coerce=True)
    entry_date: Series[DateTime] = pa.Field(coerce=True)
    employee_id: Series[str] = pa.Field(coerce=True)