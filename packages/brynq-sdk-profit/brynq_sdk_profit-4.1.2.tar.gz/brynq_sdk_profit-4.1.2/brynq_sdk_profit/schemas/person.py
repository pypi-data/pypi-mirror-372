import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import math

class PersonBaseSchema(pa.DataFrameModel):
    person_id: Series[str] = pa.Field(coerce=True, nullable=False)

class PersonGetSchema(pa.DataFrameModel):
    nmbr: Series[str] = pa.Field(coerce=True)
    description: Series[str] = pa.Field(coerce=True)
    name: Series[str] = pa.Field(coerce=True)
    sales_amount_period: Series[float] = pa.Field(coerce=True, nullable=True)
    sales_amount_till_period: Series[float] = pa.Field(coerce=True, nullable=True)
    blocked: Series[bool] = pa.Field(coerce=True)

    class Config:
        coerce = True
        strict = True

class PersonUpdateSchema(BaseModel):
    """Pydantic schema for updating a person's information with flat structure support"""
    # Required Fields
    person_id: str = Field(..., description="Person ID")


        # System Fields (optional with defaults)
    auto_number: Optional[bool] = Field(True, description="Whether to auto-generate number")
    match_person: Optional[str] = Field("7", description="Match person value for creation")
    contact_role: Optional[str] = Field("Sollicitant", description="Default contact role")

    # System Fields (optional)
    match_person: Optional[str] = Field(None, description="Match person value for updates")
    nationality: Optional[str] = Field(None, description="Nationality code (e.g., 'NL' for Netherlands)")

    # Personal Information (all optional for updates)
    first_name: Optional[str] = Field(None, alias="personal.first_name", description="First name")
    last_name: Optional[str] = Field(None, alias="personal.last_name", description="Last name")
    initials: Optional[str] = Field(None, alias="personal.initials", description="Initials")
    prefix: Optional[str] = Field(None, alias="personal.prefix", description="Name prefix")
    nickname: Optional[str] = Field(None, alias="personal.nickname", description="Nickname")
    birth_name: Optional[str] = Field(None, alias="personal.birth_name", description="Birth name")
    birth_name_separate: Optional[str] = Field(None, alias="personal.birth_name_separate", description="Birth name separate")
    prefix_birth_name: Optional[str] = Field(None, alias="personal.prefix_birth_name", description="Prefix of birth name")
    birth_date: Optional[datetime] = Field(None, alias="personal.birth_date", description="Date of birth")
    country_of_birth: Optional[str] = Field(None, alias="personal.country_of_birth", description="Country of birth")
    city_of_birth: Optional[str] = Field(None, alias="personal.city_of_birth", description="City of birth")
    gender: Optional[str] = Field(None, alias="personal.gender", description="Gender")
    ssn: Optional[str] = Field(None, alias="personal.ssn", description="Social Security Number")
    bsn: Optional[str] = Field(None, alias="personal.bsn", description="BSN number")

    # Partner Information
    birthname_partner: Optional[str] = Field(None, alias="partner.birth_name", description="Birth name of partner")
    prefix_birthname_partner: Optional[str] = Field(None, alias="partner.prefix_birth_name", description="Prefix of partner's birth name")

    # Marital Information
    marital_status: Optional[str] = Field(None, alias="marital.status", description="Marital status")
    date_of_marriage: Optional[datetime] = Field(None, alias="marital.date_of_marriage", description="Date of marriage")
    date_of_divorce: Optional[datetime] = Field(None, alias="marital.date_of_divorce", description="Date of divorce")

    # Contact Information - Work
    mail_work: Optional[str] = Field(None, alias="contact.work.email", description="Work email")
    mobile_work: Optional[str] = Field(None, alias="contact.work.mobile", description="Work mobile number")
    phone_work: Optional[str] = Field(None, alias="contact.work.phone", description="Work phone number")

    # Contact Information - Private
    mail_private: Optional[str] = Field(None, alias="contact.private.email", description="Private email")
    mobile_private: Optional[str] = Field(None, alias="contact.private.mobile", description="Private mobile number")
    phone_private: Optional[str] = Field(None, alias="contact.private.phone", description="Private phone number")

    # Additional Information
    name_use: Optional[str] = Field(None, alias="preferences.name_use", description="Name use preference")
    match_person_on: Optional[str] = Field(None, alias="preferences.match_person_on", description="Match person on")


    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "person_id": "PERSON123",
                "first_name": "John",
                "last_name": "Doe",
                "birth_date": "1990-01-01T00:00:00",
                "gender": "M",
                "nationality": "Dutch",
                "bsn": "123456789",
                "marital_status": "married",
                "date_of_marriage": "2020-06-15T00:00:00",
                "mail_work": "john.doe@company.com",
                "phone_work": "+31612345678"
            }
        }

class PersonCreateSchema(PersonUpdateSchema):
    """Pydantic schema for creating a new person with flat structure support"""
    # Override person_id as optional for creation
    person_id: Optional[str] = None
