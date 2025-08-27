import asyncio
import pandas as pd
from typing import Optional
import requests

from .schemas.debtor import DebtorGetSchema, DebtorCreateSchema
from .schemas.creditor import CreditorUpdateSchema, CreditorGetSchema, CreditorCreateSchema


class Debtor:
    """Debtor management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize Debtor class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_debtor"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get debtor information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing debtor information

        Raises:
            Exception: If get debtor operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=DebtorGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get debtor failed: {str(e)}") from e

    def __build_req_body(self, data: dict) -> dict:
        """
        Creates the request body for debtor operations

        Args:
            data: Dictionary containing debtor data

        Returns:
            dict: Formatted request body for AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            base_body = {
                "KnSalesRelationPer": {
                    "Element": {
                        "@DbId": data.get('debtor_id'),
                        "Fields": {
                            "CuId": data.get("currency")
                        },
                        "Objects": {
                            "KnPerson": {
                                "Element": {
                                    "Fields": {
                                        "MatchPer": data.get('match_person_on', '0'),
                                        "BcId": data.get('internal_id',1)
                                    },
                                    "Objects": {}
                                }
                            }
                        }
                    }
                }
            }

            # Handle address fields
            address_fields = {
                'mailbox_address': 'PbAd',
                'country': 'CoId',
                'street': 'Ad',
                'house_number': 'HmNr',
                'house_number_add': 'HmAd',
                'postal_code': 'ZpCd',
                'city': 'Rs',
                'search_address_by_postal_code': 'ResZip'
            }

            address_updates = {v: data[k] for k, v in address_fields.items() if k in data}

            if address_updates:
                address_body = {
                    "KnBasicAddressAdr": {
                        "Element": {
                            "Fields": address_updates
                        }
                    },
                    "KnBasicAddressPad": {
                        "Element": {
                            "Fields": address_updates
                        }
                    }
                }
                base_body['KnSalesRelationPer']['Element']['Objects']['KnPerson']['Element']['Objects'].update(address_body)

            # Handle debtor specific fields
            debtor_fields = {
                'collective_ledger_account': 'ColA',
                'payment_condition': 'PaCd',
                'send_reminder': 'DuYN'
            }

            debtor_updates = {v: data[k] for k, v in debtor_fields.items() if k in data}
            base_body['KnSalesRelationPer']['Element']['Fields'].update(debtor_updates)

            # Handle person fields
            person_fields = {
                'autonumber_person': 'AutoNum',
                'enter_birthname_seperate': 'SpNm',
                'person_id': 'BcCo',
                'mailbox_address': 'PbAd',
                'mail_private': 'EmA2',
                'nickname': 'CaNm',
                'first_name': 'FiNm',
                'initials': 'In',
                'prefix': 'Is',
                'last_name': 'LaNm',
                'prefix_birth_name': 'IsBi',
                'birth_name': 'NmBi',
                'prefix_partner_name': 'IsPa',
                'partner_name': 'NmPa',
                'gender': 'ViGe',
                'phone_private': 'TeN2',
                'name_use': 'ViUs'
            }

            person_updates = {v: data[k] for k, v in person_fields.items() if k in data}
            base_body['KnSalesRelationPer']['Element']['Objects']['KnPerson']['Element']['Fields'].update(person_updates)

            return base_body
        except Exception as e:
            raise Exception("Build request body failed: " + str(e)) from e

    def create(self, data: dict, overload_fields: dict = None, method: str = 'PUT') -> Optional[requests.Response]:
        """
        Create debtor in AFAS

        Args:
            data: Dictionary containing debtor data
            overload_fields: Dictionary of custom fields to be included
            method: HTTP method - PUT for update, POST for create

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails or invalid method provided
        """
        try:
            try:
                valid_data = DebtorCreateSchema(**data).model_dump()
            except Exception as e:
                raise Exception("Data validation failed: " + str(e))

            url = f"{self.afas.base_url}/KnSalesRelationPer"
            body = self.__build_req_body(valid_data)

            if overload_fields:
                body['KnSalesRelationPer']['Element']['Objects']['KnPerson']['Element']['Fields'].update(overload_fields)

            response = self.afas.session.post(
                url=url,
                json=body,
                timeout=self.afas.timeout
            )

            return response
        except Exception as e:
            raise ValueError("Create debtor failed: " + str(e))

