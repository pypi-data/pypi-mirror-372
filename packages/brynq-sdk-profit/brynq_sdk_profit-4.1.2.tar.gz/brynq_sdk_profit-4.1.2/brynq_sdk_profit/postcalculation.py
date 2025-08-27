import asyncio
import pandas as pd
from typing import Optional
import requests

from .schemas.calculations import PostCalculationCreateSchema, PostCalculationUpdateSchema, PostCalculationGetSchema


class PostCalculation:
    """Post Calculation management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize PostCalculation class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_realization"
        self.field_mappings = {
            'realization': {
                'id': "Id",
                'external_key': "XpRe",
                'quantity': "Qu",
                'employee_id': "EmId",
                'type_of_hours': "StId",
                'costcenter_employee': "CrId",
                'approved': "Ap",
                'description': "Ds",
                'project_id': "PrId",
                'project_phase': "PrSt",
                'date': "DaTi",
                'item_type': "VaIt",
                'item_code': "ItCd"
            },
            'specification': {
                'specification_axis_code_1': "V1Cd",
                'specification_axis_code_2': "V2Cd",
                'specification_axis_code_3': "V3Cd",
                'specification_axis_code_4': "V4Cd",
                'specification_axis_code_5': "V5Cd"
            }
        }

        self.required_fields = ['employee_id', 'date', 'item_type', 'item_code']
        self.allowed_fields = ['external_key', 'quantity', 'type_of_hours',
                               'costcenter_employee', 'approved', 'description',
                               'project_id', 'project_phase'] + \
                              ['specification_axis_code_' + str(i) for i in range(1, 6)]

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get post calculation information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing post calculation information

        Raises:
            Exception: If get post calculation operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=PostCalculationGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get post calculation failed: {str(e)}") from e

    def __build_request_body(self, data: dict, overload_fields: dict = None) -> Optional[dict]:
        """
        Build request body for post calculation update/create.

        Args:
            data: Dictionary containing post calculation data
            overload_fields: Optional field overrides

        Returns:
            dict: Formatted request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
            base_body = {
                "PtRealization": {
                    "Element": {
                        "Fields": {}
                    }
                }
            }

            # Add realization fields
            realization_fields = {}
            for field, afas_field in self.field_mappings['realization'].items():
                if field in data:
                    value = data[field]
                    if not pd.isna(value) and value != '' and value:
                        realization_fields[afas_field] = value

            base_body['PtRealization']['Element']['Fields'].update(realization_fields)

            # Add specification fields if present
            specification_fields = {}
            for field, afas_field in self.field_mappings['specification'].items():
                if field in data:
                    value = data[field]
                    if not pd.isna(value) and value != '' and value:
                        specification_fields[afas_field] = value

            if specification_fields:
                base_body['PtRealization']['Element']['Fields'].update(specification_fields)

            # Add overload fields if provided
            if overload_fields:
                base_body['PtRealization']['Element']['Fields'].update(overload_fields)

            return base_body

        except Exception as e:
            raise Exception(f"Build request body failed: {str(e)}")

    def create(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Create post calculation entry in AFAS

        Args:
            data: Dictionary containing post calculation data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = PostCalculationCreateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            body = self.__build_request_body(data=valid_data, overload_fields=overload_fields)
            return self.afas.session.post(
                url=f"{self.afas.base_url}/PtRealization",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Post calculation creation failed: {str(e)}")

    def update(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Update post calculation entry in AFAS

        Args:
            data: Dictionary containing post calculation data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = PostCalculationUpdateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            body = self.__build_request_body(data=valid_data, overload_fields=overload_fields)
            return self.afas.session.put(
                url=f"{self.afas.base_url}/PtRealization",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Post calculation update failed: {str(e)}")

    def delete(self, post_calculation_id: str, date: str) -> requests.Response:  # NOT WORKING ANYMORE ???
        """
        Delete post calculation entry in AFAS

        Args:
            post_calculation_id: ID of the post calculation entry to delete
            date: Date of the post calculation entry (YYYY-MM-DD)

        Returns:
            requests.Response: Response from AFAS API
        """

        try:
            return self.afas.session.delete(
                url=f"{self.afas.base_url}/PtRealization/PtRealization/Id,DaTi/{post_calculation_id},{date}", timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Post calculation delete failed: {str(e)}")
