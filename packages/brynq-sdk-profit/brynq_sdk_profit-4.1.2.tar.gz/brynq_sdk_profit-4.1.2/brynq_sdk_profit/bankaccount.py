import asyncio
import pandas as pd
from typing import Optional, Dict, Any
import requests

from .schemas.bank_account import (
    BankAccountUpdatePersonSchema,
    GetBankAccountSchema,
    BankAccountUpdateInfoSchema
)

class BankAccount:
    """Bank account management class for AFAS integration"""

    def __init__(self, afas_connector: Any) -> None:
        """
        Initialize BankAccount class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_bank_accounts"

    def get(self, filter_fields: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Get bank account data

        Args:
            filter_fields: Optional filters to apply

        Returns:
            pd.DataFrame: Bank account data
            
        Raises:
            Exception: If get bank account operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=GetBankAccountSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get bank account failed: {str(e)}") from e

    def __build_employee_bank_request_body(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a request body for employee bank account data.

        Args:
            data (Dict[str, Any]): Input data containing bank account information

        Returns:
            Dict[str, Any]: Formatted request body for AFAS API

        Raises:
            SchemaException: If input data doesn't match required schema
        """
        try:
            # Construct base request body according to employee structure
            base_body = {
                "AfasEmployee": {
                    "Element": {
                        "@EmId": data.get("employee_id"),
                        "Objects": {
                            "AfasBankInfo": {
                                "Element": {
                                    "@NoBk": data.get("cash_payment"),
                                    "Fields": {
                                        "IbCk": data.get("iban_check"),#Always True ?
                                        "Iban": data.get("iban"),
                                    }
                                }
                            }
                        }
                    }
                }
            }

            # Add optional bank fields if present
            bank_field_mapping = {
                'bankname': 'BkIc',
                'country': 'CoId',
                'cash_payment': '@NoBk',
                'salary_bank_account': 'SaAc',
                'acc_outside_sepa': 'FoPa',
                #'bank_type': 'BkTp',
                'sequence_number': 'SeNo',
                'bic_code': 'Bic',
                'payment_reference': 'Ds',
                'deviating_name': 'Nm',
                'wage_component_id': 'ScId',
                'branch_address':'BaAd',
                'routing_number':'U840F08F04FD9ABCD446D6990FAE30EFF', #Clearing system must set with this
                'bank_name':'BaNm',
            }

            bank_fields = {}
            for field, afas_field in bank_field_mapping.items():
                if field in data and pd.notna(data[field]):
                    bank_fields[afas_field] = data[field]

            if "CoId" in bank_fields:
                bank_fields["CoId"] = self.afas.iso2_mapping.get(bank_fields["CoId"])

            if bank_fields:
                base_body['AfasEmployee']['Element']['Objects']['AfasBankInfo']['Element']['Fields'].update(bank_fields)

            return base_body
        except Exception as e:
            raise KeyError("Build request body failed: " + str(e)) from e

    def __build_person_bank_request_body(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a request body for person bank account data.

        Args:
            data (Dict[str, Any]): Input data containing bank account information

        Returns:
            Dict[str, Any]: Formatted request body for AFAS API

        Raises:
            SchemaException: If input data doesn't match required schema
        """
        # Validate data using pandera

        # Construct base request body for person
        try:
            base_body = {
                "KnPerson": {
                    "Element": {
                        "Fields": {
                            "MatchPer": data.get("match_person"), #Match person with employee "0"
                            "BcCo": data.get("person_id"),
                        },
                        "Objects": {
                            "KnBankAccount": {
                                "Element": {
                                    "Fields": {
                                        "Iban": data.get("iban"),
                                        "IbCk": data.get("iban_check") # Always True ?
                                    }
                                }
                            }
                        }
                    }
                }
            }

            # Add optional bank fields if present
            bank_field_mapping = {
                'country': 'CoId',
                #'bank_type': 'BkTp',
                'bic_or_swift': 'Bic',
                'branch_address':'BaAd',
                'routing_number':'U840F08F04FD9ABCD446D6990FAE30EFF', #Clearing system must set with this
                'bank_address':'BaAd',
                'bank_name':'BaNm',
            }

            bank_fields = {}
            for field, afas_field in bank_field_mapping.items():
                if field in data and pd.notna(data[field]):
                    bank_fields[afas_field] = data[field]

            if "CoId" in bank_fields:
                bank_fields["CoId"] = self.afas.iso2_mapping.get(bank_fields["CoId"])

            if bank_fields:
                base_body['KnPerson']['Element']['Objects']['KnBankAccount']['Element']['Fields'].update(bank_fields)

            # Add SSN if provided
            if "ssn" in data and pd.notna(data["ssn"]):
                base_body['KnPerson']['Element']['Objects']['KnBankAccount']['Element']['Fields']["Sose"] = data['ssn']
            return base_body
        except Exception as e:
            raise Exception("Build body failed: " + str(e)) from e

    def update_bank_info(self, data: Dict[str, Any]) -> requests.Response:
        """
        Update Bank Account for employee in AFAS

        Args:
            data (Dict[str, Any]): Dictionary containing bank account data

        Returns:
            requests.Response: Response from AFAS API
        """
        # Add employee_id to data for schema validation
        try:
            try:
                valid_data = BankAccountUpdateInfoSchema(**data).model_dump()
                req_body = self.__build_employee_bank_request_body(data=valid_data)
            except Exception as e:
                raise Exception("Data validation failed:" + str(e)) from e

            # Determine URL based on sequence_number presence
            if 'sequence_number' in data:
                url = f"{self.afas.base_url}/KnEmployee/AfasEmployee/@EmId/{data['employee_id']}/AfasBankInfo/SeNo/{data['sequence_number']}"
            else:
                url = f"{self.afas.base_url}/KnEmployee/AfasBankInfo"

            # Send request to AFAS
            return self.afas.session.post(
                url=url,
                json=req_body, timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception("Update bank info employee failed: " + str(e)) from e

    def update(self, data: Dict[str, Any]) -> requests.Response:
        """
        Create/Update Bank Account for person in AFAS
        
        Args:
            data (Dict[str, Any]): Dictionary containing bank account data
        
        Returns:
            requests.Response: Response from AFAS API
        """
        # Add person_id to data for schema validation
        try:
            try:
                valid_data = BankAccountUpdatePersonSchema(**data).model_dump()
                req_body = self.__build_person_bank_request_body(data=valid_data)
            except Exception as e:
                raise Exception("Data validation failed:" + str(e)) from e

        # Send POST request to AFAS
        # This makes both create and update doesn't matter PUT or POST
            return self.afas.session.put(
                    url=f"{self.afas.base_url}/KnPerson/KnBankAccount",
                    json=req_body, timeout=self.afas.timeout
                )
        except Exception as e:
            raise Exception("Update bank account person: " + str(e)) from e

    def delete_bank_account_employee(self, data: Dict[str, Any]) -> requests.Response:
        """
        Delete a bank account for an employee in AFAS.

        Args:
            data (Dict[str, Any]): Dictionary containing:
                - employee_id (str): ID of the employee
                - sequence_number (str): Sequence number of the bank account
        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If required fields are missing
        """

        # Send DELETE request to AFAS
        try:
            return self.afas.session.delete(
                url=f"{self.afas.base_url}/KnEmployee/AfasEmployee/@EmId/{data['employee_id']}/AfasBankInfo/SeNo/{data['sequence_number']}", timeout=self.afas.timeout)
        except Exception as e:
            raise Exception("Delete Bank Account Failed.", e)