class Creditor:
    """Creditor management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize Creditor class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_creditor"
        self.update_url = f"{self.afas.base_url}/KnPurchaseRelationPer"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get creditor information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing creditor information

        Raises:
            Exception: If get creditor operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=CreditorGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get creditor failed: {str(e)}") from e

    def __build_req_body(self, data: dict, overload_fields: dict) -> dict:
        """
        Creates the request body for creditor operations

        Args:
            data: Dictionary containing creditor data

        Returns:
            dict: Formatted request body for AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            base_body = {
                "KnPurchaseRelationPer": {
                    "Element": {
                        "Fields": {
                            "CuId": data.get("currency")
                        },
                        "Objects": {
                            "KnPerson": {
                                "Element": {
                                    "Fields": {
                                        "MatchPer": data.get('match_person_on', '0'),
                                    },
                                    "Objects": []
                                }
                            }
                        }
                    }
                }
            }

            # Add creditor ID if present
            if 'creditor_id' in data:
                base_body['KnPurchaseRelationPer']['Element'].update({"@CrId": data['creditor_id']})

            # Handle base creditor fields
            base_fields = {
                'is_creditor': 'IsCr',
                'payment_to_external': 'IB47',
                'preferred_iban': 'Iban',
                'remark': 'Rm',
                'payment_condition': 'PaCd',
                'collective_account': 'ColA',
                'preferred_delivery_method': 'InPv',
                'automatic_payment': 'AuPa',
                'compact': 'PaCo',
                'payment_specification': 'PaSp',
                'preferred_provisioning': 'InPv'
            }

            base_updates = {}
            for key in base_fields.keys():
                if key in data:
                    if data[key] != '' and pd.notna(data[key]):
                        base_updates[base_fields[key]] = data[key]

            base_body['KnPurchaseRelationPer']['Element']['Fields'].update(base_updates)

            # Handle person fields
            person_fields = {
                'internal_id': 'BcId',
                'person_id': 'BcCo',
                'log_birthname_seperately': 'SpNm',
                'postal_address_applied': 'PadAdr',
                'auto_number': 'AutoNum',
                'last_name': 'LaNm',
                'first_name': 'FiNm',
                'middle_name': 'Is',
                'gender': 'ViGe',
                'salutation': 'TtId',
                'correspondence': 'Corr',
            }

            person_updates = {}
            for key in person_fields:
                if key in data:
                    if data[key] != '' and pd.notna(data[key]):
                        person_updates[person_fields[key]] = data[key]
            base_body['KnPurchaseRelationPer']['Element']['Objects']['KnPerson']['Element']['Fields'].update(person_updates)

            # Handle address fields
            address_fields = {
                'country': 'CoId',
                'address_is_postal_address': 'PbAd',
                'street': 'Ad',
                'house_number': 'HmNr',
                'house_number_addition': 'HmAd',
                'postal_code': 'ZpCd',
                'city': 'Rs',
                'match_city_on_postal_code': 'ResZip',
                'mailbox_address': 'PbAd'

            }

            address_updates = {}
            for key in address_fields:
                if key in data:
                    if data[key] != '' and pd.notna(data[key]):
                        address_updates[address_fields[key]] = data[key]
            base_body['KnPurchaseRelationPer']['Element']['Objects']['KnPerson']['Element']['Fields'].update(
                address_updates)

            if address_updates:
                new_address = {
                    "KnBasicAddressAdr": {
                        "Element": {
                            "Fields": address_updates
                        }
                    }
                }
                base_body['KnPurchaseRelationPer']['Element']['Objects']['KnPerson']['Element']['Objects'].append(
                    new_address)

            # Handle bank account fields
            bank_fields = {
                'country_of_bank': 'CoId',
                'iban_check': 'IbCk',
                'iban': 'Iban'
            }

            bank_updates = {}
            for key in bank_fields:
                if key in data:
                    if data[key] != '' and pd.notna(data[key]):
                        bank_updates[bank_fields[key]] = data[key]

            if bank_updates:
                new_bank = {
                    "KnBankAccount": {
                        "Element": {
                            "Fields": bank_updates
                        }
                    }
                }
                base_body['KnPurchaseRelationPer']['Element']['Objects']['KnPerson']['Element']['Objects'].append(new_bank)
            if overload_fields:
                # Add overload fields to base element fields
                base_body['KnPurchaseRelationPer']['Element']['Fields'].update(overload_fields)
                # Add overload fields to person fields
                base_body['KnPurchaseRelationPer']['Element']['Objects']['KnPerson']['Element']['Fields'].update(
                    overload_fields)

            return base_body
        except Exception as e:
            raise Exception("Build request body failed: " + str(e)) from e

    def create(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Create creditor in AFAS

        Args:
            data: Dictionary containing creditor data
            overload_fields: Dictionary of custom fields to be included

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            try:
                valid_data = CreditorCreateSchema(**data).model_dump()
            except Exception as e:
                raise Exception("Data validation failed: " + str(e))

            body = self.__build_req_body(valid_data, overload_fields)

            return self.afas.session.post(
                url=self.update_url,
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise ValueError("Create creditor failed: " + str(e))

    def update(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Update creditor in AFAS

        Args:
            data: Dictionary containing creditor data
            overload_fields: Dictionary of custom fields to be included

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails or invalid method provided
        """
        try:
            try:
                valid_data = CreditorUpdateSchema(**data).model_dump()
            except Exception as e:
                raise Exception("Data validation failed: " + str(e))

            body = self.__build_req_body(valid_data, overload_fields)

            return self.afas.session.put(
                url=self.update_url,
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise ValueError("Update creditor failed: " + str(e))
