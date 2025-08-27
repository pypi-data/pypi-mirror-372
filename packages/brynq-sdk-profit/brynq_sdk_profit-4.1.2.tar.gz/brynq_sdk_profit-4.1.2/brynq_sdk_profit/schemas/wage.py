import pandera as pa
from pandera.typing import Series, DateTime
from .employee import EmployeeBaseSchema
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import math
import pandas as pd

class WageComponentCreateSchema(BaseModel):
    """Pydantic schema for creating a new wage component"""
    # Required Fields
    parameter: str = Field(..., description="Parameter for the wage component")
    id: int = Field(..., description="id")
    employee_id: str = Field(..., description="Employee id")
    start_date: datetime = Field(..., description="Start date of the wage component")
    value: float = Field(..., description="Value of the wage component")

    # Optional Fields
    end_date: Optional[datetime] = Field(None, description="End date of the wage component")
    contract_no: Optional[str] = Field(None, description="Contract number")
    apply_type: Optional[str] = Field(None, description="Type of application")


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "parameter": "SALARY",
                "employee_id": "EMP123",
                "start_date": "2025-01-01T00:00:00",
                "value": 4000.00,
                "contract_no": "CNT456",
                "apply_type": "monthly"
            }
        }
class WageComponentUpdateSchema(WageComponentCreateSchema):
    """Pydantic schema for updating a wage component"""
class WageComponentGetSchema(EmployeeBaseSchema):
    wage_component_id: Series[int] = pa.Field(coerce=True, nullable=True)
    parameter: Series[int] = pa.Field(coerce=True, nullable=False)
    start_date: Series[DateTime] = pa.Field(coerce=True, nullable=False)
    value: Series[float] = pa.Field(coerce=True, nullable=True)
    booked_by: Series[str] = pa.Field(coerce=True, nullable=False)
    end_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)


class WageMutationGetSchema(pa.DataFrameModel):
    employee_id: Series[str] = pa.Field(coerce=True, nullable=True)
    guid: Series[str] = pa.Field(coerce=True, nullable=False)
    year: Series[int] = pa.Field(coerce=True, nullable=False)
    month: Series[int] = pa.Field(coerce=True, nullable=False)
    date: Series[DateTime] = pa.Field(coerce=True, nullable=False)
    booked_by: Series[str] = pa.Field(coerce=True, nullable=False)
    wage_component_id: Series[str] = pa.Field(coerce=True, nullable=True)
    value: Series[float] = pa.Field(coerce=True, nullable=True)
    description: Series[str] = pa.Field(coerce=True, nullable=True)


    class Config:
        coerce = True
        strict = True
class WageMutationCreateSchema(BaseModel):
    """Pydantic schema for creating a new wage mutation"""
    # Required Fields
    employee_id: str = Field(..., description="Employee ID")
    year: int = Field(..., description="Year of the mutation")
    month: int = Field(..., description="Month of the mutation")
    employer_nmbr: str = Field(..., description="Employer number")
    wage_component_id: int = Field(..., description="Wage component ID")
    value: float = Field(..., description="Value of the mutation")
    percentage: float = Field(None, description="Percentage of the mutation")

    # Optional Fields
    period_table: Optional[str] = Field(None, description="Period table")


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee_id": "EMP123",
                "year": 2025,
                "month": 1,
                "employer_nmbr": "EMP001",
                "wage_component_id": 456,
                "value": 1000.00,
                "period_table": "PT2025"
            }
        }
class WageMutationUpdateSchema(BaseModel):
    """Pydantic schema for updating a wage mutation"""
    # Required Fields
    guid: str = Field(..., description="Unique identifier of the mutation")
    employee_id: str = Field(..., description="Employee ID")
    year: int = Field(..., description="Year of the mutation")
    month: str = Field(..., description="Month of the mutation")
    employer_nmbr: str = Field(..., description="Employer number")
    wage_component_id: int = Field(..., description="Wage component ID")
    value: float = Field(..., description="Value of the mutation")
    percentage: float = Field(None, description="Percentage of the mutation")

    # Optional Fields
    period_table: Optional[str] = Field(None, description="Period table")
    date: Optional[str] = Field(None, description="Date of the mutation")


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "guid": "WM123",
                "employee_id": "EMP123",
                "year": 2025,
                "month": "01",
                "employer_nmbr": "EMP001",
                "wage_component_id": 456,
                "value": "1200.00",
                "date": "2025-01-15"
            }
        }

class WageComponentSchema(EmployeeBaseSchema):
    parameter: Series[str] = pa.Field(coerce=True, nullable=False)
    id: Series[str] = pa.Field(coerce=True, nullable=False)
    start_date: Series[DateTime] = pa.Field(coerce=True, nullable=False)
    value: Series[float] = pa.Field(coerce=True, nullable=False)
    end_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    contract_no: Series[str] = pa.Field(coerce=True, nullable=True)
    apply_type: Series[str] = pa.Field(coerce=True, nullable=True)
