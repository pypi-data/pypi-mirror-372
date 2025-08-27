import pandera as pa
from pandera.typing import Series, DateTime
from .person import PersonBaseSchema
from .employee import EmployeeBaseSchema
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import math
import pandas as pd

class AddressBaseSchema(pa.DataFrameModel):
    country: Series[str] = pa.Field(coerce=True, nullable=False)
    street: Series[str] = pa.Field(coerce=True, nullable=False)
    street_number: Series[str] = pa.Field(coerce=True, nullable=False)
    postal_code: Series[str] = pa.Field(coerce=True, nullable=False)
    city: Series[str] = pa.Field(coerce=True, nullable=True)

class AddressGetSchema(pa.DataFrameModel):
    address_id: Series[int] = pa.Field(coerce=True)
    address_line: Series[str] = pa.Field(coerce=True,nullable=True)
    po_box: Series[bool] = pa.Field(coerce=True)
    address_add: Series[str] = pa.Field(coerce=True, nullable=True)
    address: Series[str] = pa.Field(coerce=True, nullable=True)
    number: Series[pd.Int64Dtype] = pa.Field(nullable=True)
    number_add: Series[str] = pa.Field(coerce=True, nullable=True)
    zip_code: Series[str] = pa.Field(coerce=True, nullable=True)
    recidence: Series[str] = pa.Field(coerce=True, nullable=True)
    country: Series[str] = pa.Field(coerce=True)
    addition: Series[str] = pa.Field(coerce=True, nullable=True)
    create_date: Series[str] = pa.Field(coerce=True, nullable=True)
    modified_date: Series[str] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True

class AddressUpdateSchemaEmployee(AddressBaseSchema, EmployeeBaseSchema, PersonBaseSchema):
    address_active_effective_date: Series[DateTime] = pa.Field(coerce=True, nullable=False)
    street_number_add: Series[str] = pa.Field(coerce=True, nullable=True)
    match_employees_on: Series[str] = pa.Field(coerce=True, nullable=True)
    ssn: Series[str] = pa.Field(coerce=True, nullable=True)
    find_address_based_on_postal_code: Series[bool] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True

class EmployeeAddressUpdateSchema(BaseModel):
    """
    Pydantic schema for address updates.
    This schema is used specifically for update operations while maintaining compatibility with existing schemas.
    """
    person_id: str = Field(..., description="Person id")
    employee_id: str = Field(..., description="Employee id")

    address_active_effective_date: datetime = Field(
        ...,
        description="The effective date from which the address update should be active"
    )
    street: str = Field(..., min_length=1, max_length=100, description="Street name")
    street_number: Optional[str] = Field(..., min_length=1, max_length=20, description="Street number")
    house_number: Optional[str] = Field(..., min_length=1, max_length=20, description="House Number")
    street_number_add: Optional[str] = Field(
        None,
        max_length=20,
        description="Additional street number information"
    )
    postal_code: str = Field(..., min_length=1, max_length=12, description="Postal code")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    country: str = Field(..., min_length=1, max_length=100, description="Country name")
    ssn: Optional[str] = Field(
        None,
        min_length=1,
        max_length=20,
        description="Social Security Number"
    )
    find_address_based_on_postal_code: Optional[bool] = Field(
        None,
        description="Flag to indicate if address should be found based on postal code"
    )

    @field_validator('street_number', 'street_number_add', 'ssn', mode='before')
    def handle_nan(cls, v):
        if isinstance(v, float) and math.isnan(v):
            return None
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "address_active_effective_date": "2025-02-10T00:00:00",
                "street": "Example Street",
                "street_number": "123",
                "street_number_add": "A",
                "postal_code": "1234AB",
                "city": "Example City",
                "country": "Example Country",
                "ssn": "123456789",
                "find_address_based_on_postal_code": True
            }
        }
