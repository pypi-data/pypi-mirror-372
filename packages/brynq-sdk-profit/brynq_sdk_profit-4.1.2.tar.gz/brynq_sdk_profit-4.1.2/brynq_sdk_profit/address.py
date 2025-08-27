import asyncio
import logging
import pandas as pd
from typing import Dict, Optional, Any
import requests

from .schemas.address import AddressGetSchema, EmployeeAddressUpdateSchema


class Address:
    """Address management class for AFAS integration"""

    def __init__(self, afas_connector: Any) -> None:
        """
        Initialize Address class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_address"
        self.address_fields_mappings = {
            'country': 'CoId',
            'street': 'Ad',
            'house_number': 'HmNr',
            'postal_code': 'ZpCd',
            'street_number_add': 'HmAd',
            'city': 'Rs'
        }

    def get(self, filter_fields: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Get address information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing address information

        Raises:
            Exception: If get address operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=AddressGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get address failed: {str(e)}") from e

    def __build_employee_address_update_body(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare request body for address update.
        Validates input data and returns formatted request body.

        Args:
            data: Dictionary containing address data
        Returns:
            dict: Formatted request body for AFAS API

        Raises:
            Exception: If data validation fails
        """
        try:
            base_address_fields = {
                'CoId': self.afas.iso2_mapping.get(data.get('country')),
                'StAd': data.get('street'),
                'Ad': data.get('street'),
                'HmNr': data.get('house_number'),
                'ZpCd': data.get('postal_code'),
                'BeginDate': data.get('address_active_effective_date'),
                'Rs': data.get('city')
            }
            kn_basic_address = base_address_fields.copy()
            kn_basic_address.update({'PbAd': False})
            kn_basic_address_pad = base_address_fields.copy()
            kn_basic_address_pad.update({'PbAd': True})

            # Construct request body
            request_body = {
                "AfasEmployee": {
                    "Element": {
                        "@EmId": data['employee_id'],
                        "Objects": [
                            {
                                'KnPerson': {
                                    'Element': {
                                        'Fields': {
                                            'MatchPer': data.get('match_person'),# 0 if you wanna match it with person
                                            'BcCo': data.get('person_id')
                                        },
                                        'Objects': [
                                            {
                                                'KnBasicAddressAdr': {
                                                    'Element': {
                                                        'Fields': kn_basic_address
                                                    }
                                                },
                                            },
                                            {
                                                'KnBasicAddressPad': {
                                                    'Element': {
                                                        'Fields': kn_basic_address_pad
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }

            }
            return request_body
        except Exception as e:
            raise Exception(f"Build request body failed: {str(e)}") from e

    def update_employee_address(self, data: Dict[str, Any]) -> Optional[requests.Response]:
        """
        Create new address for employee in AFAS

        Args:
            data: Dictionary containing address data

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If address data validation fails
        """
        try:
            try:
                validated_data = EmployeeAddressUpdateSchema(**data).model_dump()
                validated_data = self.afas.convert_timestamp_columns(validated_data)
            except Exception as e:
                raise Exception(f"Address data validation failed: {str(e)}") from e

            req_body = self.__build_employee_address_update_body(data=validated_data)
            response = self.afas.session.put(
                url=self.afas.employee_url,
                json=req_body, timeout=self.afas.timeout
            )
            return response
        except Exception as e:
            raise Exception(f"Failed to update employee address: {str(e)}") from e
