import requests
from typing import Optional

from .schemas.organisation import OrganisationalUnitUpdateSchema, OrganisationalUnitCreateSchema

class OrganisationalUnit:
    """Organisation Unit management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize Organisation class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector

    def __build_request_body(self,data: dict, overload_fields: Optional[dict] = None) -> dict:
        """
        Build request body for organisational unit operations.
        Validates input data and returns formatted request body.

        Args:
            data: Dictionary containing organisational unit data
            overload_fields: Optional dictionary containing additional custom fields

        Returns:
            dict: Formatted request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
            # Base required fields
            base_fields = {
                "Ds": data['organisational_unit_description'],
                "OTId": data['organisational_unit_type_id'],
                "StUn": data['staff'],
                "Empl": data['contains_employees'],
                "RpOu": data['reports_to_unit_above']
            }

            # Optional allowed fields
            optional_field_mappings = {
                'reporting_unit': 'ReOu',
                'manager': 'MaId',
                'cockpit_1': 'Cpt1',
                'cockpit_2': 'Cpt2',
                'cockpit_3': 'Cpt3',
                'cockpit_4': 'Cpt4',
                'cockpit_5': 'Cpt5'
            }

            # Add optional fields if present in data
            fields_to_update = {
                optional_field_mappings[key]: data[key]
                for key in optional_field_mappings
                if key in data
            }

            # Merge all fields
            all_fields = {**base_fields, **fields_to_update}

            # Add any custom overload fields
            if overload_fields:
                all_fields.update(overload_fields)

            # Construct the complete request body
            request_body = {
                "KnOrgunit": {
                    "Element": {
                        "@OuId": data['organisational_unit_id'],
                        "Fields": all_fields
                    }
                }
            }

            return request_body
        except Exception as e:
            raise Exception(f"Build request body failed: {str(e)}")

    def create(self, data: dict, overload_fields: Optional[dict] = None) -> Optional[requests.Response]:
        """
        Create new organisational unit in AFAS.

        Args:
            data: Dictionary containing organisational unit data
            overload_fields: Optional dictionary containing additional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = OrganisationalUnitCreateSchema(**data).model_dump()
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            req_body = self.__build_request_body(data=valid_data, overload_fields=overload_fields)
            return self.afas.session.post(
                url=f"{self.afas.base_url}/KnOrgUnit",
                json=req_body
            )
        except Exception as e:
            raise Exception(f"Organisational unit creation failed: {str(e)}")

    def update(self, data: dict, overload_fields: Optional[dict] = None) -> Optional[requests.Response]:
        """
        Update existing organisational unit in AFAS.

        Args:
            data: Dictionary containing organisational unit data
            overload_fields: Optional dictionary containing additional custom fields

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            try:
                valid_data = OrganisationalUnitUpdateSchema(**data).model_dump()
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            req_body = self.__build_request_body(data=valid_data, overload_fields=overload_fields)
            return self.afas.session.put(
                url=f"{self.afas.base_url}/KnOrgUnit",
                json=req_body
            )
        except Exception as e:
            raise Exception(f"Organisational unit update failed: {str(e)}")