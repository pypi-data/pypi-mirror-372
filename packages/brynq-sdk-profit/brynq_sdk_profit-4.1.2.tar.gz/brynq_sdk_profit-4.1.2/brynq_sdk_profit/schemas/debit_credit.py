import pandera as pa
from pandera.typing import Series, DateTime

class DebtorUpdateSchema(pa.DataFrameModel):
    # Required Fields
    debtor_id: Series[str] = pa.Field(coerce=True, nullable=False)

    # Personal Information
    person_id: Series[str] = pa.Field(coerce=True, nullable=True)
    first_name: Series[str] = pa.Field(coerce=True, nullable=True)
    initials: Series[str] = pa.Field(coerce=True, nullable=True)
    prefix: Series[str] = pa.Field(coerce=True, nullable=True)
    last_name: Series[str] = pa.Field(coerce=True, nullable=True)
    nickname: Series[str] = pa.Field(coerce=True, nullable=True)
    gender: Series[str] = pa.Field(coerce=True, nullable=True)

    # Birth and Partner Information
    birth_name: Series[str] = pa.Field(coerce=True, nullable=True)
    prefix_birth_name: Series[str] = pa.Field(coerce=True, nullable=True)
    partner_name: Series[str] = pa.Field(coerce=True, nullable=True)
    prefix_partner_name: Series[str] = pa.Field(coerce=True, nullable=True)
    enter_birthname_seperate: Series[bool] = pa.Field(coerce=True, nullable=True)

    # Address Information
    country: Series[str] = pa.Field(coerce=True, nullable=True)
    street: Series[str] = pa.Field(coerce=True, nullable=True)
    house_number: Series[str] = pa.Field(coerce=True, nullable=True)
    house_number_add: Series[str] = pa.Field(coerce=True, nullable=True)
    postal_code: Series[str] = pa.Field(coerce=True, nullable=True)
    city: Series[str] = pa.Field(coerce=True, nullable=True)
    mailbox_address: Series[str] = pa.Field(coerce=True, nullable=True)
    search_address_by_postal_code: Series[bool] = pa.Field(coerce=True, nullable=True)

    # Contact Information
    mail_private: Series[str] = pa.Field(coerce=True, nullable=True)
    phone_private: Series[str] = pa.Field(coerce=True, nullable=True)

    # Other Fields
    match_person_on: Series[str] = pa.Field(coerce=True, nullable=True)
    name_use: Series[str] = pa.Field(coerce=True, nullable=True)
    autonumber_person: Series[bool] = pa.Field(coerce=True, nullable=True)
    begin_date: Series[DateTime] = pa.Field(coerce=True, nullable=True)

    class Config:
        coerce = True
        strict = False  # overload_fields için False

class DebtorGetSchema(pa.DataFrameModel):
    DebtorId: Series[str] = pa.Field(coerce=True)
    DebtorName: Series[str] = pa.Field(coerce=True)
    BcCo: Series[str] = pa.Field(coerce=True)
    SearchName: Series[str] = pa.Field(coerce=True,nullable=True)
    AdressLine1: Series[str] = pa.Field(coerce=True)
    AdressLine3: Series[str] = pa.Field(coerce=True)
    AdressLine4: Series[str] = pa.Field(coerce=True, nullable=True)
    TelNr: Series[str] = pa.Field(coerce=True,nullable=True)
    Email: Series[str] = pa.Field(coerce=True)
    IBAN: Series[str] = pa.Field(coerce=True, nullable=True)
    VatNr: Series[str] = pa.Field(coerce=True, nullable=True)
    ChOfCommNr: Series[str] = pa.Field(coerce=True,nullable=True)
    CollectAccount: Series[str] = pa.Field(coerce=True)
    PayCon: Series[str] = pa.Field(coerce=True)
    VatDuty: Series[str] = pa.Field(coerce=True)
    Blocked: Series[bool] = pa.Field(coerce=True)
    CreditLimit: Series[float] = pa.Field(coerce=True)
    CurrencyId: Series[str] = pa.Field(coerce=True)
    AutoPayment: Series[bool] = pa.Field(coerce=True)
    CreateDate: Series[str] = pa.Field(coerce=True)
    ModifiedDate: Series[str] = pa.Field(coerce=True)

    class Config:
        coerce = True
        strict = True

