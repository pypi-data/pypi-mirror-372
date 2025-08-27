import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SpecificationAxisMixin(pa.DataFrameModel):
    specification_axis_code_1: Series[str] = pa.Field(coerce=True, nullable=True)
    specification_axis_code_2: Series[str] = pa.Field(coerce=True, nullable=True)
    specification_axis_code_3: Series[str] = pa.Field(coerce=True, nullable=True)
    specification_axis_code_4: Series[str] = pa.Field(coerce=True, nullable=True)
    specification_axis_code_5: Series[str] = pa.Field(coerce=True, nullable=True)

class PostCalculationGetSchema(pa.DataFrameModel):
    identity: Series[int] = pa.Field(coerce=True)         # Unique identifier
    year: Series[int] = pa.Field(coerce=True)             # Year of time entry
    period_id: Series[int] = pa.Field(coerce=True)        # Period identifier
    date_time: Series[str] = pa.Field(coerce=True)        # Date and time of entry
    employee_id: Series[str] = pa.Field(coerce=True,nullable=True)      # Employee identifier
    project_id: Series[str] = pa.Field(coerce=True,nullable=True)       # Project identifier
    description: Series[str] = pa.Field(coerce=True,nullable=True)      # Entry description
    item_type: Series[str] = pa.Field(coerce=True)        # Type of item
    item_code_id: Series[str] = pa.Field(coerce=True)     # Item code identifier
    unit_id: Series[str] = pa.Field(coerce=True)          # Unit of measurement
    quantity_unit: Series[float] = pa.Field(coerce=True)  # Quantity in hours/units
    chargeable: Series[bool] = pa.Field(coerce=True)      # Is the entry chargeable?
    approved: Series[bool] = pa.Field(coerce=True)        # Is the entry approved?
    prepared: Series[bool] = pa.Field(coerce=True)        # Is the entry prepared?
    date_modified: Series[str] = pa.Field(coerce=True)    # Last modification date
    system_date: Series[str] = pa.Field(coerce=True)      # System registration date

    class Config:
        coerce = True
        strict = True

class BasePostCalculationSchema(BaseModel):
    """Base schema for all post calculation operations"""
    # Common Fields - These are fields that appear in both operations
    date: Optional[datetime] = Field(None, description="Date of the calculation")
    item_type: Optional[str] = Field(None, description="Type of the item")
    item_code: Optional[str] = Field(None, description="Code of the item")

    # Optional Fields - Identifiers
    id: Optional[str] = Field(None, description="Unique identifier")
    external_key: Optional[str] = Field(None, description="External reference key")
    employee_id: Optional[str] = Field(None, description="Employee identifier")

    # Optional Fields - Quantities and Types
    quantity: Optional[float] = Field(None, description="Quantity value")
    type_of_hours: Optional[str] = Field(None, description="Type of hours")

    # Optional Fields - Project Related
    costcenter_employee: Optional[str] = Field(None, description="Employee cost center")
    approved: Optional[bool] = Field(None, description="Approval status")
    description: Optional[str] = Field(None, description="Description of the calculation")
    project_id: Optional[str] = Field(None, description="Project identifier")
    project_phase: Optional[str] = Field(None, description="Project phase")

    # Specification Axis fields (from SpecificationAxisMixin)
    specification_axis_1: Optional[str] = Field(None, description="Specification axis 1")
    specification_axis_2: Optional[str] = Field(None, description="Specification axis 2")
    specification_axis_3: Optional[str] = Field(None, description="Specification axis 3")
    specification_axis_4: Optional[str] = Field(None, description="Specification axis 4")
    specification_axis_5: Optional[str] = Field(None, description="Specification axis 5")

    class Config:
        from_attributes = True


class PostCalculationCreateSchema(BasePostCalculationSchema):
    """Schema for creating post calculations"""
    # Override fields to make them required
    date: datetime = Field(..., description="Date of the calculation")
    item_type: str = Field(..., description="Type of the item")
    item_code: str = Field(..., description="Code of the item")


class PostCalculationUpdateSchema(BasePostCalculationSchema):
    """Schema for updating post calculations"""
    # Override field to make it required
    id: str = Field(..., description="Unique identifier")

