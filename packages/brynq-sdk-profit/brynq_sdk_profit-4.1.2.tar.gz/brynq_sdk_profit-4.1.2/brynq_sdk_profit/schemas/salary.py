import pandas as pd
import pandera as pa
from pandera.typing import Series, DateTime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import math


class SalaryCreateSchema(BaseModel):
    """Pydantic schema for creating a new salary record"""
    # Required Fields
    start_date_salary: Optional[datetime] = Field(None, description="Start date of the salary")
    employee_id: str = Field(..., description="Employee ID")
    salary_type: str = Field(..., description="Type of salary")

    # Optional Fields
    step: Optional[int] = Field(None, description="Salary step")
    period_table: Optional[str] = Field(None, description="Period table")
    salary_year: Optional[datetime] = Field(None, description="Salary year")
    salary_year_amount: Optional[float] = Field(None, description="Yearly salary amount")
    salary_amount: Optional[float] = Field(None, description="Salary amount")
    net_salary: Optional[float] = Field(None, description="Whether the salary is net")
    function_scale: Optional[str] = Field(None, description="Function scale")
    function_scale_type: Optional[str] = Field(None, description="Function scale type")
    salary_scale: Optional[str] = Field(None, description="Salary scale")
    salary_scale_type: Optional[str] = Field(None, description="Salary scale type")
    apply_timetable: Optional[bool] = Field(None, description="Whether to apply timetable")
    employment_number: Optional[str] = Field(None, description="Employment number")


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee_id": "EMP123",
                "startdate_salary": "2025-01-01T00:00:00",
                "salary_type": "monthly",
                "step": 3,
                "salary_amount": 4000.00,
                "salary_year_amount": 48000.00,
                "net_salary": False,
                "function_scale": "B3",
                "function_scale_type": "standard",
                "salary_scale": "S8",
                "employment_number": "123456",
                "apply_timetable": True
            }
        }


class SalaryUpdateSchema(BaseModel):
    """Pydantic schema for updating a salary record"""
    # Required Fields
    employee_id: str = Field(..., description="Employee ID of the salary record")

    # Optional Fields
    start_date_salary: Optional[datetime] = Field(None, description="Start date of the salary")
    salary_type: Optional[str] = Field(None, description="Type of salary (U=Hourly wage, V=Fixed salary, S=Scale salary, Su=Scale hourly wage)")
    period_table: Optional[str] = Field("5", description="Period table (default: 5)")
    step: Optional[int] = Field(None, description="Salary step")
    salary_year: Optional[datetime] = Field(None, description="Salary year")
    salary_year_amount: Optional[float] = Field(None, description="Yearly salary amount")
    salary_amount: Optional[float] = Field(None, description="Salary amount")
    net_salary: Optional[float] = Field(None, description="Whether the salary is net")
    function_scale: Optional[str] = Field(None, description="Function scale")
    function_scale_type: Optional[str] = Field(None, description="Function scale type")
    salary_scale: Optional[str] = Field(None, description="Salary scale")
    salary_scale_type: Optional[str] = Field(None, description="Salary scale type")
    apply_timetable: Optional[bool] = Field(None, description="Whether to apply timetable")
    employment_number: Optional[str] = Field(None, description="Employment number")


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "salary_id": "SAL123",
                "salary_amount": 4500.00,
                "salary_year_amount": 54000.00,
                "step": 4,
                "function_scale": "B4"
            }
        }

class BaseSalarySchema(pa.DataFrameModel):
    """Base schema for salary-related operations in Pandera DataFrame format.

    This schema defines the minimum required fields for any salary operation.
    Use this as a base class for other salary-related DataFrame schemas.
    """
    startdate_salary: Series[DateTime] = pa.Field(coerce=True, nullable=False)
    employee_id: Series[str] = pa.Field(coerce=True, nullable=False)
    salary_type: Series[str] = pa.Field(coerce=True, nullable=False)

class SalaryGetSchema(pa.DataFrameModel):
    """Schema for retrieving salary information in DataFrame format.

    This schema defines the structure for salary data retrieval operations,
    including both employee and employer information along with salary details.
    """
    salary_id: Series[str] = pa.Field(coerce=True)
    type_of_salary: Series[str] = pa.Field(coerce=True)
    employer_id: Series[str] = pa.Field(coerce=True)
    employee_id: Series[str] = pa.Field(coerce=True)
    name: Series[str] = pa.Field(coerce=True)
    start_date: Series[DateTime] = pa.Field(coerce=True)
    salary: Series[int] = pa.Field(coerce=True)
    employer_name: Series[str] = pa.Field(coerce=True)

    class Config:
        coerce = True
        strict = True
