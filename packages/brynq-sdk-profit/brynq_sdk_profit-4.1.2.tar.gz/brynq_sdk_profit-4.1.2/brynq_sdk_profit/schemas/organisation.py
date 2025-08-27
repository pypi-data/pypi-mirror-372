import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field
from typing import Optional

class OrganisationGetSchema(pa.DataFrameModel):
    employer: Series[str] = pa.Field(coerce=True)
    name: Series[str] = pa.Field(coerce=True)
    description: Series[str] = pa.Field(coerce=True)
    start_date_change: Series[str] = pa.Field(coerce=True)


class OrganisationUpdateSchema(BaseModel):
    """
    Pydantic schema for organization updates.
    This schema allows validation of both flat and nested dictionaries through field aliases.
    """
    # Required Fields
    organisation_id: str = Field(..., alias="organisation.id", description="Organization ID")
    name: str = Field(..., alias="organisation.name", description="Organization name")
    blocked: bool = Field(..., alias="organisation.blocked", description="Blocked status")

    # System Fields
    match_organisation: Optional[str] = Field("0", alias="organisation.match_organisation", description="Match organization setting (default: 0)")
    organisation_id: Optional[int] = Field(1, alias="organisation.organisation_id", description="Business relation ID (default: 1)")

    # Business Information
    collective_ledger_account: Optional[str] = Field(None, alias="business.collective_ledger_account", description="Collective ledger account")
    search_name: Optional[str] = Field(None, alias="business.search_name", description="Search name")
    kvk_number: Optional[str] = Field(None, alias="business.chamber_of_commerce", description="Chamber of Commerce number")
    vat_number: Optional[str] = Field(None, alias="business.vat_number", description="VAT number")
    status: Optional[str] = Field(None, alias="business.status", description="Status")

    # Contact Information
    phone_number_work: Optional[str] = Field(None, alias="contact.phone.work", description="Work phone number")
    email_work: Optional[str] = Field(None, alias="contact.email.work", description="Work email")

    # Address Information
    mailbox_address: Optional[str] = Field(None, alias="address.mailbox", description="Mailbox address")
    country: Optional[str] = Field(None, alias="address.country", description="Country")
    street: Optional[str] = Field(None, alias="address.street", description="Street")
    housenumber: Optional[str] = Field(None, alias="address.house_number", description="House number")
    housenumber_add: Optional[str] = Field(None, alias="address.house_number_addition", description="House number addition")
    zipcode: Optional[str] = Field(None, alias="address.zipcode", description="Zip code")
    residence: Optional[str] = Field(None, alias="address.residence", description="Residence")
    search_living_place_by_zipcode: Optional[bool] = Field(None, alias="address.search_by_zipcode", description="Search living place by zip code")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "organisation": {
                    "id": "ORG123",
                    "name": "Example Organization",
                    "blocked": False
                },
                "business": {
                    "search_name": "Example Org",
                    "chamber_of_commerce": "12345678",
                    "vat_number": "NL123456789B01",
                    "collective_ledger_account": "CLA001",
                    "status": "Active"
                },
                "contact": {
                    "phone": {
                        "work": "+31612345678"
                    },
                    "email": {
                        "work": "contact@example.org"
                    }
                },
                "address": {
                    "street": "Example Street",
                    "house_number": "42",
                    "house_number_addition": "A",
                    "zipcode": "1234 AB",
                    "country": "Netherlands",
                    "residence": "Amsterdam",
                    "mailbox": "P.O. Box 123",
                    "search_by_zipcode": True
                }
            }
        }

class OrganisationCreateSchema(OrganisationUpdateSchema):
    pass


from pydantic import BaseModel, Field
from typing import Optional

class OrganisationalUnitUpdateSchema(BaseModel):
    """
    Pydantic schema for organizational unit updates.
    """
    # Required Fields
    organisational_unit_id: str = Field(description="Unique identifier for the organizational unit")
    organisational_unit_description: str = Field(description="Description of the organizational unit")
    organisational_unit_type_id: str = Field(description="Type identifier for the organizational unit")
    staff: bool = Field(description="Indicates if the unit has staff")
    contains_employees: bool = Field(description="Indicates if the unit contains employees")
    reports_to_unit_above: str = Field(description="Indicates if the unit reports to a unit above")

    # Optional Fields
    reporting_unit: Optional[str] = Field(None, description="Unit this organizational unit reports to")
    manager: Optional[str] = Field(None, description="Manager of the organizational unit")
    cockpit_1: Optional[str] = Field(None, description="Cockpit field 1")
    cockpit_2: Optional[str] = Field(None, description="Cockpit field 2")
    cockpit_3: Optional[str] = Field(None, description="Cockpit field 3")
    cockpit_4: Optional[str] = Field(None, description="Cockpit field 4")
    cockpit_5: Optional[str] = Field(None, description="Cockpit field 5")

    class Config:
        from_attributes = True

class OrganisationalUnitCreateSchema(OrganisationalUnitUpdateSchema):
    pass
