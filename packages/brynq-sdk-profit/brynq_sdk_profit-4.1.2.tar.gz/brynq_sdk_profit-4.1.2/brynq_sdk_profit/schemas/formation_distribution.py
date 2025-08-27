import pandera as pa
from pandera.typing import Series
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FormationDistributionCreateSchema(BaseModel):
    """
    Pydantic schema for function creation.
    This schema allows validation of both flat and nested dictionaries through field aliases.
    """
    # Required Fields
    employee_id: str = Field(..., description="Employee ID")
    startdate: datetime = Field(..., description="Function start date")
    organizational_unit: str = Field(..., description="Organizational unit ID")
    function_id: str = Field(..., description="Function ID")
    costcenter_id: str = Field(..., description="Cost center ID")
    percentage: float = Field(None, description="Percentage")

    # Optional Fields
    costcarrier_id: Optional[str] = Field(None, description="Cost carrier ID")


    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "employee_id": "EMP123",
                "startdate": "2025-01-01T00:00:00",
                "organizational_unit": "ORG1",
                "function_id": "FUNC1",
                "costcenter_id": "CC1",
                "costcarrier_id": "CCR1",
                "percentage": 100
            }
        }


class FormationDistributionGetSchema(pa.DataFrameModel):
    # Required Fields
    id: Series[str] = pa.Field(coerce=True, nullable=False)
    blocked: Series[bool] = pa.Field(coerce=True, nullable=False)
    employer: Series[str] = pa.Field(coerce=True, nullable=False)
    description: Series[str] = pa.Field(coerce=True, nullable=False)
    type: Series[str] = pa.Field(coerce=True, nullable=False)
    percentage: Series[float] = pa.Field(coerce=True, nullable=False)
