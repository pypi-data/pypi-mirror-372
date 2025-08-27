import pandera as pa
from pandera.typing import Series

class UserBaseSchema(pa.DataFrameModel):
    """Base schema for user-related operations in Pandera DataFrame format.
    
    This schema defines the core user fields required for authentication and identification.
    It serves as the foundation for user data validation across the system.
    """
    profit_user_code: Series[str] = pa.Field(coerce=True, nullable=False)
    person_id: Series[str] = pa.Field(coerce=True, nullable=False)

class UserUpdateSchema(pa.DataFrameModel):
    userPrincipalName: Series[str] = pa.Field(coerce=True, nullable=True)
    mail: Series[str] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True
