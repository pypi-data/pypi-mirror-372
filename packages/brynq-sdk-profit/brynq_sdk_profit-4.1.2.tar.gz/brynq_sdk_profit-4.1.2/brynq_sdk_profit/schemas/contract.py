import pandera as pa
from pandera.typing import Series, DateTime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import math

from .employee import EmployeeBaseSchema


work_schedule_columns = [
    'actual_working_pattern_days_monday',
    'actual_working_pattern_days_tuesday',
    'actual_working_pattern_days_wednesday',
    'actual_working_pattern_days_thursday',
    'actual_working_pattern_days_friday',
    'actual_working_pattern_days_saturday',
    'actual_working_pattern_days_sunday'
]

class ContractComponentSchema(EmployeeBaseSchema):
    # Required Fields
    start_date_contract: Series[DateTime] = pa.Field(coerce=True, nullable=False)

    # Optional Fields
    type_of_employment: Series[str] = pa.Field(coerce=True, nullable=True)
    end_date_contract: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    termination_reason: Series[str] = pa.Field(coerce=True, nullable=True)
    termination_initiative: Series[str] = pa.Field(coerce=True, nullable=True)
    probation_period: Series[str] = pa.Field(coerce=True, nullable=True)
    probation_enddate: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    cao: Series[str] = pa.Field(coerce=True, nullable=True)
    terms_of_employment: Series[str] = pa.Field(coerce=True, nullable=True)
    type_of_contract: Series[str] = pa.Field(coerce=True, nullable=False)
    employer_nmbr: Series[str] = pa.Field(coerce=True, nullable=True)
    type_of_employee: Series[str] = pa.Field(coerce=True, nullable=True)
    employment: Series[str] = pa.Field(coerce=True, nullable=True)
    seniority_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    contract_chain_code: Series[str] = pa.Field(coerce=True, nullable=True)
    start_date_contract_chain: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    date_in_service_original: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    number_income_ratio: Series[str] = pa.Field(coerce=True, nullable=True)

class ContractGetSchema(pa.DataFrameModel):
    employee_id: Series[str] = pa.Field(coerce=True)  # Employee ID
    name: Series[str] = pa.Field(coerce=True)  # Employee Name
    description: Series[str] = pa.Field(coerce=True)  # Description
    date_in_service: Series[str] = pa.Field(coerce=True)  # Start Date
    date_off_service: Series[str] = pa.Field(coerce=True, nullable=True)  # End Date

    class Config:
        coerce = True
        strict = True

# class RehireSalaryComponentSchema(pa.DataFrameModel):
#     function_scale_type: Series[str] = pa.Field(coerce=True, nullable=True)
#     salary_scale_type: Series[str] = pa.Field(coerce=True, nullable=True)

class ContractRehireSchema(pa.DataFrameModel):
    salary: Series[str] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = False

