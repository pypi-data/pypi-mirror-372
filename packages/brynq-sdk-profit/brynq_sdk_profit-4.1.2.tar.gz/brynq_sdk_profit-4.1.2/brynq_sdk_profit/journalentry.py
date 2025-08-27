import asyncio
import pandas as pd
from typing import Optional
import requests

from .schemas.cost import JournalEntryUploadSchema, JournalentryGetSchema
from brynq_sdk_functions import Functions

class JournalEntry:
    """Journal Entry management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize JournalEntry class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_journal_entry"


    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get journal entry information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing journal entry information

        Raises:
            Exception: If get journal entry operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=JournalentryGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get journal entry failed: {str(e)}") from e

    def __build_request_body(self, df: pd.DataFrame) -> dict:
        """
        Creates request body for journal entries

        Args:
            df: data with journal entries

        Returns:
            dict: Request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
            base_body = {
                "FiEntryPar": {
                    "Element": {
                        "Fields": {
                            "Year": str(df.iloc[0]['year']),
                            "Peri": str(df.iloc[0]["period"]),
                            "UnId": str(df.iloc[0]['administration_id']),
                            "JoCo": str(df.iloc[0]['journal_id'])
                        },
                        "Objects": [
                            {
                                "FiEntries": {
                                    "Element": []
                                }
                            }
                        ]
                    }
                }
            }

            for row in df.to_dict(orient='records'):
                for key, value in row.items():
                    if isinstance(value, pd.Timestamp):
                        row[key] = value.strftime('%Y-%m-%d')
                    elif pd.api.types.is_integer_dtype(pd.Series([value])):
                        row[key] = int(value)
                    elif pd.api.types.is_float_dtype(pd.Series([value])):
                        row[key] = float(value)
                entry = {
                    "Fields": {
                        "VaAs": row.get("account_reference", "1"),  
                        "AcNr": row["general_ledger_id"],
                        "EnDa": row['date_booking'],
                        "BpDa": row['date_approved'],
                        "BpNr": row['booking_number'],
                        "Ds": row['description'],
                        "AmDe": row['debet'],
                        "AmCr": row['credit']
                    },
                    "Objects": [
                        {
                            "FiDimEntries": {
                                "Element": {
                                    "Fields": {
                                        "DiC1": row['cost_center_id'] if pd.notna(row['cost_center_id']) else None,
                                        "DiC2": row['cost_carrier_id'] if pd.notna(row['cost_carrier_id']) else None
                                    }
                                }
                            }
                        }
                    ]
                }
                base_body['FiEntryPar']["Element"]["Objects"][0]["FiEntries"]["Element"].append(entry)

            return base_body
        except Exception as e:
            raise Exception(f"Build request body failed: {str(e)}")

    def __create_journalentry_for_period(self, df: pd.DataFrame) -> requests.Response:
        """
        Creates journal entries in Afas profit using the FiEntries updateconnector.

        Args:
            df: DataFrame with journal entries. Must contain all required fields and balance per booking number.

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails or data is unbalanced
        """

        # Create request body
        body = self.__build_request_body(df)

        # Make API request
        return self.afas.session.post(
            url=f"{self.afas.base_url}/FiEntries",
            json=body, timeout=self.afas.timeout
        )

    def create(self, df: pd.DataFrame) -> Optional[requests.Response]:

        upload_summary = []
        status_codes = []  # extract all period and year data as a list and drop duplicates from the list
        df['unique_period_year_per_administration'] = df['period'].astype(str) + df['year'].astype(str) + df[
            'administration_id'].astype(str) + df['journal_id'].astype(str)
        year_period_per_administration_list = df['unique_period_year_per_administration'].unique().tolist()
        for unique_period in year_period_per_administration_list:
            df_period = df[df['unique_period_year_per_administration'] == unique_period]
            # drop the columns that are not needed for the upload iteration
            df_period = df_period.sort_values(by=['booking_number', 'date_booking'])
            # pass the index payload and the dataframe to the upload method
            # reset the index of the dataframe
            df_period = df_period.reset_index(drop=True)
            try:
                valid_data, invalid_data = Functions.validate_data(df=df_period, schema=JournalEntryUploadSchema,
                                                                   debug=True)
            except Exception as e:
                raise ValueError(f"Data validation error: {str(e)}")
            update = self.__create_journalentry_for_period(df=valid_data)
            json_update = update.json()
            if 200 <= update.status_code < 300:
                upload_summary.append(
                    f"Journal entries for year {df_period.iloc[0]['year']}, period {df_period.iloc[0]['period']}, adminstration {df_period.iloc[0]['administration_id']} and journal {df_period.iloc[0]['journal_id']} uploaded successfully. Status code: {update.status_code}")
                status_codes.append(update.status_code)
            else:
                upload_summary.append(
                    f"Journal entries for year {df_period.iloc[0]['year']}, period {df_period.iloc[0]['period']}, adminstration {df_period.iloc[0]['administration_id']} and journal {df_period.iloc[0]['journal_id']} failed. Status code: {update.status_code} {json_update['externalMessage']}")
                status_codes.append(update.status_code)

        return upload_summary, status_codes

    def delete(self, year, entry_no) -> requests.Response:
        return self.afas.session.delete(
            url=f"{self.afas.base_url}/FiEntries/FiEntryPar/Year,UnId/{year},{entry_no}",
            timeout=self.afas.timeout
        )
