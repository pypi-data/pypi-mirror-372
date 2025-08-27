import asyncio
import pandas as pd
from typing import Optional
import requests

from .schemas.organisation import OrganisationUpdateSchema, OrganisationGetSchema, OrganisationCreateSchema

class Organisation:
    """Organisation management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize Organisation class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_organization"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get organisation information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing organisation information

        Raises:
            Exception: If get organisation operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=OrganisationGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get organisation failed: {str(e)}") from e

    def __build_create_body(self, data: dict, custom_fields: dict = None) -> dict:
        """
        Creates the request body for organization operations

        Args:
            data: Dictionary containing organization data
            custom_fields: Dictionary of custom fields to be included

        Returns:
            dict: Formatted request body for AFAS API

        Raises:
            Exception: If building request body fails
        """
        try:
            base_body = {
                "KnOrganisation": {
                    "Element": {
                        "Fields": {
                            "MatchOga": data.get("match_organisation_on", "0"),
                            "BcId": data.get("organisation_id", 1),
                            "BcCo": data['organisation_id'],
                            "Nm": data['name'],
                            "Bl": data['blocked']
                        },
                        "Objects": {}
                    }
                }
            }

            # Handle address related fields
            address_fields = {
                'mailbox_address': 'PbAd',
                'country': 'CoId',
                'street': 'Ad',
                'housenumber': 'HmNr',
                'housenumber_add': 'HmAd',
                'zipcode': 'ZpCd',
                'residence': 'Rs',
                'search_living_place_by_zipcode': 'ResZip'
            }

            address_updates = {v: data[k] for k, v in address_fields.items() if k in data}

            if address_updates:
                address_body = {
                    "KnBasicAddressAdr": {
                        "Element": {
                            "Fields": address_updates
                        }
                    }
                }
                base_body['KnOrganisation']['Element']['Objects'].update(address_body)

            # Handle other fields
            other_fields = {
                'search_name': 'SeNm',
                'kvk_number': 'CcNr',
                'phone_number_work': 'TeNr',
                'email_work': 'EmAd',
                'vat_number': 'FiNr',
                'status': 'StId'
            }

            field_updates = {v: data[k] for k, v in other_fields.items() if k in data}
            field_updates.update(custom_fields) if custom_fields is not None else ''
            base_body['KnOrganisation']['Element']['Fields'].update(field_updates)

            return base_body
        except Exception as e:
            raise Exception(f"Build create body failed: {str(e)}")

    def create(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Create new organization in AFAS

        Args:
            data: Dictionary containing organization data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = OrganisationCreateSchema(**data).model_dump()
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            body = self.__build_create_body(data=valid_data, custom_fields=overload_fields)
            return self.afas.session.post(
                url=f"{self.afas.base_url}/KnOrganisation",
                json=body,
            )
        except Exception as e:
            raise Exception(f"Organization creation failed: {str(e)}")

    def update(self, data: dict, custom_fields: dict = None) -> Optional[requests.Response]:
        """
        Update organization in AFAS

        Args:
            data: Dictionary containing organization data
            custom_fields: Dictionary of custom fields to be included

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails or invalid method provided
        """
        try:
            try:
                valid_data = OrganisationUpdateSchema(**data).model_dump()
            except Exception as e:
                raise Exception(f"Organization data validation failed: {str(e)}")

            url = f"{self.afas.base_url}/KnOrganisation"
            body = self.__build_create_body(data=valid_data, custom_fields=custom_fields)

            response = self.afas.session.put(
                url=url,
                json=body
            )

            return response
        except Exception as e:
            raise Exception(f"Organization update failed: {str(e)}")

    def delete(self, data: dict) -> requests.Response:
        """
        Delete organization from AFAS

        Args:
            data: Dictionary containing organization data. Must include:
                - organisation_id: ID of the organization
                - name: Name of the organization
                - blocked: Blocked status

        Returns:
            requests.Response: Response from AFAS API
        """
        url = f"{self.afas.base_url}/KnOrganisation/KnOrganisation/MatchOga,BdId,BcCo,Nm,Bl/0,1,{data['organisation_id']},{data['name']},{data['blocked']}"

        return self.afas.session.delete(url=url)
