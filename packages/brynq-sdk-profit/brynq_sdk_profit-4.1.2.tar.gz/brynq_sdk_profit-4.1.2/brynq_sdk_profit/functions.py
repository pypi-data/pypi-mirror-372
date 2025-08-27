import asyncio
import requests
import pandas as pd
from typing import Optional

from .schemas.function import FunctionGetSchema, FunctionCreateSchema


class EmployeeFunction:
    """Employee function management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize EmployeeFunction class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_functions"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get functions information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing functions information

        Raises:
            Exception: If get functions operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=FunctionGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get functions failed: {str(e)}") from e

    def __build_req_body(self, data: dict) -> dict:
        try:
            # Function fields mapping
            function_mapping = {
                'organizational_unit': 'DpId',
                'function_id': 'FuId',
                'costcenter_id': 'CrId',
                'costcarrier_id': 'CcId'
            }

            # Base structure
            base_body = {
                "AfasEmployee": {
                    "Element": {
                        "@EmId": data['employee_id'],
                        "Objects": {
                            "AfasOrgunitFunction": {
                                "Element": {
                                    "@DaBe": data['startdate'],  # Function start date
                                    "Fields": {}
                                }
                            }
                        }
                    }
                }
            }

            # Add function fields
            function_fields = {
                function_mapping[key]: value
                for key, value in data.items()
                if key in function_mapping and pd.notna(value)
            }

            base_body['AfasEmployee']['Element']['Objects']['AfasOrgunitFunction']['Element']['Fields'].update(function_fields)
            return base_body
        except Exception as e:
            raise Exception("Build request body failed: " + str(e)) from e

    def create(self, data: dict) -> Optional[requests.Response]:
        """
        Update function information for an employee in AFAS

        Args:
            data: Dictionary containing function data

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            try:
                valid_data = FunctionCreateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception("Data validation failed: " + str(e))

            body = self.__build_req_body(valid_data)
            return self.afas.session.post(
                url=f"{self.afas.base_url}/KnEmployee/AfasOrgunitFunction",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise ValueError("Create function failed: " + str(e))
