import pandera as pa
from pandera.typing import Series
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CreditorGetSchema(pa.DataFrameModel):
    creditor_id: Series[str] = pa.Field(coerce=True)
    creditor_name: Series[str] = pa.Field(coerce=True)
    bcco: Series[str] = pa.Field(coerce=True)
    search_name: Series[str] = pa.Field(coerce=True,nullable=True)
    address_line_1: Series[str] = pa.Field(coerce=True)
    address_line_2: Series[str] = pa.Field(coerce=True)
    address_line_3: Series[str] = pa.Field(coerce=True, nullable=True)
    tel_nmbr: Series[str] = pa.Field(coerce=True,nullable=True)
    email: Series[str] = pa.Field(coerce=True, nullable=True)
    iban: Series[str] = pa.Field(coerce=True, nullable=True)
    btw_nmbr: Series[str] = pa.Field(coerce=True, nullable=True)
    ch_of_comm_nmbr: Series[str] = pa.Field(coerce=True, nullable=True)
    payment_condition: Series[str] = pa.Field(coerce=True, nullable=True)
    credit_limit: Series[float] = pa.Field(coerce=True, nullable=True)
    temp_blocked: Series[bool] = pa.Field(coerce=True)
    vat_duty: Series[str] = pa.Field(coerce=True)
    auto_payment: Series[bool] = pa.Field(coerce=True)
    blocked: Series[bool] = pa.Field(coerce=True)
    create_date: Series[str] = pa.Field(coerce=True)
    modified_date: Series[str] = pa.Field(coerce=True)

    class Config:
        coerce = True
        strict = True

class CreditorUpdateSchema(BaseModel):
    """
    Pydantic schema for creditor updates.
    This schema allows validation of both flat and nested dictionaries through field aliases.
    """
    # Required Fields
    creditor_id: str = Field(..., description="Creditor ID")

    # Base Fields
    currency: Optional[str] = Field(None, description="Currency code (e.g., EUR)")
    match_person_on: Optional[str] = Field(None, description="Value to match person with (0 to match with person_id)")

    # Base creditor fields
    is_creditor: Optional[bool] = Field(None, description="Is this a creditor")
    payment_to_external: Optional[bool] = Field(None, description="Payment to external")
    preferred_iban: Optional[str] = Field(None, description="Preferred IBAN")
    remark: Optional[str] = Field(None, description="Remark")
    payment_condition: Optional[str] = Field(None, description="Payment condition")
    collective_account: Optional[str] = Field(None, description="Collective account")
    preferred_delivery_method: Optional[str] = Field(None, description="Preferred delivery method")
    automatic_payment: Optional[bool] = Field(None, description="Automatic payment")
    compact: Optional[bool] = Field(None, description="Compact")
    payment_specification: Optional[str] = Field(None, description="Payment specification")
    preferred_provisioning: Optional[str] = Field(None, description="Preferred provisioning")

    # Person fields
    internal_id: Optional[str] = Field(None, description="Internal ID")
    person_id: Optional[str] = Field(None, description="Person ID")
    log_birthname_seperately: Optional[bool] = Field(None, description="Log birthname separately")
    postal_address_applied: Optional[bool] = Field(None, description="Postal address applied")
    auto_number: Optional[bool] = Field(None, description="Auto number")
    last_name: Optional[str] = Field(None, description="Last name")
    first_name: Optional[str] = Field(None, description="First name")
    middle_name: Optional[str] = Field(None, description="Middle name")
    gender: Optional[str] = Field(None, description="Gender")
    salutation: Optional[str] = Field(None, description="Salutation")
    correspondence: Optional[bool] = Field(None, description="Correspondence")

    # Address fields
    country: Optional[str] = Field(None, description="Country")
    address_is_postal_address: Optional[bool] = Field(None, description="Address is postal address")
    street: Optional[str] = Field(None, description="Street")
    house_number: Optional[str] = Field(None, description="House number")
    house_number_addition: Optional[str] = Field(None, description="House number addition")
    postal_code: Optional[str] = Field(None, description="Postal code")
    city: Optional[str] = Field(None, description="City")
    match_city_on_postal_code: Optional[bool] = Field(None, description="Match city on postal code")
    mailbox_address: Optional[str] = Field(None, description="Mailbox address")

    # Bank account fields
    country_of_bank: Optional[str] = Field(None, description="Country of bank")
    iban_check: Optional[bool] = Field(None, description="IBAN check")
    iban: Optional[str] = Field(None, description="IBAN")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "creditor_id": "CR123",
                "is_creditor": True,
                "preferred_iban": "NL91ABNA0417164300",
                "payment_condition": "30",
                "automatic_payment": True,
                "person_id": "P123",
                "last_name": "Doe",
                "first_name": "John",
                "gender": "M",
                "country": "Netherlands",
                "street": "Example Street",
                "house_number": "42",
                "postal_code": "1234 AB",
                "city": "Amsterdam",
                "iban": "NL91ABNA0417164300",
                "iban_check": True
            }
        }

class CreditorCreateSchema(CreditorUpdateSchema):
    """
    Pydantic schema for creditor creates.
    This schema allows validation of both flat and nested dictionaries through field aliases.
    """
    pass
