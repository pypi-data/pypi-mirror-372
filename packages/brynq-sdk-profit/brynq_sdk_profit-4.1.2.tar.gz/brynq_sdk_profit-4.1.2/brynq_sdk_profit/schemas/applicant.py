import pandas as pd
import pandera as pa
from pandera.typing import Series,DateTime


class ApplicantUpdateSchema(pa.DataFrameModel):
    # Required Fields
    last_name: Series[str] = pa.Field(coerce=True, nullable=False)
    gender: Series[str] = pa.Field(coerce=True, nullable=False)
    application_number: Series[str] = pa.Field(coerce=True, nullable=False)

    # Optional Fields
    initials: Series[str] = pa.Field(coerce=True, nullable=True)
    first_name: Series[str] = pa.Field(coerce=True, nullable=True)
    date_of_birth: Series[str] = pa.Field(coerce=True, nullable=True)
    email: Series[str] = pa.Field(coerce=True, nullable=True)
    mobile_phone: Series[str] = pa.Field(coerce=True, nullable=True)
    country: Series[str] = pa.Field(coerce=True, nullable=True)
    street: Series[str] = pa.Field(coerce=True, nullable=True)
    housenumber: Series[str] = pa.Field(coerce=True, nullable=True)
    housenumber_addition: Series[str] = pa.Field(coerce=True, nullable=True)
    postal_code: Series[str] = pa.Field(coerce=True, nullable=True)
    city: Series[str] = pa.Field(coerce=True, nullable=True)
    site_guid: Series[str] = pa.Field(coerce=True, nullable=True)
    work_email: Series[str] = pa.Field(coerce=True, nullable=True)
    person_id: Series[str] = pa.Field(coerce=True, nullable=True)


class SubscriptionUpdateSchema(pa.DataFrameModel):
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
