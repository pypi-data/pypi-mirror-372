import pandera as pa
from pandera.typing import Series, DateTime


class BaseDossierItemSchema(pa.DataFrameModel):
    # Required Fields
    dossieritem_type_id: Series[str] = pa.Field(coerce=True, nullable=False)

    # Optional Fields
    subject: Series[str] = pa.Field(coerce=True, nullable=True)
    note: Series[str] = pa.Field(coerce=True, nullable=True)
    date_created: Series[DateTime] = pa.Field(coerce=True, nullable=True)
    created_by: Series[str] = pa.Field(coerce=True, nullable=True)
    person_responsible: Series[str] = pa.Field(coerce=True, nullable=True)
    is_done: Series[bool] = pa.Field(coerce=True, nullable=True)
    property_1: Series[str] = pa.Field(coerce=True, nullable=True)
    property_2: Series[str] = pa.Field(coerce=True, nullable=True)
    property_3: Series[str] = pa.Field(coerce=True, nullable=True)
    save_file_with_subject: Series[bool] = pa.Field(coerce=True, nullable=True)
    profile_id: Series[str] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True


class DossierItemReactionSchema(pa.DataFrameModel):
    # Required Fields (from base)
    # dossieritem_type_id, subject, note, date_created, created_by, person_responsible, is_done, property_1, property_2, property_3, save_file_with_subject, profile_id

    # Additional Required Fields
    dossieritem_id: Series[str] = pa.Field(coerce=True, nullable=False)
    reaction: Series[str] = pa.Field(coerce=True, nullable=False)
    reaction_visibility: Series[str] = pa.Field(coerce=True, nullable=False)

    #Required Fields Attachment
    filename: Series[str] = pa.Field(coerce=True, nullable=False)
    attachment_filepath: Series[str] = pa.Field(coerce=True, nullable=False)


class DossierItemUploadSchema(BaseDossierItemSchema):
    # Required Fields (from base)
    # dossieritem_type_id, subject, note, date_created, created_by, person_responsible, is_done, property_1, property_2, property_3, save_file_with_subject, profile_id

    # Optional Fields for Subject Link
    sales_administration_id: Series[str] = pa.Field(coerce=True, nullable=True)
    sales_invoice_type_id: Series[str] = pa.Field(coerce=True, nullable=True)
    sales_invoice_id: Series[str] = pa.Field(coerce=True, nullable=True)
    purchase_administration_id: Series[str] = pa.Field(coerce=True, nullable=True)
    purchase_invoice_type_id: Series[str] = pa.Field(coerce=True, nullable=True)
    purchase_invoice_id: Series[str] = pa.Field(coerce=True, nullable=True)
    project_id: Series[str] = pa.Field(coerce=True, nullable=True)
    campaign_id: Series[str] = pa.Field(coerce=True, nullable=True)
    active: Series[bool] = pa.Field(coerce=True, nullable=True)
    precalculation_id: Series[str] = pa.Field(coerce=True, nullable=True)
    subscription_id: Series[str] = pa.Field(coerce=True, nullable=True)
    item_type: Series[str] = pa.Field(coerce=True, nullable=True)
    item_code: Series[str] = pa.Field(coerce=True, nullable=True)
    course_id: Series[str] = pa.Field(coerce=True, nullable=True)
    forecast_id: Series[str] = pa.Field(coerce=True, nullable=True)
    car_id: Series[str] = pa.Field(coerce=True, nullable=True)
    organizational_unit: Series[str] = pa.Field(coerce=True, nullable=True)
    purchase_order_id: Series[str] = pa.Field(coerce=True, nullable=True)
    sales_offer_id: Series[str] = pa.Field(coerce=True, nullable=True)
    sales_order_id: Series[str] = pa.Field(coerce=True, nullable=True)
    purchase_offer_id: Series[str] = pa.Field(coerce=True, nullable=True)
    location_id: Series[str] = pa.Field(coerce=True, nullable=True)
    application_id: Series[str] = pa.Field(coerce=True, nullable=True)
    to_purchase_relation: Series[str] = pa.Field(coerce=True, nullable=True)
    to_sales_relation: Series[str] = pa.Field(coerce=True, nullable=True)
    to_applicant: Series[str] = pa.Field(coerce=True, nullable=True)
    to_employee: Series[str] = pa.Field(coerce=True, nullable=True)
    to_person: Series[str] = pa.Field(coerce=True, nullable=True)
    destination_type_id: Series[str] = pa.Field(coerce=True, nullable=True)
    destination: Series[str] = pa.Field(coerce=True, nullable=True)
    employee_id: Series[str] = pa.Field(coerce=True, nullable=True)
    person_id: Series[str] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = True
