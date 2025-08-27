import pandera as pa
from pandera.typing import Series, DateTime
from pydantic import BaseModel, Field
from typing import Optional

class DebtorGetSchema(pa.DataFrameModel):
    debtor_id: Series[str] = pa.Field(coerce=True)
    debtor_name: Series[str] = pa.Field(coerce=True)
    bcco: Series[str] = pa.Field(coerce=True)
    search_name: Series[str] = pa.Field(coerce=True,nullable=True)
    address_line_1: Series[str] = pa.Field(coerce=True)
    address_line_3: Series[str] = pa.Field(coerce=True)
    address_line_4: Series[str] = pa.Field(coerce=True, nullable=True)
    tel_nmbr: Series[str] = pa.Field(coerce=True,nullable=True)
    email: Series[str] = pa.Field(coerce=True, nullable=True)
    iban: Series[str] = pa.Field(coerce=True, nullable=True)
    btw_nmbr: Series[str] = pa.Field(coerce=True, nullable=True)
    ch_of_comm_nmbr: Series[str] = pa.Field(coerce=True, nullable=True)
    collect_account: Series[str] = pa.Field(coerce=True)
    pay_con: Series[str] = pa.Field(coerce=True)
    vat_duty: Series[str] = pa.Field(coerce=True)
    blocked: Series[bool] = pa.Field(coerce=True)
    credit_limit: Series[float] = pa.Field(coerce=True)
    currency_id: Series[str] = pa.Field(coerce=True)
    auto_payment: Series[bool] = pa.Field(coerce=True)
    create_date: Series[str] = pa.Field(coerce=True)
    modified_date: Series[str] = pa.Field(coerce=True)

    class Config:
        coerce = True
        strict = True


class DebtorCreateSchema(BaseModel):
    """
    Pydantic schema for debtor creates.
    This schema allows validation of both flat and nested dictionaries through field aliases.
    """
    # Required Fields
    debtor_id: str = Field(..., description="Debtor ID")

    # Base Fields
    currency: Optional[str] = Field(None, description="Currency code (e.g., EUR)")
    internal_id: Optional[int] = Field(None, description="Internal ID for person identification")
    match_person_on: Optional[str] = Field(None, description="Value to match person with (0 to match with person_id)")

    # Personal Information (KnPerson.Element.Fields)
    person_id: Optional[str] = Field(None, alias="person.person_id", description="Person ID")
    first_name: Optional[str] = Field(None, alias="person.first_name", description="First name")
    initials: Optional[str] = Field(None, alias="person.initials", description="Initials")
    prefix: Optional[str] = Field(None, alias="person.prefix", description="Prefix")
    last_name: Optional[str] = Field(None, alias="person.last_name", description="Last name")
    nickname: Optional[str] = Field(None, alias="person.nickname", description="Nickname")
    gender: Optional[str] = Field(None, alias="person.gender", description="Gender")
    phone_private: Optional[str] = Field(None, alias="person.phone_private", description="Private phone number")
    mail_private: Optional[str] = Field(None, alias="person.mail_private", description="Private email")
    name_use: Optional[str] = Field(None, alias="person.name_use", description="Name use")
    autonumber_person: Optional[bool] = Field(None, alias="person.autonumber_person", description="Auto number person")

    # Birth and Partner Information (KnPerson.Element.Fields)
    birth_name: Optional[str] = Field(None, alias="person.birth_name", description="Birth name")
    prefix_birth_name: Optional[str] = Field(None, alias="person.prefix_birth_name", description="Prefix of birth name")
    partner_name: Optional[str] = Field(None, alias="person.partner_name", description="Partner name")
    prefix_partner_name: Optional[str] = Field(None, alias="person.prefix_partner_name", description="Prefix of partner name")
    enter_birthname_seperate: Optional[bool] = Field(None, alias="person.enter_birthname_seperate", description="Whether to enter birth name separately")

    # Address Information (KnBasicAddressAdr.Element.Fields and KnBasicAddressPad.Element.Fields)
    country: Optional[str] = Field(None, alias="address.country", description="Country")
    street: Optional[str] = Field(None, alias="address.street", description="Street")
    house_number: Optional[str] = Field(None, alias="address.house_number", description="House number")
    house_number_add: Optional[str] = Field(None, alias="address.house_number_add", description="House number addition")
    postal_code: Optional[str] = Field(None, alias="address.postal_code", description="Postal code")
    city: Optional[str] = Field(None, alias="address.city", description="City")
    mailbox_address: Optional[str] = Field(None, alias="address.mailbox_address", description="Mailbox address")
    search_address_by_postal_code: Optional[bool] = Field(None, alias="address.search_address_by_postal_code", description="Search address by postal code")

    # Debtor Specific Fields (KnSalesRelationPer.Element.Fields)
    collective_ledger_account: Optional[str] = Field(None, alias="debtor.collective_ledger_account", description="Collective ledger account")
    payment_condition: Optional[str] = Field(None, alias="debtor.payment_condition", description="Payment condition")
    send_reminder: Optional[bool] = Field(None, alias="debtor.send_reminder", description="Send reminder")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "debtor_id": "12345",
                "person": {
                    "person_id": "P123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": "M"
                },
                "address": {
                    "country": "Netherlands",
                    "street": "Example Street",
                    "house_number": "42",
                    "postal_code": "1234 AB"
                },
                "debtor": {
                    "payment_condition": "30",
                    "send_reminder": True
                }
            }
        }