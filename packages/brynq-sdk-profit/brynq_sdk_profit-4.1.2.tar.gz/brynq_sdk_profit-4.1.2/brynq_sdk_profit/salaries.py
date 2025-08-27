import asyncio
import pandas as pd
from typing import Optional
import requests

from .schemas.salary import SalaryGetSchema, SalaryUpdateSchema, SalaryCreateSchema


class Salaries:
    """Salaries management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize Salaries class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.base_url = f"{self.afas.base_url}/brynq_sdk_salaries"
        self.salary_types_mapping = {
            "Hourly wage": "U",
            "Fixed salary": "V",
            "Scale salary": "S",
            "Scale hourly wage": "Su"
        }

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get salary information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing salary information

        Raises:
            Exception: If get salary operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.base_url, schema=SalaryGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get salary failed: {str(e)}") from e

    def __build_update_body(self, data: dict, overload_fields: dict = None) -> dict:
        """
        Creates request body for salary update

        Args:
            data: Dictionary containing salary update data
            overload_fields: Optional custom fields

        Returns:
            dict: Request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
            # Field mapping
            field_mapping = {
                'step': 'SaSt',
                'final_step': 'SaS2',
                'salary_year_amount': 'SaYe',
                'period_table': 'PtId',
                'salary_scale': 'VaSc',
                'salary_scale_type': 'TaId',
                'function_scale': 'FuSc',
                'function_scale_type': 'FuTa',
                'net_salary': 'NtSa',
                'apply_timetable': 'TtPy',
                'employment_number': 'DvSn',
                'allowance': 'EmSc',
                'rsp': 'Rsp'
            }

        # Base body with required fields
            base_body = {
            "AfasEmployee": {
                    "Element": {
                        "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasSalary": {
                            "Element": {
                                "@DaBe": data['start_date_salary'],
                                "Fields": {
                                    "SaPe": self.salary_types_mapping.get(data.get("salary_type"), "U"),
                                    "EmSa": data.get("salary_amount")
                                }
                            }
                        }
                    }
                    }
                }
            }

        # Create fields to update
            fields_to_update = {}

            # Handle optional fields
            for key, map_key in field_mapping.items():
                if key in data and pd.notna(data[key]) and data[key] != '':
                    fields_to_update[map_key] = data[key]

            # Special handling for period_table (default: 5)
            fields_to_update['PtId'] = data.get("period_table", "5")

            # Add overload fields if they exist and not empty
            if overload_fields:
                non_empty_overloads = {
                    k: v for k, v in overload_fields.items()
                    if v is not None and v != '' and pd.notna(v)
                }
                if non_empty_overloads:
                    fields_to_update.update(non_empty_overloads)

            # Update base body with all fields
            if fields_to_update:
                base_body['AfasEmployee']['Element']['Objects']['AfasSalary']['Element']['Fields'].update(fields_to_update)

                return base_body
        except Exception as e:
            raise Exception(f"Build request body failed: {str(e)}")

    def update(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:  # Manages both create and update.
        """
        Update salary information in AFAS

        Args:
            data: Dictionary containing salary update data
            overload_fields: Optional custom fields
            method: HTTP method (PUT or POST)

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate data
            try:
                valid_data = SalaryUpdateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

        # Create request body
            body = self.__build_update_body(data=valid_data, overload_fields=overload_fields)

            # Make API request
            return self.afas.session.put(
                url=f"{self.afas.base_url}/KnEmployee/AfasSalary",
                json=body,
                timeout=self.afas.timeout
            )

        except Exception as e:
           raise Exception(f"Update Salary failed: {str(e)}")

    def create(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Create salary information in AFAS

        Args:
            data: Dictionary containing salary creation data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate data
            try:
                valid_data = SalaryCreateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            # Create request body
            body = self.__build_update_body(data=valid_data, overload_fields=overload_fields)

            # Make API request
            return self.afas.session.post(
                url=f"{self.afas.base_url}/KnEmployee/AfasSalary",
                json=body,
                timeout=self.afas.timeout
            )

        except Exception as e:
            raise Exception(f"Create Salary failed: {str(e)}")