class ContractUpdateSchema(BaseModel):
    """Pydantic schema for contract updates.
    This schema allows validation of both flat and nested dictionaries through field aliases.
    """
    # Employee Fields
    employee_id: str = Field(..., description="Employee ID")

    # Function Component Fields (from FunctionComponentSchema)
    organizational_unit: str = Field(..., alias="function.organizational_unit", description="Organizational unit")
    function_id: str = Field(..., alias="function.function_id", description="Function ID")
    cost_center_id: str = Field(..., alias="function.cost_center_id", description="Cost center ID")
    cost_carrier_id: Optional[str] = Field(None, alias="function.costcarrier_id", description="Cost carrier ID")
    function_start_date: Optional[datetime] = Field(None, alias="function.start_date", description="Start date")

    # Contract Component Fields (from ContractComponentSchema)
    start_date_contract: datetime = Field(..., alias="contract.start_date_contract", description="Contract start date")
    type_of_contract: str = Field(..., alias="contract.type_of_contract", description="Type of contract")
    type_of_employment: Optional[str] = Field(None, alias="contract.type_of_employment", description="Type of employment")
    end_date_contract: Optional[datetime] = Field(None, alias="contract.end_date_contract", description="Contract end date")
    termination_reason: Optional[str] = Field(None, alias="contract.termination_reason", description="Termination reason")
    termination_initiative: Optional[str] = Field(None, alias="contract.termination_initiative", description="Termination initiative")
    probation_period: Optional[str] = Field(None, alias="contract.probation_period", description="Probation period")
    probation_end_date: Optional[datetime] = Field(None, alias="contract.probation_enddate", description="Probation end date")
    cao: Optional[str] = Field(None, alias="contract.cao", description="CAO")
    terms_of_employment: Optional[str] = Field(None, alias="contract.terms_of_employment", description="Terms of employment")
    employer_nmbr: Optional[str] = Field(None, alias="contract.employer_nmbr", description="Employer number")
    type_of_employee: Optional[str] = Field(None, alias="contract.type_of_employee", description="Type of employee")
    employment: Optional[str] = Field(None, alias="contract.employment", description="Employment")
    seniority_date: Optional[datetime] = Field(None, alias="contract.seniority_date", description="Seniority date")
    contract_chain_code: Optional[str] = Field(None, alias="contract.contract_chain_code", description="Contract chain code")
    start_date_contract_chain: Optional[datetime] = Field(None, alias="contract.start_date_contract_chain", description="Contract chain start date")
    date_in_service_original: Optional[datetime] = Field(None, alias="contract.date_in_service_original", description="Original service start date")
    number_income_ratio: Optional[str] = Field(None, alias="contract.number_income_ratio", description="Income ratio number")

    # Schedule Fields
    weekly_hours: Optional[int] = Field(None, alias="schedule.weekly_hours", description="Weekly working hours")
    part_time_percentage: int = Field(..., alias="schedule.part_time_percentage", description="Part-time percentage")
    changing_work_pattern: Optional[bool] = Field(None, alias="schedule.changing_work_pattern", description="Whether the work pattern is changing (StPa)")
    monday: Optional[float] = Field(None, alias="schedule.working_pattern.monday", description="Monday hours")
    tuesday: Optional[float] = Field(None, alias="schedule.working_pattern.tuesday", description="Tuesday hours")
    wednesday: Optional[float] = Field(None, alias="schedule.working_pattern.wednesday", description="Wednesday hours")
    thursday: Optional[float] = Field(None, alias="schedule.working_pattern.thursday", description="Thursday hours")
    friday: Optional[float] = Field(None, alias="schedule.working_pattern.friday", description="Friday hours")
    saturday: Optional[float] = Field(None, alias="schedule.working_pattern.saturday", description="Saturday hours")
    sunday: Optional[float] = Field(None, alias="schedule.working_pattern.sunday", description="Sunday hours")

    # Salary Fields
    salary_type: Optional[str] = Field(..., alias="salary.type_of_salary", description="Type of salary")
    salary_year_amount: float = Field(..., alias="salary.salary_year_amount", description="Yearly salary amount")
    period_table: int = Field(..., alias="salary.period_table", description="Period table")


    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee_id": "12345",
                "function": {
                    "organizational_unit": "DEPT123",
                    "function_id": "FUNC456",
                    "cost_center_id": "CC789",
                    "costcarrier_id": "CCR123",
                    "start_date": "2025-01-01T00:00:00"
                },
                "contract": {
                    "start_date_contract": "2025-01-01T00:00:00",
                    "type_of_contract": "Permanent",
                    "type_of_employment": "Full-time",
                    "cao": "Example CAO",
                    "terms_of_employment": "Standard",
                    "employer_nmbr": "EMP001",
                    "type_of_employee": "Regular",
                    "seniority_date": "2025-01-01T00:00:00"
                },
                "schedule": {
                    "weekly_hours": 40,
                    "part_time_percentage": 100,
                    "working_pattern": {
                        "monday": 8.0,
                        "tuesday": 8.0,
                        "wednesday": 8.0,
                        "thursday": 8.0,
                        "friday": 8.0
                    }
                },
                "salary": {
                    "type_of_salary": "Monthly",
                    "salary_year_amount": 50000,
                    "period_table": 12
                }
            }
        }
