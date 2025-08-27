import asyncio
import pandas as pd
import requests

from .schemas.wage import WageComponentGetSchema, WageComponentCreateSchema, WageComponentUpdateSchema


class WageComponents:
    """Bank account management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize WageComponent class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_wage_components"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get wage components information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing wage components information

        Raises:
            Exception: If get wage components operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=WageComponentGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get wage components failed: {str(e)}") from e

    def delete(self, data: dict) -> requests.Response:
        """
        Delete wage component in AFAS

        Args:
            data: Dictionary containing wage component data

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If deletion fails
        """
        try:
            url = f'{self.afas.base_url}/HrVarValue/HrVarValue/@VaId,EmId,DaBe/{data["parameter"]},{data["employee_id"]},{pd.to_datetime(data["start_date"]).strftime("%Y-%m-%d")}'
            return self.afas.session.delete(url=url, timeout=self.afas.timeout)
        except Exception as e:
            raise ValueError(f"Wage component deletion failed: {str(e)}")

    def __build_request_body(self, data: dict, overload_fields: dict = None) -> dict:
        """
        Creates request body for wage component

        Args:
            data: Dictionary containing wage component data
            overload_fields: Optional custom fields

        Returns:
            dict: Request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
            base_body = {
                    "HrVarValue": {
                        "Element": {
                            "Fields": {
                                "VaId": data['parameter'],
                                 "Va": data['value'],
                                "EmId": data['employee_id'],
                                "DaBe": data['start_date'],
                            "ReAu": data['id']
                        }
                    }
                }
            }

            # Optional fields mapping
            optional_fields_mapping = {
                'contract_no': 'EnSe',
                'end_date': 'DaEn',
                'apply_type': 'DiTp'
            }

            # Add optional fields if they exist and not empty
            optional_fields = {
                optional_fields_mapping[key]: value
                for key, value in data.items()
                if key in optional_fields_mapping and pd.notna(value) and value != ''
            }

            if optional_fields:
                base_body['HrVarValue']['Element']['Fields'].update(optional_fields)

            # Add overload fields if they exist and not empty
                if overload_fields:
                    non_empty_overloads = {
                        k: v for k, v in overload_fields.items()
                        if v is not None and v != '' and pd.notna(v)
                    }
                    if non_empty_overloads:
                        base_body['HrVarValue']['Element']['Fields'].update(non_empty_overloads)

                return base_body
        except Exception as e:
            raise Exception(f"Build request body failed: {str(e)}")

    def create(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        Create or update wage component in AFAS

        Args:
            data: Dictionary containing wage component data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate data
            try:
                valid_data = WageComponentCreateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            body = self.__build_request_body(data=valid_data, overload_fields=overload_fields)
            return self.afas.session.post(
                url=f"{self.afas.base_url}/HrVarValue",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise ValueError(f"Wage component operation failed: {str(e)}")

    def update(self, data: dict, overload_fields: dict = None) -> requests.Response:  # This also performs create
        """
        Update wage component in AFAS

        Args:
            data: Dictionary containing wage component data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate data
            try:
                valid_data = WageComponentUpdateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")
            # Create request body
            body = self.__build_request_body(data=valid_data, overload_fields=overload_fields)

            return self.afas.session.put(
                url=f"{self.afas.base_url}/HrVarValue",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise ValueError(f"Wage component update failed: {str(e)}")
