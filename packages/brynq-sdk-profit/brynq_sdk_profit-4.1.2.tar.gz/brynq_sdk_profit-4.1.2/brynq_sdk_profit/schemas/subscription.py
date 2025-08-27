import pandas as pd
import pandera as pa
from pandera.typing import Series, DateTime


class SubscriptionUpdateSchema(pa.DataFrameModel):
    """Schema for updating subscription information in DataFrame format.
    
    This schema validates subscription updates including start/end dates,
    item details, amounts, and termination information. It ensures data
    consistency when modifying existing subscriptions in the system.
    
    The schema includes validation for amounts to prevent negative values
    and handles both subscription-level and subscription-line-level updates.
    """
    # Required Fields
    subscription_id: Series[str] = pa.Field(coerce=True, nullable=False)

    # Optional Fields
    start_date_subscription: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    end_date_subscription: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    item_type_id: Series[str] = pa.Field(coerce=True, nullable=True)
    item_code: Series[str] = pa.Field(coerce=True, nullable=True)
    amount: Series[float] = pa.Field(coerce=True, nullable=True)
    subscription_line_id: Series[str] = pa.Field(coerce=True, nullable=True)
    start_date_subscription_line: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    end_date_subscription_line: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    reason_of_termination: Series[str] = pa.Field(coerce=True, nullable=True)
    reason_of_termination_subscription: Series[str] = pa.Field(coerce=True, nullable=True)

    @pa.check("amount")
    def validate_amount(cls, series: Series) -> Series:
        """Validate that amount is not negative"""
        return series >= 0

    class Config:
        coerce = True
        strict = True
