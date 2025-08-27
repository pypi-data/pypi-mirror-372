import asyncio
import pandas as pd
import requests

from .schemas.wage import WageMutationGetSchema, WageMutationCreateSchema, WageMutationUpdateSchema

class WageMutations:
    """Bank account management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize BankAccount class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_wage_mutations"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get wage mutations data

        Args:
            filter_fields: Optional filters to apply

        Returns:
            pd.DataFrame: Wage mutations data
            
        Raises:
            Exception: If get wage mutations operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=WageMutationGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get wage mutations failed: {str(e)}") from e

    def __build_create_body(self, data: dict, overload_fields: dict = None) -> dict:
        """
        Creates request body for wage mutation

        Args:
            data: Dictionary containing wage mutation data
            overload_fields: Optional custom fields

        Returns:
            dict: Request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
            base_body = {
                "HrCompMut": {
                    "Element": {
                        "@Year": data['year'],
                        "@PeId": data['month'],
                        "@EmId": data['employee_id'],
                        "@ErId": data['employer_nmbr'],
                        "@Sc02": data['wage_component_id'],
                        "Fields": {
                            "VaD1": data['value']
                        }
                    }
                }
            }

            # Element level attributes
            element_attrs = {}
            if 'period_table' in data:
                if pd.notna(data['period_table']) and data['period_table']!="":
                    element_attrs["@PtId"] = data['period_table']
                else:
                    element_attrs["@PtId"] = 5
            # Handle period_table (default: 5)

            # Add date if exists
            if 'date' in data and pd.notna(data['date']) and data['date'] != '':
                element_attrs["@DaTi"] = data['date']

            # Add element attributes
            base_body['HrCompMut']['Element'].update(element_attrs)

            # Add overload fields if they exist and not empty
            if overload_fields:
                non_empty_overloads = {
                    k: v for k, v in overload_fields.items()
                    if v is not None and v != '' and pd.notna(v)
                }
                if non_empty_overloads:
                    base_body['HrCompMut']['Element']['Fields'].update(non_empty_overloads)

            return base_body
        except Exception as e:
            raise Exception(f"Build create request body failed: {str(e)}")

    def create(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        Create new wage mutation in AFAS

        Args:
            data: Dictionary containing wage mutation data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate data
            try:
               valid_data = WageMutationCreateSchema(**data).model_dump()
               body = self.__build_create_body(valid_data, overload_fields)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            # Make API request
            return self.afas.session.post(
                url=f"{self.afas.base_url}/HrCompMut",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise ValueError(f"Wage mutation creation failed: {str(e)}")

    def __build_update_body(self, data: dict, overload_fields: dict = None) -> dict:
        """
        Creates request body for updating wage mutation

        Args:
            data: Dictionary containing wage mutation update data
            overload_fields: Optional custom fields

        Returns:
            dict: Request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
            base_body = {
                "HrCompMutGUID": {
                    "Element": {
                        "@GuLi": data['guid'],
                        "Fields": {
                            "VaD1": data['value'],
                            "Year": data['year'],
                            "PeId": data['month'],
                            "EmId": data['employee_id'],
                            "ErId": data['employer_nmbr'],
                            "Sc02": data['wage_component_id'],
                        }
                    }
                }
            }

            # Element level attributes
            element_attrs = {}

            # Handle period_table (default: 5)
            if 'period_table' in data and pd.notna(data['period_table']):
                element_attrs["PtId"] = data['period_table']
            else:
                element_attrs["PtId"] = "5"

            # Add date if exists
            if 'date' in data and pd.notna(data['date']) and data['date'] != '':
                element_attrs["DaTi"] = data['date']

            # Add element attributes if not empty
            if element_attrs:
                base_body['HrCompMutGUID']['Element'].update(element_attrs)

            # Add overload fields if they exist and not empty
            if overload_fields:
                non_empty_overloads = {
                    k: v for k, v in overload_fields.items()
                    if v is not None and v != '' and pd.notna(v)
                }
                if non_empty_overloads:
                    base_body['HrCompMutGUID']['Element']['Fields'].update(non_empty_overloads)

            return base_body
        except Exception as e:
            raise Exception(f"Build update request body failed: {str(e)}")

    def update(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        Update wage mutation in AFAS using GUID

        Args:
            data: Dictionary containing wage mutation update data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            try:
                valid_data = WageMutationUpdateSchema(**data).model_dump()
                body = self.__build_update_body(valid_data, overload_fields)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")
        # Make API request
            return self.afas.session.put(
                url=f"{self.afas.base_url}/HrCompMutGUID",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise ValueError(f"Wage mutation update failed: {str(e)}")

    def delete(self, data: dict) -> requests.Response:
        """
        Delete wage mutation in AFAS

        Args:
            data: Dictionary containing wage mutation data (must include 'guid')

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If deletion fails
        """
        try:
            return self.afas.session.delete(url=f"{self.afas.base_url}/HrCompMutGUID/HrCompMutGUID/@GuLi/{data['guid']}", timeout=self.afas.timeout)
        except Exception as e:
            raise ValueError(f"Wage mutation deletion failed: {str(e)}")