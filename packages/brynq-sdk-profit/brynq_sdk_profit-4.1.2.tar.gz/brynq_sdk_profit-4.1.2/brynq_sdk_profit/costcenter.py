import asyncio
import pandas as pd
from typing import Optional
import requests

from .schemas.cost import CostCenterSchema, CostCenterGetSchema


class CostCenter:
    """Cost centre management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize CostCentre class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_cost_center"
        self.update_url = f"{self.afas.base_url}/HrCostCentre"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get cost center information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing cost center information

        Raises:
            Exception: If get cost center operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=CostCenterGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get cost center failed: {str(e)}") from e

    def __build_req_body(self, data: dict, overload_fields: dict = None) -> dict:
        try:
            body = {
                "HrCostCentre": {
                    "Element": {
                        "@CmId": data['employer_id'],
                        "@CrId": data['cost_center_id'],
                        "Fields": {
                            "CrDs": data['cost_center_description'],
                            "Bl": data['blocked'],
                            "CrTy": data['cost_center_type'],
                        }
                    }
                }
            }

            # Add any custom fields from overload_fields
            if overload_fields:
                body["HrCostCentre"]["Element"]["Fields"].update(overload_fields)

            return body
        except Exception as e:
            raise Exception("Build request body failed: " + str(e)) from e

    def update(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Create or update cost centre in AFAS

        Args:
            data: Dictionary containing cost centre data
            overload_fields: Optional dictionary containing custom fields to be added

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails or invalid method provided
        """
        try:
            try:
                valid_data = CostCenterSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Cost centre data validation failed: {str(e)}")

            body = self.__build_req_body(data=valid_data, overload_fields=overload_fields)

            response = self.afas.session.put(
                url=self.update_url,
                json=body,
                timeout=self.afas.timeout
            )
            return response

        except Exception as e:
            raise Exception("Update cost centre failed: " + str(e)) from e

    def create(self, data: dict, overload_fields: dict = None):
        """
        Create cost centre in AFAS

        Args:
            data: Dictionary containing cost centre data
            overload_fields: Optional dictionary containing custom fields to be added

        Raises:
            ValueError: If validation fails
        """
        try:
            try:
                valid_data = CostCenterSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")
            body = self.__build_req_body(data=valid_data, overload_fields=overload_fields)

            return self.afas.session.post(
                url=self.update_url,
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception("Create cost centre failed: " + str(e)) from e

    def delete(self, data) -> requests.Response:
        """
        Delete cost centre from AFAS

        Args:
            data: contains cost_center_id and employer_id
        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            return self.afas.session.delete(
                url=f"{self.update_url}/HrCostCentre/CmId,CrId/{data['employer_id']},{data['cost_center_id']}", timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception("Delete cost center failed: " + str(e)) from e
