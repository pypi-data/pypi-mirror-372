import pandera as pa
from pandera.typing import Series, DateTime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import math



class EmployeeBaseSchema(pa.DataFrameModel):
    employee_id: Series[str] = pa.Field(coerce=True, nullable=False)

class EmployeeGetSchema(EmployeeBaseSchema):
    # Required Fields
    employee_id: Series[str] = pa.Field(coerce=True, nullable=False)
    person_id: Series[str] = pa.Field(coerce=True, nullable=False)
    gender: Series[str] = pa.Field(coerce=True, nullable=False)
    first_name: Series[str] = pa.Field(coerce=True, nullable=False)
    last_name: Series[str] = pa.Field(coerce=True, nullable=False)
    employer_number: Series[str] = pa.Field(coerce=True, nullable=True)
    prefix_birth_name: Series[str] = pa.Field(coerce=True, nullable=True)
    birth_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    nationality: Series[str] = pa.Field(coerce=True, nullable=True)
    ssn: Series[str] = pa.Field(coerce=True, nullable=True)
    title: Series[str] = pa.Field(coerce=True, nullable=True)
    phone_work: Series[str] = pa.Field(coerce=True, nullable=True)
    mail_work: Series[str] = pa.Field(coerce=True, nullable=True)
    street: Series[str] = pa.Field(coerce=True, nullable=True)
    state: Series[str] = pa.Field(coerce=True, nullable=True)
    street_number: Series[str] = pa.Field(coerce=True, nullable=True)
    street_number_add: Series[str] = pa.Field(coerce=True, nullable=True)
    postal_code: Series[str] = pa.Field(coerce=True, nullable=True)
    city: Series[str] = pa.Field(coerce=True, nullable=True)
    country: Series[str] = pa.Field(coerce=True, nullable=True)
    function_start_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    function: Series[str] = pa.Field(coerce=True, nullable=True)
    organisational_unit: Series[str] = pa.Field(coerce=True, nullable=True)
    supervisor_id: Series[str] = pa.Field(coerce=True, nullable=True)
    cost_center: Series[str] = pa.Field(coerce=True, nullable=True)
    work_schedule_valid_from: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    days_per_week: Series[float] = pa.Field(coerce=True, nullable=True)
    weekly_hours: Series[float] = pa.Field(coerce=True, nullable=True)
    contract_start_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    end_date_contract: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    type_of_contract: Series[str] = pa.Field(coerce=True, nullable=True)
    type_of_employee: Series[str] = pa.Field(coerce=True, nullable=True)
    probation_end_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    termination_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    termination_reason: Series[str] = pa.Field(coerce=True, nullable=True)
    salary_amount: Series[float] = pa.Field(coerce=True, nullable=True)
    salary_type: Series[str] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True

class EmployeeCreateSchema(BaseModel):
    """Pydantic schema for creating a new employee with flat structure support"""
    # System Fields
    employment_status: Optional[str] = Field(None, description="Employment status (default: I)")
    blocked: Optional[str] = Field(None, description="Blocked status (default: 0)")
    different_language: Optional[str] = Field(None, description="Language ID (default: 001)")
    person_id: Optional[str] = Field(None, description="Person ID")
    postal_address_applied: Optional[str] = Field(None, description="Postal address applied (default: 1)")
    auto_number: Optional[str] = Field(None, description="Auto number setting (default: 0)")
    match_person: Optional[str] = Field(None, description="Match person value (default: 7)")
    birth_name_seperate: Optional[str] = Field(None, description="Birth name separate setting (default: 1)")
    name_usage: Optional[str] = Field(None, description="Name usage setting (default: 0)")
    salutation: Optional[str] = Field(None, description="Salutation/Title")

    # Personal Information
    employee_id: str = Field(..., alias="employee.id", description="First name")
    first_name: str = Field(..., alias="employee.first_name", description="First name")
    last_name: str = Field(..., alias="employee.last_name", description="Last name")
    gender: Optional[str] = Field(None, alias="employee.gender", description="Gender")
    birth_date: Optional[datetime] = Field(None, alias="employee.birth_date", description="Date of birth")
    initials: Optional[str] = Field(None, alias="employee.initials", description="Initials")
    prefix: Optional[str] = Field(None, alias="employee.prefix", description="Name prefix")
    nickname: Optional[str] = Field(None, alias="employee.nickname", description="Nickname")
    birth_name: Optional[str] = Field(None, alias="employee.birth_name", description="Birth name")
    prefix_birth_name: Optional[str] = Field(None, alias="employee.prefix_birth_name", description="Prefix of birth name")
    nationality: Optional[str] = Field(None, alias="employee.nationality", description="Nationality")
    ssn: Optional[str] = Field(None, alias="employee.ssn", description="Social Security Number")

    # Address Information
    street: str = Field(..., alias="address.street", description="Street name")
    street_number: Optional[str] = Field(None, alias="address.street_number", description="Street number")
    street_number_add: Optional[str] = Field(None, alias="address.street_number_add", description="Street number addition")
    postal_code: str = Field(..., alias="address.postal_code", description="Postal code")
    city: str = Field(..., alias="address.city", description="City")
    state: Optional[str] = Field(None, alias="address.state", description="State")
    country: str = Field(..., alias="address.country", description="Country")
    city_of_birth: Optional[str] = Field(None, alias="address.city_of_birth", description="City of birth")
    country_of_birth: Optional[str] = Field(None, alias="address.country_of_birth", description="Country of birth")

    # Contact Information
    phone_work: Optional[str] = Field(None, alias="contact.phone_work", description="Work phone number")
    mail_work: Optional[str] = Field(None, alias="contact.mail_work", description="Work email")

    # Marital Information
    marital_status: Optional[str] = Field(None, alias="marital.marital_status", description="Marital status")
    date_of_marriage: Optional[datetime] = Field(None, alias="marital.date_of_marriage", description="Date of marriage")
    date_of_divorce: Optional[datetime] = Field(None, alias="marital.date_of_divorce", description="Date of divorce")
    birthname_partner: Optional[str] = Field(None, alias="marital.birthname_partner", description="Birth name of partner")
    prefix_birthname_partner: Optional[str] = Field(None, alias="marital.prefix_birthname_partner", description="Prefix of partner's birth name")

    # Other Information
    work_start_date: Optional[datetime] = Field(None, description="Work start date")


    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee": {
                    "id": "EMP001",
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": "M",
                    "birth_date": "1990-01-01T00:00:00",
                    "initials": "JD",
                    "prefix": "Mr",
                    "nickname": "Johnny",
                    "birth_name": "John Smith",
                    "prefix_birth_name": "Mr",
                    "nationality": "American",
                    "ssn": "123-45-6789"
                },
                "address": {
                    "street": "Main Street",
                    "street_number": "123",
                    "street_number_add": "A",
                    "postal_code": "12345",
                    "city": "Example City",
                    "state": "Example State",
                    "country": "Example Country",
                    "city_of_birth": "Birth City",
                    "country_of_birth": "Birth Country"
                },
                "contact": {
                    "phone_work": "+1234567890",
                    "mail_work": "john.doe@example.com"
                },
                "marital": {
                    "marital_status": "married",
                    "date_of_marriage": "2020-06-15T00:00:00",
                    "date_of_divorce": None,
                    "birthname_partner": "Jane Smith",
                    "prefix_birthname_partner": "Ms"
                },
                "work_start_date": "2025-01-01T00:00:00"
            }
        }


