import asyncio
import pandas as pd
from typing import Optional
import requests

from .schemas.cost import CostCarrierGetSchema, CostCarrierCreateSchema, CostCarrierUpdateSchema


class CostCarrier:
    """Cost carrier management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize CostCarrier class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_cost_carrier"
        self.update_url = f"{self.afas.base_url}/HrCostCarrier"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get cost carrier information from AFAS.

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing cost carrier information

        Raises:
            Exception: If get cost carrier operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=CostCarrierGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get cost carrier failed: {str(e)}") from e

    def __build_req_body(self, data: dict) -> dict:
        try:
            body = {
                "HrCostCarrier": {
                    "Element": {
                        "@CmId": data['employer_id'],
                        "@CcId": data['cost_carrier_id'],
                        "Fields": {
                            "CcDs": data['cost_carrier_description'],
                            "Bl": data['blocked']
                        }
                    }
                }
            }
            return body
        except Exception as e:
            raise Exception("Build request body failed: " + str(e)) from e

    def create(self, data: dict) -> Optional[requests.Response]:
        """
        Create a new cost carrier in AFAS

        Args:
            data: Dictionary containing cost carrier data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = CostCarrierCreateSchema(**data).model_dump()
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            body = self.__build_req_body(data=valid_data)
            return self.afas.session.post(
                url=f"{self.afas.base_url}/KnCostCarrier",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Cost carrier creation failed: {str(e)}")

    def update(self, data: dict) -> Optional[requests.Response]:
        """
        Update cost carrier in AFAS

        Args:
            data: Dictionary containing cost carrier data

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = CostCarrierUpdateSchema(**data).model_dump()
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            body = self.__build_req_body(data=valid_data)
            return self.afas.session.put(
                url=f"{self.afas.base_url}/KnCostCarrier",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Cost carrier update failed: {str(e)}")

    def delete(self, data: dict) -> requests.Response:
        """
        Delete a cost carrier from AFAS

        Args:
            data (dict): Cost carrier data to be deleted

        Returns:
            Response from the AFAS API
        """
        try:
            return self.afas.session.delete(
                url=f"{self.update_url}/HrCostCarrier/@CmId,@CcId/{data['employer_id']},{data['cost_carrier_id']}", timeout=self.afas.timeout)
        except Exception as e:
            raise Exception(f"Cost carrier deletion failed: {str(e)}")