class CreditorUpdateSchema(pa.DataFrameModel):
    # Required Fields
    creditor_id: Series[str] = pa.Field(coerce=True, nullable=False)

    # Basic Settings
    currency_id: Series[str] = pa.Field(coerce=True, nullable=True)  # added
    is_creditor: Series[bool] = pa.Field(coerce=True, nullable=True)  # added

    # Personal Identification
    person_id: Series[str] = pa.Field(coerce=True, nullable=True)
    internal_id: Series[str] = pa.Field(coerce=True, nullable=True)
    match_person_on: Series[str] = pa.Field(coerce=True, nullable=True)

    # Personal Information
    last_name: Series[str] = pa.Field(coerce=True, nullable=True)  # added
    gender: Series[str] = pa.Field(coerce=True, nullable=True)  # added
    salutation: Series[str] = pa.Field(coerce=True, nullable=True)  # added
    correspondence: Series[bool] = pa.Field(coerce=True, nullable=True)  # added

    # Payment and Delivery Settings
    collective_account: Series[str] = pa.Field(coerce=True, nullable=True)
    preferred_delivery_method: Series[str] = pa.Field(coerce=True, nullable=True)
    automatic_payment: Series[bool] = pa.Field(coerce=True, nullable=True)
    compact: Series[bool] = pa.Field(coerce=True, nullable=True)
    payment_specification: Series[str] = pa.Field(coerce=True, nullable=True)

    # Additional Information
    log_birthname_seperately: Series[bool] = pa.Field(coerce=True, nullable=True)
    remark: Series[str] = pa.Field(coerce=True, nullable=True)
    postal_address_applied: Series[bool] = pa.Field(coerce=True, nullable=True)  # added
    auto_number: Series[bool] = pa.Field(coerce=True, nullable=True)  # added

    # Bank Account Information
    country_of_bank: Series[str] = pa.Field(coerce=True, nullable=True)  # added
    iban_check: Series[bool] = pa.Field(coerce=True, nullable=True)  # added
    bank_account: Series[str] = pa.Field(coerce=True, nullable=True)  # added
    account_guardian: Series[bool] = pa.Field(coerce=True, nullable=True)  # added
    account_check: Series[bool] = pa.Field(coerce=True, nullable=True)  # added

    # Address Information
    country: Series[str] = pa.Field(coerce=True, nullable=True)  # added
    is_postal_address: Series[bool] = pa.Field(coerce=True, nullable=True)  # added
    house_number: Series[str] = pa.Field(coerce=True, nullable=True)  # added
    postal_code: Series[str] = pa.Field(coerce=True, nullable=True)  # added
    city: Series[str] = pa.Field(coerce=True, nullable=True)  # added
    match_city_on_postal_code: Series[bool] = pa.Field(coerce=True, nullable=True)  # added
    mailbox_address: Series[str] = pa.Field(coerce=True, nullable=True)


    class Config:
        coerce = True
        strict = False  # overload_fields için False

class CreditorGetSchema(pa.DataFrameModel):
    CreditorId: Series[str] = pa.Field(coerce=True)
    CreditorName: Series[str] = pa.Field(coerce=True)
    BcCo: Series[str] = pa.Field(coerce=True)
    SearchName: Series[str] = pa.Field(coerce=True)
    Adressline1: Series[str] = pa.Field(coerce=True)
    Adressline3: Series[str] = pa.Field(coerce=True)
    Adressline4: Series[str] = pa.Field(coerce=True, nullable=True)
    TelNr: Series[str] = pa.Field(coerce=True)
    Email: Series[str] = pa.Field(coerce=True,nullable=True)
    IBAN: Series[str] = pa.Field(coerce=True, nullable=True)
    Btw_nummer: Series[str] = pa.Field(coerce=True, nullable=True)  # Changed from "Btw-nummer" due to dash
    ChOfCommNr: Series[str] = pa.Field(coerce=True,nullable=True)
    PaymentCondition: Series[str] = pa.Field(coerce=True,nullable=True)
    CreditLimit: Series[float] = pa.Field(coerce=True, nullable=True)
    TempBlocked: Series[bool] = pa.Field(coerce=True)
    VatDuty: Series[str] = pa.Field(coerce=True)
    AutoPayment: Series[bool] = pa.Field(coerce=True)
    Blocked: Series[bool] = pa.Field(coerce=True)
    CreateDate: Series[str] = pa.Field(coerce=True)
    ModifiedDate: Series[str] = pa.Field(coerce=True)

    class Config:
        coerce = True
        strict = True