class EmployeeTerminateSchema(BaseModel):
    """Pydantic schema for terminating an employee"""
    employee_id: str = Field(..., description="Employee ID")
    termination_date: datetime = Field(..., description="Termination date")
    end_date_contract: datetime = Field(..., description="Contract end date")
    start_date_contract: datetime = Field(..., description="Contract start date")
    termination_initiative: Optional[str] = Field(None, description="Termination initiative")
    termination_reason: Optional[str] = Field(None, description="Reason for termination")

    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee_id": "EMP123",
                "termination_date": "2025-12-31T00:00:00",
                "end_date_contract": "2025-12-31T00:00:00",
                "start_date_contract": "2025-01-01T00:00:00",
                "termination_initiative": "Employee",
                "termination_reason": "Resignation"
            }
        }


class EmployeeUpdateSchema(BaseModel):
    """Pydantic schema for updating an employee with flat structure support"""
    # Employee ID (required)
    employee_id: str = Field(..., description="Employee ID")

    # Personal Information (all optional for updates)
    first_name: Optional[str] = Field(None, alias="personal.first_name", description="First name")
    last_name: Optional[str] = Field(None, alias="personal.last_name", description="Last name")
    gender: Optional[str] = Field(None, alias="personal.gender", description="Gender")
    birth_date: Optional[datetime] = Field(None, alias="personal.birth_date", description="Date of birth")
    initials: Optional[str] = Field(None, alias="personal.initials", description="Initials")
    prefix: Optional[str] = Field(None, alias="personal.prefix", description="Name prefix")
    nickname: Optional[str] = Field(None, alias="personal.nickname", description="Nickname")
    birth_name: Optional[str] = Field(None, alias="personal.birth_name", description="Birth name")
    prefix_birth_name: Optional[str] = Field(None, alias="personal.prefix_birth_name", description="Prefix of birth name")
    nationality: Optional[str] = Field(None, alias="personal.nationality", description="Nationality")
    ssn: Optional[str] = Field(None, alias="personal.ssn", description="Social Security Number")

    # Address Information (all optional for updates)
    street: Optional[str] = Field(None, alias="address.street", description="Street name")
    street_number: Optional[str] = Field(None, alias="address.street_number", description="Street number")
    street_number_add: Optional[str] = Field(None, alias="address.street_number_add", description="Street number addition")
    postal_code: Optional[str] = Field(None, alias="address.postal_code", description="Postal code")
    city: Optional[str] = Field(None, alias="address.city", description="City")
    state: Optional[str] = Field(None, alias="address.state", description="State")
    country: Optional[str] = Field(None, alias="address.country", description="Country")
    city_of_birth: Optional[str] = Field(None, alias="address.city_of_birth", description="City of birth")
    country_of_birth: Optional[str] = Field(None, alias="address.country_of_birth", description="Country of birth")

    # Contact Information (all optional for updates)
    phone_work: Optional[str] = Field(None, alias="contact.phone_work", description="Work phone number")
    mail_work: Optional[str] = Field(None, alias="contact.mail_work", description="Work email")

    # Marital Information (all optional for updates)
    marital_status: Optional[str] = Field(None, alias="marital.marital_status", description="Marital status")
    date_of_marriage: Optional[datetime] = Field(None, alias="marital.date_of_marriage", description="Date of marriage")
    date_of_divorce: Optional[datetime] = Field(None, alias="marital.date_of_divorce", description="Date of divorce")
    birthname_partner: Optional[str] = Field(None, alias="marital.birthname_partner", description="Birth name of partner")
    prefix_birthname_partner: Optional[str] = Field(None, alias="marital.prefix_birthname_partner", description="Prefix of partner's birth name")


    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee_id": "EMP123",
                "first_name": "John",
                "last_name": "Doe",
                "phone_work": "+1234567890",
                "mail_work": "john.doe@example.com",
                "street": "New Street",
                "city": "New City"
            }
        }
