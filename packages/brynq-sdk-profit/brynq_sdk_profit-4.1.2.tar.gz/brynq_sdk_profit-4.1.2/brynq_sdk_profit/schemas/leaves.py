from wsgiref.handlers import format_date_time

import pandas as pd
import pandera as pa
from pandera.typing import Series, DateTime
from .employee import EmployeeBaseSchema
from .date import DateBaseSchema
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import math



class LeaveGetSchema(pa.DataFrameModel):
    leave_id: Series[int] = pa.Field(coerce=True)
    employee_id: Series[str] = pa.Field(coerce=True)
    name: Series[str] = pa.Field(coerce=True)
    bsn: Series[str] = pa.Field(coerce=True,nullable=True)
    export: Series[bool] = pa.Field(coerce=True)
    hours: Series[int] = pa.Field(coerce=True)
    start_date: Series[DateTime] = pa.Field(coerce=True)
    end_date: Series[DateTime] = pa.Field(coerce=True)
    dv_id: Series[int] = pa.Field(coerce=True)
    modified_date: Series[str] = pa.Field(coerce=True)
    leave_code: Series[str] = pa.Field(coerce=True)
    leave_desc: Series[str] = pa.Field(coerce=True)
    reason_code: Series[str] = pa.Field(coerce=True, nullable=True)
    reason_desc: Series[str] = pa.Field(coerce=True, nullable=True)
    other_system_id: Series[str] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True
class LeaveCreateSchema(BaseModel):
    """Pydantic schema for creating a new leave request"""
    # Required Fields
    employee_id: str = Field(..., description="Employee ID")
    start_date: datetime = Field(..., description="Start date of the leave")
    type_of_leave: str = Field(..., description="Type of leave")

    # Optional Fields
    end_date: Optional[datetime] = Field(None, description="End date of the leave")
    reason: Optional[str] = Field(None, description="Reason for the leave")
    entry_sequence: Optional[int] = Field(None, description="Entry sequence number")
    employee_responsible: Optional[str] = Field(None, description="Employee responsible")
    remarks: Optional[str] = Field(None, description="Additional remarks")
    detail_type: Optional[int] = Field(None, description="Type of detail")
    partial_start: Optional[int] = Field(None, description="Partial start indicator")
    partial_end: Optional[int] = Field(None, description="Partial end indicator")
    partial_leave: Optional[bool] = Field(None, description="Whether it's a partial leave")
    other_system_id: Optional[int] = Field(None, description="ID from another system")


    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee_id": "EMP123",
                "start_date": "2025-02-11T00:00:00",
                "absence_type": "vacation",
                "duration": 8.0,
                "end_date": "2025-02-11T00:00:00",
                "reason": "Annual leave",
                "type_of_leave": "paid",
                "partial_leave": False
            }
        }
class LeaveBalanceUpdateSchema(BaseModel):
    """Pydantic schema for updating leave balance"""
    # Required Fields
    type_of_leave: str = Field(..., description="Type of leave")
    hours: float = Field(..., description="Number of hours")

    # Optional Fields
    correction_reason: Optional[str] = Field(None, description="Reason for correction")
    booking_date: Optional[datetime] = Field(None, description="Booking date")
    employment_id: Optional[str] = Field(None, description="Employment ID")
    note: Optional[str] = Field(None, description="Additional notes")
    process_in_payroll: Optional[bool] = Field(None, description="Whether to process in payroll")
    leave_balance: Optional[str] = Field(None, description="Leave balance information")
    weeks: Optional[float] = Field(None, description="Number of weeks")


    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "type_of_leave": "vacation",
                "hours": 80.0,
                "correction_reason": "Annual adjustment",
                "booking_date": "2025-02-11T00:00:00",
                "process_in_payroll": True,
                "weeks": 2.0
            }
        }
class LeaveUpdateSchema(BaseModel):
    """Pydantic schema for updating a leave request"""
    # Required Fields
    leave_id: str = Field(..., description="Leave ID")

    # Optional Fields
    total_hours: Optional[float] = Field(None, description="Total hours of leave")
    partial_leave: Optional[bool] = Field(None, description="Whether it's a partial leave")
    employment_id: Optional[str] = Field(None, description="Employment ID")
    reason_of_leave: Optional[str] = Field(None, description="Reason for leave")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    type_of_leave: Optional[str] = Field(None, description="Type of leave")
    start_date: Optional[datetime] = Field(None, description="Start date of the leave")
    end_date: Optional[datetime] = Field(None, description="End date of the leave")
    remarks: Optional[str] = Field(None, description="Additional remarks")
    other_system_id: Optional[int] = Field(None, description="ID from another system")


    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "leave_id": "LEAVE123",
                "total_hours": 16.0,
                "partial_leave": True,
                "type_of_leave": "vacation",
                "start_date": "2025-02-11T00:00:00",
                "end_date": "2025-02-12T00:00:00",
                "reason_of_leave": "Change in plans"
            }
        }

