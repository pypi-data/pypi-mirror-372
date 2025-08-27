import pandera as pa
from pandera.typing import Series

from .employee import EmployeeBaseSchema
from .person import PersonBaseSchema

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import math


class BaseBankAccountSchema(pa.DataFrameModel):
    iban: Series[str] = pa.Field(coerce=True)
    bankname: Series[str] = pa.Field(coerce=True, nullable=True)
    country: Series[str] = pa.Field(coerce=True, nullable=True)
    bank_type: Series[str] = pa.Field(coerce=True, nullable=True)
    bic_code: Series[str] = pa.Field(coerce=True, nullable=True)

class GetBankAccountSchema(EmployeeBaseSchema):
    iban: Series[str] = pa.Field(coerce=True, nullable=True)
    bic_code: Series[str] = pa.Field(coerce=True, nullable=True)
    seq_no: Series[str] = pa.Field(coerce=True, nullable=True)


# Employee bank account update schema
class BankAccountUpdateSchema(BaseBankAccountSchema):
    # Required Fields (from base)
    employee_id: Series[str] = pa.Field(coerce=True, nullable=False)

    # Optional Fields - Settings
    cash_payment: Series[bool] = pa.Field(coerce=True, nullable=True)
    salary_bank_account: Series[bool] = pa.Field(coerce=True, nullable=True)
    acc_outside_sepa: Series[bool] = pa.Field(coerce=True, nullable=True)
    iban_check: Series[bool] = pa.Field(coerce=True, nullable=True)
    sequence_number: Series[int] = pa.Field(coerce=True, nullable=True)
    routing_number: Series[int] = pa.Field(coerce=True, nullable=True)

class BankAccountUpdateInfoSchema(BaseModel):
    """
    Pydantic schema for employee bank account updates.
    This schema is used specifically for update operations while maintaining compatibility with existing schemas.
    """
    # Required field
    employee_id: str = Field(..., description="Employee id")
    iban: str = Field(..., description="IBAN number")

    # Optional fields from BaseBankAccountSchema
    bankname: Optional[str] = Field(None, max_length=100, description="Name of the bank")
    country: Optional[str] = Field(None, max_length=100, description="Country of the bank")
    bank_type: Optional[str] = Field(None, description="Type of bank account")
    bic_code: Optional[str] = Field(None, max_length=11, description="BIC/SWIFT code")

    # Optional Settings fields
    cash_payment: Optional[bool] = Field(None, description="Flag to indicate if payment is made in cash")
    salary_bank_account: Optional[bool] = Field(None, description="Flag to indicate if this is a salary bank account")
    acc_outside_sepa: Optional[bool] = Field(None, description="Flag to indicate if account is outside SEPA")
    sequence_number: Optional[int] = Field(None, description="Sequence number")
    routing_number: Optional[int] = Field(None, description="Bank routing number")
    iban_check: Optional[bool] = Field(None, description="Flag to indicate if IBAN should be checked")

    @field_validator('bic_code', 'routing_number', 'sequence_number', mode='before')
    def handle_nan(cls, v):
        if isinstance(v, float) and math.isnan(v):
            return None
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee_id": "12345",
                "iban": "NL91ABNA0417164300",
                "bankname": "Example Bank",
                "country": "Netherlands",
                "bank_type": "Savings",
                "bic_code": "ABNANL2A",
                "cash_payment": False,
                "salary_bank_account": True,
                "acc_outside_sepa": False,
                "sequence_number": 1,
                "routing_number": 123456789,
                "iban_check": True
            }
        }


class BankAccountUpdatePersonSchema(BaseModel):
    """
    Pydantic schema for person bank account updates.
    This schema is used specifically for update operations while maintaining compatibility with existing schemas.
    """
    person_id: str = Field(..., description="Person id")

    # Required fields from BaseBankAccountSchema
    iban: str = Field(..., description="IBAN number")

    # Optional fields from BaseBankAccountSchema
    bankname: Optional[str] = Field(None, max_length=100, description="Name of the bank")
    country: Optional[str] = Field(None, max_length=100, description="Country of the bank")
    bank_type: Optional[str] = Field(None, description="Type of bank account")
    bic_code: Optional[str] = Field(None, max_length=11, description="BIC/SWIFT code")

    # Optional fields specific to person bank account
    match_employees_on: Optional[str] = Field(None, description="Field to match employees on")
    match_person: Optional[str] = Field(None, description="Value to match person with employee (0 to match with person_id)")
    ssn: Optional[str] = Field(None, max_length=20, description="Social Security Number")
    branch_address: Optional[str] = Field(None, max_length=200, description="Bank branch address")
    routing_number: Optional[int] = Field(None, description="Bank routing number")
    bank_name: Optional[str] = Field(None, max_length=100, description="Name of the bank")
    iban_check: Optional[bool] = Field(None, description="Flag to indicate if IBAN should be checked")

    @field_validator('ssn','bic_code', 'routing_number', mode='before')
    def handle_nan(cls, v):
        if isinstance(v, float) and math.isnan(v):
            return None
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "person_id": "12345",
                "iban": "NL91ABNA0417164300",
                "iban_check": True,
                "bankname": "Example Bank",
                "country": "Netherlands",
                "bank_type": "Savings",
                "bic_code": "ABNANL2A",
                "ssn": "123456789",
                "branch_address": "Example Street 123",
                "routing_number": 123456789,
                "bank_name": "Example Bank",
                "match_employees_on": "employee_id",
                "match_person": "0"
            }
        }