class SickLeaveGetSchema(pa.DataFrameModel):
    employee_id: Series[str] = pa.Field(coerce=True)
    start_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    end_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    expected_end_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    guid: Series[str] = pa.Field(coerce=True)
    other_system_id: Series[str] = pa.Field(coerce=True,nullable=True)

    class Config:
        coerce = True
        strict = True
class SickLeaveUpdateSchema(BaseModel):
    """Pydantic schema for updating a sick leave request"""
    # Required Fields
    guid: str = Field(..., description="Unique identifier for the sick leave")

    # Optional Fields
    start_date: Optional[datetime] = Field(None, description="Start date of sick leave")
    start_date_report_date: Optional[datetime] = Field(None, description="Date when sickness was reported")
    type_of_leave: Optional[str] = Field(None, description="Type of sick leave")
    end_date: Optional[datetime] = Field(None, description="End date of sick leave")
    safety_net: Optional[str] = Field(None, description="Safety net information")
    end_date_report_date: Optional[datetime] = Field(None, description="Date when end of sickness was reported")
    reason_ending: Optional[str] = Field(None, description="Reason for ending sick leave")
    end_date_expected: Optional[datetime] = Field(None, description="Expected end date")
    available_first_day: Optional[datetime] = Field(None, description="First day of availability")
    total_hours: Optional[float] = Field(None, description="Total hours of sick leave")
    percentage_available: Optional[str] = Field(None, description="Percentage of availability")
    other_system_id: Optional[int] = Field(None, description="ID from another system")

    # Additional configurable fields
    reason_for_closing: Optional[str] = Field("1", description="Reason code for closing sick leave (default: 1)")
    absence_type_id: Optional[str] = Field("S", description="Type of absence (default: S)")
    hours_per_week_presence: Optional[str] = Field("0", description="Hours per week of presence")
    specify_presence: Optional[str] = Field("0", description="Specify presence details")


    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "guid": "SL123456",
                "start_date": "2025-02-11T00:00:00",
                "type_of_leave": "sick_leave",
                "end_date_expected": "2025-02-15T00:00:00",
                "percentage_available": "50.0",
                "total_hours": 20.0
            }
        }
class SickLeaveCreateSchema(BaseModel):
    """Pydantic schema for creating a new sick leave"""
    # Required Fields
    employee_id: str = Field(..., description="Employee ID")
    start_date_report_date: datetime = Field(..., description="Date when sickness was reported")
    type_of_leave: str = Field(..., description="Type of sick leave")

    # Optional Fields
    start_date: Optional[datetime] = Field(None, description="Start date of sick leave")
    end_date: Optional[datetime] = Field(None, description="End date of sick leave")
    safety_net: Optional[str] = Field(None, description="Safety net information")
    end_date_report_date: Optional[datetime] = Field(None, description="Date when end of sickness was reported")
    reason_ending: Optional[str] = Field(None, description="Reason for ending sick leave")
    end_date_expected: Optional[datetime] = Field(None, description="Expected end date")
    available_first_day: Optional[datetime] = Field(None, description="First day of availability")
    total_hours: Optional[float] = Field(None, description="Total hours of sick leave")
    percentage_available: Optional[str] = Field(None, description="Percentage of availability")
    other_system_id: Optional[int] = Field(None, description="ID from another system")

    # Additional configurable fields
    reason_for_closing: Optional[str] = Field("1", description="Reason code for closing sick leave (default: 1)")
    absence_type_id: Optional[str] = Field("S", description="Type of absence (default: S)")


    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee_id": "EMP123",
                "start_date_report_date": "2025-02-11T00:00:00",
                "type_of_sickleave": "full",
                "percentage_available": "0.0",
                "start_date": "2025-02-11T00:00:00",
                "end_date_expected": "2025-02-15T00:00:00",
                "total_hours": 40.0
            }
        }
